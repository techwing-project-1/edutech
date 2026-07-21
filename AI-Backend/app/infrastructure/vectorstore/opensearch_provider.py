import datetime
from datetime import timezone
from typing import List, Optional
from opensearchpy import helpers

from app.domain.interfaces.vector_store import VectorStoreInterface
from app.domain.schemas.vectorstore import VectorRecord, SearchResult, CollectionStats, VectorMetadata
from app.core.exceptions import VectorStoreException
from app.infrastructure.opensearch.client import opensearch_manager
from app.infrastructure.opensearch.index_manager import opensearch_index_manager
from app.infrastructure.opensearch.logger import opensearch_logger

class OpenSearchProvider(VectorStoreInterface):
    """
    Concrete implementation of the Vector Database for Amazon OpenSearch.
    """
    
    def __init__(self):
        self.client = opensearch_manager.get_client()

    def create_collection(self, collection_name: str) -> None:
        opensearch_index_manager.create_index_if_missing(collection_name)
        
    def insert(self, collection_name: str, records: List[VectorRecord]) -> None:
        self.create_collection(collection_name)
        actions = []
        for record in records:
            doc = {
                "embedding": record.embedding,
                "text": record.document_text,
                "created_at": datetime.datetime.now(timezone.utc).isoformat()
            }
            # Safely unpack metadata
            meta_dict = record.metadata.model_dump(exclude_none=True)
            doc.update(meta_dict)
            
            actions.append({
                "_op_type": "index",
                "_index": collection_name,
                "_id": record.id,
                "_source": doc
            })
            
        try:
            success, failed = helpers.bulk(self.client, actions, chunk_size=500)
            opensearch_logger.info(f"Successfully bulk indexed {success} records into {collection_name}.")
            if failed:
                opensearch_logger.warning(f"Failed to index {len(failed)} records.")
        except Exception as e:
            opensearch_logger.error(f"Failed to insert records into OpenSearch: {str(e)}")
            raise VectorStoreException(f"OpenSearch Insert Error: {str(e)}")
        
    def search(self, collection_name: str, query_embedding: List[float], top_k: int, metadata_filter: Optional[dict] = None, explain_mode: bool = False) -> List[SearchResult]:
        query = {
            "size": top_k,
            "query": {
                "bool": {
                    "must": [
                        {
                            "knn": {
                                "embedding": {
                                    "vector": query_embedding,
                                    "k": top_k
                                }
                            }
                        }
                    ],
                    "filter": []
                }
            }
        }
        
        if metadata_filter:
            for key, value in metadata_filter.items():
                if value is not None:
                    query["query"]["bool"]["filter"].append({"term": {key: value}})
                    
        if explain_mode:
            import json
            opensearch_logger.debug(f"[EXPLAIN MODE] OpenSearch DSL Query for '{collection_name}': {json.dumps(query, indent=2)}")
                    
        try:
            response = self.client.search(index=collection_name, body=query)
            hits = response.get("hits", {}).get("hits", [])
            
            search_results = []
            for hit in hits:
                source = hit.get("_source", {})
                score = hit.get("_score", 0.0)
                doc_id = hit.get("_id")
                
                # Extract text
                text = source.get("text", "")
                
                # Extract metadata
                meta_dict = {k: v for k, v in source.items() if k not in ["embedding", "text"]}
                metadata = VectorMetadata(**meta_dict)
                
                # OpenSearch l2 space_type returns _score as 1 / (1 + L2). We invert this to match ChromaDB's raw L2 distance.
                l2_distance = (1.0 / score) - 1.0 if score > 0 else 2.0
                
                search_results.append(SearchResult(
                    id=doc_id,
                    score=l2_distance,
                    document_text=text,
                    metadata=metadata
                ))
            return search_results
        except Exception as e:
            opensearch_logger.error(f"OpenSearch search failed: {str(e)}")
            raise VectorStoreException(f"OpenSearch Search Error: {str(e)}")
        
    def delete_by_document_id(self, collection_name: str, document_id: str) -> None:
        query = {
            "query": {
                "term": {
                    "document_id": document_id
                }
            }
        }
        try:
            self.client.delete_by_query(index=collection_name, body=query)
            opensearch_logger.info(f"Deleted all records for document_id: {document_id}")
        except Exception as e:
            opensearch_logger.error(f"Failed to delete document '{document_id}': {str(e)}")
            raise VectorStoreException(f"OpenSearch Delete Error: {str(e)}")
        
    def delete_collection(self, collection_name: str) -> None:
        opensearch_index_manager.delete_index(collection_name)
        
    def get_collection_stats(self, collection_name: str) -> CollectionStats:
        try:
            self.client.indices.refresh(index=collection_name)
            response = self.client.count(index=collection_name)
            count = response.get("count", 0)
            return CollectionStats(collection_name=collection_name, total_vectors=count)
        except Exception as e:
            raise VectorStoreException(f"OpenSearch Stats Error: {str(e)}")
