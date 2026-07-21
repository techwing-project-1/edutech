from app.domain.schemas.vectorstore import VectorMetadata

class MetadataManager:
    """
    Responsible for constructing rich metadata objects before Vector Database insertion.
    Ensures that filtering fields (e.g., semester, section, subject) are strictly typed.
    """
    
    @staticmethod
    def build_metadata(**kwargs) -> VectorMetadata:
        """
        Dynamically builds the metadata schema.
        Pydantic automatically validates required fields (document_id, chunk_id, chunk_index)
        while allowing flexible optional fields.
        """
        return VectorMetadata(**kwargs)
