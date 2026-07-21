def merge_with_overlap(chunk1: str, chunk2: str, overlap_size: int) -> str:
    """
    Reusable utility for custom text splitters.
    Ensures that context is not lost between chunk boundaries.
    """
    if not chunk1: return chunk2
    if not chunk2: return chunk1
    
    # Simple conceptual overlap placeholder logic.
    # Production overlap is handled natively within LangChain splitters.
    return chunk1 + "\n... [OVERLAP] ...\n" + chunk2
