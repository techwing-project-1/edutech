from typing import List, Dict, Any

from opensearchpy.exceptions import RequestError, NotFoundError

from app.infrastructure.opensearch.client import opensearch_manager
from app.infrastructure.opensearch.logger import opensearch_logger
from app.infrastructure.opensearch.exceptions import IndexCreationError

class OpenSearchIndexManager:
    """
    Manages OpenSearch index operations.
    Responsible for creating, checking, and deleting indexes with strict production-ready mappings.
    """
    
    def __init__(self):
        self._manager = opensearch_manager

    def get_production_mapping(self, vector_dimension: int = 384) -> Dict[str, Any]:
        """
        Returns the standard mapping for RAG documents.
        Supports dense vectors for embeddings and scalar types for metadata filtering.
        """
        return {
            "settings": {
                "index": {
                    "knn": True,
                    "knn.algo_param.ef_search": 100
                }
            },
            "mappings": {
                "properties": {
                    # Core Vector Field
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": vector_dimension,
                        "method": {
                            "name": "hnsw",
                            "space_type": "l2",
                            "engine": "lucene",
                            "parameters": {
                                "ef_construction": 128,
                                "m": 24
                            }
                        }
                    },
                    
                    # Full-Text Search Field
                    "text": {
                        "type": "text"
                    },
                    
                    # Exact Match / Filter Metadata
                    "document_id": {
                        "type": "keyword"
                    },
                    "document_name": {
                        "type": "keyword"
                    },
                    "faculty_name": {
                        "type": "keyword"
                    },
                    "department": {
                        "type": "keyword"
                    },
                    "semester": {
                        "type": "integer"
                    },
                    "subject": {
                        "type": "keyword"
                    },
                    "section": {
                        "type": "keyword"
                    },
                    "page_number": {
                        "type": "integer"
                    },
                    "chunk_id": {
                        "type": "keyword"
                    },
                    "chunk_index": {
                        "type": "integer"
                    },
                    "upload_time": {
                        "type": "date"
                    },
                    "source_file_type": {
                        "type": "keyword"
                    },
                    "created_at": {
                        "type": "date"
                    }
                }
            }
        }

    def check_index_exists(self, index_name: str) -> bool:
        """Checks if an index currently exists in the cluster."""
        client = self._manager.get_client()
        try:
            exists = client.indices.exists(index=index_name)
            return exists
        except Exception as e:
            opensearch_logger.error(f"Failed to check if index '{index_name}' exists: {str(e)}")
            return False

    def create_index_if_missing(self, index_name: str, vector_dimension: int = 384) -> bool:
        """
        Creates an index with the production mapping if it does not already exist.
        Returns True if created, False if it already existed.
        Raises IndexCreationError if creation fails.
        """
        client = self._manager.get_client()
        
        if self.check_index_exists(index_name):
            opensearch_logger.info(f"OpenSearch index '{index_name}' already exists. Skipping creation.")
            return False
            
        mapping = self.get_production_mapping(vector_dimension=vector_dimension)
        
        try:
            opensearch_logger.info(f"Creating OpenSearch index '{index_name}'...")
            response = client.indices.create(index=index_name, body=mapping)
            
            if response.get("acknowledged"):
                opensearch_logger.info(f"Successfully created OpenSearch index '{index_name}'.")
                return True
            else:
                raise IndexCreationError(f"Index creation not acknowledged by cluster for '{index_name}'.")
                
        except RequestError as e:
            if e.error == 'resource_already_exists_exception':
                # Race condition handled
                opensearch_logger.info(f"Index '{index_name}' was created concurrently.")
                return False
            else:
                opensearch_logger.error(f"Request error creating index '{index_name}': {str(e)}")
                raise IndexCreationError(f"Failed to create index '{index_name}': {str(e)}")
        except Exception as e:
            opensearch_logger.error(f"Unexpected error creating index '{index_name}': {str(e)}")
            raise IndexCreationError(f"Failed to create index '{index_name}': {str(e)}")

    def delete_index(self, index_name: str) -> bool:
        """
        Deletes an index. 
        Will not throw an error if the index does not exist.
        """
        client = self._manager.get_client()
        try:
            opensearch_logger.warning(f"Attempting to delete OpenSearch index '{index_name}'...")
            response = client.indices.delete(index=index_name)
            if response.get("acknowledged"):
                opensearch_logger.info(f"Successfully deleted index '{index_name}'.")
                return True
            return False
        except NotFoundError:
            opensearch_logger.info(f"Index '{index_name}' did not exist. Deletion skipped.")
            return False
        except Exception as e:
            opensearch_logger.error(f"Failed to delete index '{index_name}': {str(e)}")
            return False

    def list_indexes(self) -> List[str]:
        """Lists all indexes in the cluster."""
        client = self._manager.get_client()
        try:
            indexes = client.indices.get_alias("*").keys()
            return list(indexes)
        except Exception as e:
            opensearch_logger.error(f"Failed to list indexes: {str(e)}")
            return []

# Singleton instance
opensearch_index_manager = OpenSearchIndexManager()
