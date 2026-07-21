import re

class DocumentCleaner:
    """
    Cleans raw extracted text before Chunking and Embedding.
    Removing noise leads to significantly higher accuracy in Vector Retrieval (RAG).
    """
    
    @staticmethod
    def clean(text: str) -> str:
        # Strip Guide Signature, HOD Signature, and typical footers
        cleaned = re.sub(r'(?i)(Guide Signature|HOD Signature|Signature:|Approved by:).*', '', text)
        
        # Remove typical page number footers (e.g., "Page 1 of 5" or just "- 1 -")
        cleaned = re.sub(r'(?i)^\s*(?:page)?\s*\d+\s*(?:of\s*\d+)?\s*$', '', cleaned, flags=re.MULTILINE)
        
        # Remove repeated non-empty lines (often header/footer noise repeated)
        # We will split, dedup adjacent, and rejoin
        lines = cleaned.split('\n')
        dedup_lines = []
        for line in lines:
            if not dedup_lines or line.strip() != dedup_lines[-1].strip():
                dedup_lines.append(line)
        cleaned = '\n'.join(dedup_lines)

        # Strip out zero-width spaces and formatting artifacts
        cleaned = re.sub(r'[\u200b\u200c\u200d\u200e\u200f\ufeff]', '', cleaned)
        # Normalize continuous horizontal spaces
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)
        # Normalize continuous vertical spaces (newlines), thus removing empty lines > 3
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        return cleaned.strip()
