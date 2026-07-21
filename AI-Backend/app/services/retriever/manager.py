import re
import string
from typing import Optional, List, Set, Tuple
from fastapi.concurrency import run_in_threadpool
from app.domain.schemas.retriever import RetrieverRequest, RetrieverResponse, RetrievedChunk
from app.services.retriever.validator import RetrieverValidator
from app.services.embeddings.manager import EmbeddingManager
from app.domain.schemas.embedding import EmbeddingRequest
from app.services.vectorstore.manager import VectorStoreManager
from app.core.logger import logger
from app.core.retriever_config import retriever_config
from app.utils.metadata_utils import normalize_metadata
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

# Load CrossEncoder (will be loaded once on module import or lazily. We'll do it lazily/singleton)
_cross_encoder = None

def get_cross_encoder():
    global _cross_encoder
    if _cross_encoder is None:
        logger.info("Loading CrossEncoder: cross-encoder/ms-marco-MiniLM-L-6-v2")
        _cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", max_length=512)
    return _cross_encoder

SYNONYM_MAP = {
    "ai": "artificial intelligence",
    "ml": "machine learning",
    "llm": "large language model",
    "nlp": "natural language processing",
    "dl": "deep learning",
    "projects": "projects experience capstone",
    "experience": "experience work history employment role",
    "skills": "skills technologies tools proficiencies",
    "education": "education university degree academic",
    "certifications": "certifications certificates courses"
}

def preprocess_query(query: str) -> str:
    """Preprocess query: lowercase, punctuation removal, space normalization, synonym expansion"""
    # Lowercase
    q = query.lower()
    # Remove unnecessary punctuation (keep alphanumeric and spaces)
    q = q.translate(str.maketrans('', '', string.punctuation))
    # Normalize spaces
    q = " ".join(q.split())
    
    # Synonym expansion
    tokens = q.split()
    expanded = []
    for t in tokens:
        expanded.append(t)
        if t in SYNONYM_MAP:
            expanded.append(SYNONYM_MAP[t])
    
    return " ".join(expanded)

