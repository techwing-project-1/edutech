def normalize_metadata(value: str | int | None):
    """
    Normalizes a metadata value for exact matching in vector databases.
    Converts to string (if string), strips whitespace, and lowercases.
    Leaves integers (like semester) untouched.
    """
    if value is None:
        return None
    if isinstance(value, str):
        return " ".join(value.strip().lower().split())
    return value
