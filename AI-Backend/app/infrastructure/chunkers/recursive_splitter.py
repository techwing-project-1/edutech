from typing import List
from app.domain.interfaces.chunker import ChunkerInterface
from app.domain.schemas.document import DocumentResponse
from app.core.chunk_config import chunk_config
from langchain_text_splitters import RecursiveCharacterTextSplitter

class RecursiveTextSplitter(ChunkerInterface):
    """
    Utilizes LangChain's RecursiveCharacterTextSplitter.
    Configured to preserve tables, bullet points, and headings.
    """
    
    @property
    def strategy_name(self) -> str:
        return "recursive"
        
    def split(self, document: DocumentResponse) -> List[str]:
        text = document.content
        
        if not text:
            return []
            
        # 1 token ~= 4 characters for sizing
        char_chunk_size = chunk_config.chunk_size * 4
        char_overlap = chunk_config.chunk_overlap * 4
            
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=char_chunk_size,
            chunk_overlap=char_overlap,
            separators=[
                "\n\n",
                "\n",
                "|",       # Tables
                "•",       # Bullet points
                " - ",     # Dash lists
                "CERTIFICATIONS",
                "SKILLS",
                "EXPERIENCE",
                "PROJECTS",
                ". ",
                " ",
                ""
            ]
        )
        
        chunks = splitter.split_text(text)
        return chunks if chunks else [text]