class RetrieverManager:
    """
    Orchestrates the entire Retrieval flow:
    Question -> Embed -> Build Filters -> Vector Search -> BM25 -> RRF -> CrossEncoder -> Deduplicate -> Return.
    """
    
    def __init__(self):
        self.embedding_manager = EmbeddingManager()
        
    def _build_metadata_filter(self, request: RetrieverRequest) -> dict:
        """Constructs the metadata filter dictionary for OpenSearch queries."""
        filters = {}
        if request.document_id and request.document_id.strip():
            # If a specific document is selected, we bypass other filters to ensure
            # we retrieve exclusively from this document.
            filters["document_id"] = request.document_id.strip()
            return filters
            
        if request.department and request.department.strip():
            filters["department"] = normalize_metadata(request.department)
        if request.semester:
            filters["semester"] = request.semester
        if request.subject and request.subject.strip():
            filters["subject"] = normalize_metadata(request.subject)
        if request.section and request.section.strip():
            filters["section"] = normalize_metadata(request.section)
        if request.faculty_name and request.faculty_name.strip():
            filters["faculty_name"] = normalize_metadata(request.faculty_name)
        return filters

    def _determine_confidence(self, score: float) -> str:
        """Determine confidence level based on score."""
        if score >= 0.85:
            return "HIGH"
        elif score >= 0.70:
            return "MEDIUM"
        return "LOW"

    def _dynamic_threshold(self, query: str) -> float:
        """Phase 1: Dynamic Threshold based on query characteristics"""
        word_count = len(query.split())
        # For single-word keywords like "Projects", "Skills", use a lower threshold
        # so semantic variations aren't prematurely dropped, especially for large chunks.
        if word_count == 1:
            return 0.05
        elif word_count <= 3:
            return 0.10
        elif word_count <= 10:
            return 0.15
        return 0.20

    def _adaptive_top_k(self, query: str, base_top_k: int) -> int:
        return 15  # Phase 1: Retrieve 15 internally for CrossEncoder

    def _compute_rrf(self, semantic_ranks: dict, bm25_ranks: dict, k=60) -> dict:
        """Computes Reciprocal Rank Fusion."""
        rrf_scores = {}
        all_docs = set(semantic_ranks.keys()).union(set(bm25_ranks.keys()))
        for doc in all_docs:
            rrf_score = 0.0
            if doc in semantic_ranks:
                rrf_score += 1.0 / (k + semantic_ranks[doc])
            if doc in bm25_ranks:
                rrf_score += 1.0 / (k + bm25_ranks[doc])
            rrf_scores[doc] = rrf_score
        return rrf_scores

    async def search(self, request: RetrieverRequest) -> RetrieverResponse:
        import time
        start_time = time.time()
        logger.info(f"Retriever started for query: '{request.query}'")
        
        # 1. Preprocess Query
        processed_query = preprocess_query(request.query)
        logger.debug(f"Processed Query: '{processed_query}'")
        
        # 2. Validate
        RetrieverValidator.validate_request(request)
        
        # 3. Embed
        embed_req = EmbeddingRequest(texts=processed_query)
        embed_res = await run_in_threadpool(self.embedding_manager.create_embeddings, embed_req)
        query_vector = embed_res.embeddings[0]
        
        # 4. Base configs
        base_top_k = request.top_k
        adaptive_top_k = self._adaptive_top_k(processed_query, base_top_k) # Target 15 chunks
        
        base_threshold = request.similarity_threshold
        if base_threshold is None:
            base_threshold = self._dynamic_threshold(processed_query)
            
        original_filters = self._build_metadata_filter(request)
        
        # 5. Semantic Search & Candidate Selection (Cascading Fallback)
        search_top_k = 50
        vs_response = None
        applied_filters = original_filters.copy()
        
        # Fallback Strategy (Strict Order: Section -> Subject -> Semester -> Department)
        fallback_strategies = [original_filters.copy()]
        current_strategy = original_filters.copy()
        
        for key in ["section", "subject", "semester", "department"]:
            if key in current_strategy:
                current_strategy.pop(key)
                fallback_strategies.append(current_strategy.copy())
                
        if not fallback_strategies[-1]: 
            # Ensure empty filter is at the end if not already
            pass
        elif {} not in fallback_strategies:
            fallback_strategies.append({})

        candidate_chunks = []
        raw_similarities = {}
        
        for strategy_filters in fallback_strategies:
            vs_response = VectorStoreManager.search(
                query_embedding=query_vector,
                top_k=search_top_k,
                metadata_filter=strategy_filters,
                explain_mode=getattr(request, "explain_mode", False)
            )
            
            if not vs_response or not vs_response.results:
                logger.warning(f"Retrieval yielded 0 results for filters {strategy_filters}, cascading...")
                continue
                
            applied_filters = strategy_filters
            logger.info(f"Retrieval yielded {len(vs_response.results)} results using filters: {strategy_filters}")
            
            # Prepare Semantic Ranks & Data
            raw_similarities = {}
            for idx, r in enumerate(vs_response.results):
                sim = max(0.0, 1.0 - (r.score / 2.0))
                raw_similarities[r.id] = {"result": r, "semantic_sim": sim, "semantic_rank": idx + 1}

            # BM25 Keyword Search
            tokenized_corpus = [r.document_text.lower().split() for r in vs_response.results]
            bm25 = BM25Okapi(tokenized_corpus)
            tokenized_query = processed_query.split()
            bm25_scores = bm25.get_scores(tokenized_query)
            
            bm25_ranking = sorted([
                (vs_response.results[i].id, bm25_scores[i]) 
                for i in range(len(bm25_scores))
            ], key=lambda x: x[1], reverse=True)

            bm25_ranks = {doc_id: rank + 1 for rank, (doc_id, score) in enumerate(bm25_ranking)}
            semantic_ranks = {doc_id: data["semantic_rank"] for doc_id, data in raw_similarities.items()}

            # RRF Merging
            rrf_scores = self._compute_rrf(semantic_ranks, bm25_ranks)
            
            # Sort by RRF and get top 15
            top_hybrid_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:adaptive_top_k]
            
            candidate_chunks = []
            
            # Since this strategy matched AT LEAST ONE document in the database, 
            # this is our highest quality exact metadata match.
            # We MUST NOT cascade to looser filters, even if semantic similarity is low.
            # This prevents retrieving the wrong document just because its text matches BM25 better.
            for doc_id, rrf in top_hybrid_docs:
                data = raw_similarities[doc_id]
                candidate_chunks.append(data["result"])
                
            if candidate_chunks:
                logger.info(f"Metadata match achieved! Selected {len(candidate_chunks)} candidate chunks from filters {strategy_filters}. Breaking cascade.")
                # WE MUST NOT CASCADE. This metadata level matched.
                break

        if not candidate_chunks:
            logger.warning("Retrieval yielded 0 valid candidates even after all fallbacks.")

        # 9. CrossEncoder Reranking
        final_chunks = []
        if candidate_chunks:
            cross_encoder = get_cross_encoder()
            cross_inp = [[request.query, doc.document_text] for doc in candidate_chunks]
            ce_scores = cross_encoder.predict(cross_inp)
            
            scored_candidates = []
            for i, score in enumerate(ce_scores):
                # normalize cross encoder score (sigmoid approx for relative ranking)
                norm_score = round(float(1 / (1 + __import__('math').exp(-score))), 4)
                scored_candidates.append((candidate_chunks[i], norm_score))
                
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            
            # Find the best document
            best_doc_id = None
            if scored_candidates:
                best_doc_id = getattr(scored_candidates[0][0].metadata, "document_id", None)
                best_doc_name = getattr(scored_candidates[0][0].metadata, "document_name", "Unknown")
                logger.info(f"Final selected document based on best chunk score: {best_doc_name} ({best_doc_id})")
            
            # Deduplicate and extract Top-K FROM THE BEST DOCUMENT ONLY
            seen_texts: Set[str] = set()
            for doc, score in scored_candidates:
                doc_id = getattr(doc.metadata, "document_id", None)
                if best_doc_id and doc_id != best_doc_id:
                    logger.debug(f"Discarding chunk from {doc_id} as it is not the final selected document {best_doc_id}")
                    continue
                    
                if doc.document_text in seen_texts:
                    continue
                seen_texts.add(doc.document_text)
                
                chunk = RetrievedChunk(
                    chunk_id=doc.id,
                    text=doc.document_text,
                    score=score,
                    confidence=self._determine_confidence(score),
                    metadata=doc.metadata,
                    document_name=getattr(doc.metadata, "document_name", "Unknown"),
                    page=getattr(doc.metadata, "page_number", 0)
                )
                final_chunks.append(chunk)
                if len(final_chunks) == base_top_k:
                    break

        execution_time_ms = int((time.time() - start_time) * 1000)
        from app.monitoring.metrics import record_opensearch_metrics
        record_opensearch_metrics(execution_time_ms)
        
        logger.info(f"--- RETRIEVAL METRICS ---")
        logger.info(f"Query: {request.query}")
        logger.info(f"Processed Query: {processed_query}")
        logger.info(f"Base Top-K: {base_top_k} | Adaptive Top-K: {adaptive_top_k} | Candidates: {len(candidate_chunks)}")
        logger.info(f"Threshold: {base_threshold}")
        logger.info(f"Final Returned Chunks: {len(final_chunks)}")
        logger.info(f"Execution Time: {execution_time_ms} ms")
        logger.info(f"-------------------------")

        return RetrieverResponse(
            status="success",
            query=request.query,
            retrieval_time_ms=execution_time_ms,
            threshold_used=base_threshold,
            filters=applied_filters,
            retrieved_chunk_count=len(final_chunks),
            chunks=final_chunks
        )
