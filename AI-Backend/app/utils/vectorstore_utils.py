def generate_chunk_id(document_id: str, chunk_index: int) -> str:
    """
    Reusable utility: Generates a deterministic unique ID for a vector record.
    This guarantees idempotency. Upserting the same chunk twice will correctly 
    overwrite the existing vector rather than duplicating it in ChromaDB.
    """
    return f"{document_id}_chunk_{chunk_index}"
