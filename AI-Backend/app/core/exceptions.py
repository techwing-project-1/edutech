from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.logger import logger

class DomainException(Exception):
    """
    Base custom exception for the domain layer.
    Allows for structured error propagation.
    """
    def __init__(self, message: str, status_code: int = 400, error_code: str = "DOMAIN_ERROR", details: dict = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class UnsupportedMode(DomainException):
    def __init__(self, message: str = "Unsupported AI Mode", details: dict = None):
        super().__init__(message=message, status_code=400, error_code="UNSUPPORTED_MODE", details=details)

class ValidationError(DomainException):
    def __init__(self, message: str = "Validation failed", details: dict = None):
        super().__init__(message=message, status_code=422, error_code="VALIDATION_ERROR", details=details)

class ProviderUnavailable(DomainException):
    def __init__(self, message: str = "LLM Provider is unavailable", details: dict = None):
        super().__init__(message=message, status_code=503, error_code="PROVIDER_UNAVAILABLE", details=details)

class EmbeddingFailure(DomainException):
    def __init__(self, message: str = "Failed to generate embeddings", details: dict = None):
        super().__init__(message=message, status_code=500, error_code="EMBEDDING_FAILURE", details=details)

class OpenSearchFailure(DomainException):
    def __init__(self, message: str = "OpenSearch operation failed", details: dict = None):
        super().__init__(message=message, status_code=500, error_code="OPENSEARCH_FAILURE", details=details)

class TimeoutError(DomainException):
    def __init__(self, message: str = "Operation timed out", details: dict = None):
        super().__init__(message=message, status_code=504, error_code="TIMEOUT_ERROR", details=details)

class RetryExceeded(DomainException):
    def __init__(self, message: str = "Maximum retries exceeded", details: dict = None):
        super().__init__(message=message, status_code=502, error_code="RETRY_EXCEEDED", details=details)

class RateLimitExceeded(DomainException):
    def __init__(self, message: str = "Rate limit exceeded", details: dict = None):
        super().__init__(message=message, status_code=429, error_code="RATE_LIMIT_EXCEEDED", details=details)

class LLMProviderException(DomainException):
    """
    Specific exception for LLM Provider failures (e.g., timeout, auth error).
    """
    pass

class ProviderResponseParsingError(LLMProviderException):
    """
    Specific exception for failures when parsing the text content out of a raw LLM response.
    """
    pass

class ProviderAuthenticationError(LLMProviderException):
    def __init__(self, message: str = "Provider authentication failed", details: dict = None):
        super().__init__(message=message, status_code=401, error_code="PROVIDER_AUTH_ERROR", details=details)

class ProviderAuthorizationError(LLMProviderException):
    def __init__(self, message: str = "Provider authorization failed", details: dict = None):
        super().__init__(message=message, status_code=403, error_code="PROVIDER_AUTHZ_ERROR", details=details)

class ProviderQuotaExceeded(LLMProviderException):
    def __init__(self, message: str = "Provider quota or credits exhausted", details: dict = None):
        super().__init__(message=message, status_code=402, error_code="PROVIDER_QUOTA_EXHAUSTED", details=details)

class PromptException(DomainException):
    """
    Specific exception for Prompt Engineering failures (e.g., missing variables, template not found).
    """
    pass

class DocumentProcessingException(DomainException):
    """
    Specific exception for Document Processing failures (e.g., unsupported format, max size exceeded, parsing error).
    """
    pass

class ChunkingException(DomainException):
    """
    Specific exception for Chunking Layer failures (e.g., invalid strategy, empty chunks).
    """
    pass

class EmbeddingException(DomainException):
    """
    Specific exception for Embedding Layer failures (e.g., model load failure, empty batch).
    """
    pass

class VectorStoreException(DomainException):
    """
    Specific exception for Vector Database operations (e.g., OpenSearch init, insertion error, search failure).
    """
    pass

class RetrieverException(DomainException):
    """
    Specific exception for Retrieval operations (e.g., threshold errors, invalid queries).
    """
    pass

class RAGException(DomainException):
    """
    Specific exception for failures in the RAG Orchestration layer.
    """
    pass

class GeneralAIException(DomainException):
    """
    Specific exception for failures in the General AI Chat layer.
    """
    pass

class ProviderError(GeneralAIException):
    """
    Exception raised when a specific LLM Provider fails (e.g. 500 error).
    """
    pass

class RateLimitError(ProviderError):
    """
    Exception raised when the provider rate limits the application.
    """
    pass

class ContextOverflowError(GeneralAIException):
    """
    Exception raised when the context window exceeds max tokens.
    """
    pass

class PromptInjectionDetected(GeneralAIException):
    """
    Exception raised when a jailbreak or prompt injection attempt is detected.
    """
    pass

class ContentGenerationError(DomainException):
    """
    Specific exception for general failures in the Content Generation Engine.
    """
    pass

class EmptyContextError(DomainException):
    """
    Exception raised when the vector search returns zero valid chunks.
    """
    pass

class UnsupportedGenerationModeError(DomainException):
    """
    Specific exception when an unsupported mode is requested.
    """
    pass

class ContentValidationError(DomainException):
    """
    Specific exception for when generated content fails validation.
    """
    pass

class SummaryException(DomainException):
    """
    Specific exception for failures in the Summary Generator Module.
    """
    pass

class SummaryValidationError(DomainException):
    """
    Specific exception for when summary request parameters are invalid.
    """
    pass

class FlashcardException(DomainException):
    """
    Specific exception for failures in the Flashcards Generator Module.
    """
    pass

class FlashcardValidationError(DomainException):
    """
    Specific exception for when flashcard request parameters are invalid.
    """
    pass

class LLMReturnedInvalidJSON(ContentGenerationError):
    """
    Exception raised when the LLM returns malformed JSON that cannot be parsed.
    Includes the raw output, provider, and model for debugging.
    """
    def __init__(self, message: str, raw_output: str = "", provider: str = "Unknown", model: str = "Unknown", request_id: str = "Unknown"):
        details = {
            "raw_output": raw_output,
            "provider": provider,
            "model": model,
            "request_id": request_id
        }
        super().__init__(message=message, status_code=500, error_code="LLM_INVALID_JSON", details=details)

# Task 15 Specific Exceptions
class InvalidLLMJSON(LLMReturnedInvalidJSON):
    pass

class JSONRepairFailed(ContentGenerationError):
    pass

class StructuredOutputFailed(ContentGenerationError):
    pass

class EmptyLLMResponse(ContentGenerationError):
    pass

class LLMOutputTruncated(ContentGenerationError):
    pass

class RetryExhausted(ContentGenerationError):
    pass

class QuizException(DomainException):
    """
    Specific exception for failures in the Quiz Generator Module.
    """
    pass

class QuizValidationError(DomainException):
    """
    Specific exception for when quiz request parameters are invalid.
    """
    pass

class StudyNotesException(DomainException):
    """
    Specific exception for failures in the Study Notes Generator Module.
    """
    pass

class StudyNotesValidationError(DomainException):
    """
    Specific exception for when study notes request parameters are invalid.
    """
    pass


class AgentException(DomainException):
    """
    Specific exception for failures in the OpenClaw Agent Framework.
    """
    pass

class AgentValidationError(DomainException):
    """
    Specific exception for when agent request parameters are invalid.
    """
    pass

class AssignmentAgentException(AgentException):
    """
    Exception for Assignment Agent failures.
    """
    pass

class AssignmentAgentValidationError(AgentValidationError):
    """
    Exception for invalid Assignment Agent requests.
    """
    pass

class CalendarAgentException(AgentException):
    """
    Exception for Calendar Agent failures.
    """
    pass

class CalendarAgentValidationError(AgentValidationError):
    """
    Exception for invalid Calendar Agent requests.
    """
    pass

class StudyPlannerException(AgentException):
    """
    Exception for Study Planner Agent failures.
    """
    pass

class StudyPlannerValidationError(AgentValidationError):
    """
    Exception for invalid Study Planner Agent requests.
    """
    pass

class NotificationException(DomainException):
    """
    Base exception for Notification Engine failures.
    """
    pass

class NotificationValidationError(NotificationException):
    """
    Exception for invalid Notification requests.
    """
    pass

class ReminderAgentException(AgentException):
    """
    Exception for Reminder Agent failures.
    """
    pass

class ReminderAgentValidationError(AgentValidationError):
    """
    Exception for invalid Reminder Agent requests.
    """
    pass

class OrchestratorException(DomainException):
    """
    Base exception for Orchestrator routing failures.
    """
    pass

class OrchestratorValidationError(OrchestratorException):
    """
    Exception for invalid Orchestrator requests.
    """
    pass

class MonitoringException(DomainException):
    """
    Base exception for monitoring layer.
    """
    pass

class MonitoringValidationError(MonitoringException):
    """
    Exception for invalid monitoring requests.
    """
    pass

class ConfigurationException(DomainException):
    """
    Base exception for configuration layer.
    """
    pass

class InvalidConfigurationError(DomainException):
    """Raised when environment variables or configurations are missing."""
    pass

class HallucinationException(DomainException):
    """Raised when generated text fails grounding validation against retrieved context."""
    pass

class ConfigurationValidationError(ConfigurationException):
    """
    Exception for invalid configuration modifications.
    """
    pass

from fastapi.exceptions import RequestValidationError
import uuid

def add_exception_handlers(app: FastAPI):
    """
    Registers global exception handlers for the FastAPI app.
    Prevents raw stack traces from reaching the client.
    """
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Schema validation error: {exc.errors()} - Path: {request.url.path}")
        trace_id = str(uuid.uuid4())
        return JSONResponse(
            status_code=422,
            content={
                "error_code": "VALIDATION_ERROR",
                "user_message": "The request contains invalid data.",
                "developer_message": str(exc.errors()),
                "trace_id": trace_id,
                "retryable": False,
                "status": 422
            }
        )

    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException):
        logger.warning(f"Domain error: {exc.message} - Code: {exc.error_code} - Path: {request.url.path}")
        trace_id = str(uuid.uuid4())
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.error_code,
                "user_message": exc.message,
                "developer_message": str(exc.details) if exc.details else exc.message,
                "trace_id": trace_id,
                "retryable": exc.status_code >= 500 or exc.status_code == 429,
                "status": exc.status_code
            }
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        trace_id = str(uuid.uuid4())
        logger.error(f"Unhandled server error [{trace_id}]: {str(exc)} - Path: {request.url.path}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error_code": "INTERNAL_SERVER_ERROR",
                "user_message": "An unexpected system error occurred. Please try again later.",
                "developer_message": "Internal Server Error (stack trace suppressed)",
                "trace_id": trace_id,
                "retryable": True,
                "status": 500
            }
        )
