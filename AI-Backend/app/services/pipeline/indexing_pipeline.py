import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import UploadFile
from pydantic import BaseModel
from app.services.documents.manager import DocumentManager
from app.services.chunking.manager import ChunkManager
from app.services.embeddings.manager import EmbeddingManager
from app.domain.schemas.embedding import EmbeddingRequest
from app.services.vectorstore.manager import VectorStoreManager
from app.domain.schemas.vectorstore import VectorRecord, VectorMetadata
from app.utils.vectorstore_utils import generate_chunk_id
from app.utils.metadata_utils import normalize_metadata
from app.core.exceptions import DocumentProcessingException
from app.core.logger import logger

class PipelineExecutionError(Exception):
    def __init__(self, message: str, stage: str, status_code: int = 500):
        super().__init__(message)
        self.stage = stage
        self.status_code = status_code

class IndexingStatus(BaseModel):
    document_id: str
    status: str
    total_pages: int
    total_chunks: int
    message: str

class IndexingPipeline:
    """
    Orchestrates the entire PDF Indexing Workflow:
    Upload -> Validate -> Extract Text -> Clean Text -> Chunk -> Embed -> Store.
    """
    
    def __init__(self):
        self.embedding_manager = EmbeddingManager()
        
    async def execute(
        self,
        file: UploadFile,
        document_id: Optional[str] = None,
        faculty_name: Optional[str] = None,
        department: Optional[str] = None,
        subject: Optional[str] = None,
        semester: Optional[int] = None,
        section: Optional[str] = None
    ) -> IndexingStatus:
        
        logger.info(f"Starting Indexing Pipeline for {file.filename}")
        
        # 1. Generate unique Document ID if not provided, or check if provided one exists
        doc_id = document_id if document_id else str(uuid.uuid4())
        
        if document_id:
            # Check for duplicate
            try:
                # We do a dummy search to see if any chunk with this document_id exists
                # Using an empty embedding of the same size or just [0.0] depending on DB. 
                # Some databases might fail if dims don't match. 
                # Let's use a safe fallback: if the delete method deletes by ID, we can't easily check without modifying interfaces.
                # Actually, let's just use the embedding manager to create a dummy embedding, then search.
                dummy_emb = self.embedding_manager.create_embeddings(EmbeddingRequest(texts=["dummy"])).embeddings[0]
                existing = VectorStoreManager.search(dummy_emb, top_k=1, metadata_filter={"document_id": document_id})
                if existing and existing.results:
                    raise PipelineExecutionError(f"Document with ID {document_id} already exists.", stage="validation", status_code=409)
            except PipelineExecutionError:
                raise
            except Exception as e:
                logger.warning(f"Failed to check duplicate document ID: {str(e)}")

        upload_time = datetime.now(timezone.utc).isoformat()
        
        # 2. Process Upload (Extracts text page by page, cleans it, and enhances metadata)
        try:
            pages = await DocumentManager.process_upload(file)
        except Exception as e:
            raise PipelineExecutionError(f"PDF extraction failed: {str(e)}", stage="text_extraction", status_code=422)
        
        total_chunks_processed = 0
        records_to_insert = []
        
        # 3. Process each page sequentially
        for page in pages:
            # 4. Chunk the text
            try:
                chunk_response = ChunkManager.process_single(page)
            except Exception as e:
                raise PipelineExecutionError(f"Chunking failed on page {page.metadata.page_number}: {str(e)}", stage="chunk_generation", status_code=500)
            
            # 5. Process each chunk
            for chunk in chunk_response.chunks:
                # Ignore duplicate/empty chunks dynamically
                if not chunk.text or not chunk.text.strip():
                    continue
                    
                chunk_id = generate_chunk_id(doc_id, total_chunks_processed)
                
                # 6. Generate Embeddings (Sentence Transformers)
                try:
                    embed_req = EmbeddingRequest(texts=chunk.text)
                    embed_res = self.embedding_manager.create_embeddings(embed_req)
                    vector = embed_res.embeddings[0]
                except Exception as e:
                    raise PipelineExecutionError(f"Embedding generation failed for chunk {chunk_id}: {str(e)}", stage="embedding_generation", status_code=500)
                
                # 7. Construct Metadata
                meta = VectorMetadata(
                    document_id=doc_id,
                    document_name=normalize_metadata(file.filename) or "unknown document",
                    faculty_name=normalize_metadata(faculty_name) or "unknown faculty",
                    department=normalize_metadata(department) or "unknown department",
                    subject=normalize_metadata(subject) or "unknown subject",
                    semester=semester or 0,
                    section=normalize_metadata(section) or "unknown section",
                    page_number=page.metadata.page_number or 1,
                    chunk_id=chunk_id,
                    chunk_index=total_chunks_processed,
                    embedding_model=embed_res.model_used,
                    created_at=upload_time,
                    upload_time=upload_time,
                    source_file_type=page.metadata.source_file_type or "Unknown"
                )
                
                # 8. Create standard record
                record = VectorRecord(
                    id=chunk_id,
                    embedding=vector,
                    metadata=meta,
                    document_text=chunk.text
                )
                
                records_to_insert.append(record)
                total_chunks_processed += 1
                
        # 9. Store in OpenSearch via Batch Insert
        if records_to_insert:
            try:
                VectorStoreManager.insert(records_to_insert)
            except Exception as e:
                raise PipelineExecutionError(f"Vector Database insertion failed: {str(e)}", stage="vectorstore_insertion", status_code=500)
            
        logger.info(f"Indexing completed successfully for '{file.filename}'. Total chunks: {total_chunks_processed}")
        
        return IndexingStatus(
            document_id=doc_id,
            status="success",
            total_pages=len(pages),
            total_chunks=total_chunks_processed,
            message="Document indexed successfully into Vector Store."
        )
