from app.domain.schemas.retriever import RetrieverRequest
from app.core.exceptions import RetrieverException

class RetrieverValidator:
    """
    Validates incoming retrieval requests before expensive embedding and database calls.
    """
    
    @staticmethod
    def validate_request(request: RetrieverRequest) -> None:
        if not request.query or not request.query.strip():
            raise RetrieverException("Validation Error: Question cannot be empty.")
        
        if request.top_k < 1:
            raise RetrieverException("Validation Error: top_k must be at least 1.")
