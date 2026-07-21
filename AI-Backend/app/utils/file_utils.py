import os
import uuid
import pathlib

def get_file_extension(filename: str) -> str:
    """Safely extract the file extension in lowercase."""
    return pathlib.Path(filename).suffix.lower()

def generate_secure_filename(original_filename: str) -> str:
    """
    Generate a unique, safe filename to prevent directory traversal attacks.
    Retains the original extension.
    """
    ext = get_file_extension(original_filename)
    return f"{uuid.uuid4().hex}{ext}"

def get_file_size(filepath: str) -> int:
    """Return the physical file size in bytes."""
    if not os.path.exists(filepath):
        return 0
    return os.path.getsize(filepath)
