from app.domain.interfaces.document_loader import DocumentLoaderInterface
from app.infrastructure.document_parser.pdf_loader import PDFLoader
from app.infrastructure.document_parser.txt_loader import TXTLoader
from app.infrastructure.document_parser.docx_loader import DOCXLoader
from app.core.exceptions import DocumentProcessingException
from app.utils.file_utils import get_file_extension

class DocumentLoaderFactory:
    """
    Factory Pattern for document loaders.
    Dynamically routes a document to the correct parsing engine based on its extension.
    """
    
    @staticmethod
    def get_loader(file_path: str) -> DocumentLoaderInterface:
        ext = get_file_extension(file_path)
        
        if ext == ".pdf":
            return PDFLoader()
        elif ext == ".txt":
            return TXTLoader()
        elif ext == ".docx":
            return DOCXLoader()
        # Future Extensions:
        # elif ext == ".pptx": return PPTXLoader()
        # elif ext == ".md": return MarkdownLoader()
        else:
            raise DocumentProcessingException(f"Unsupported document format: {ext}")
