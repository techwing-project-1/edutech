class OpenSearchException(Exception):
    """Base exception for all OpenSearch related errors."""
    pass

class ConfigurationError(OpenSearchException):
    """Raised when OpenSearch configuration is missing or invalid."""
    pass

class OpenSearchConnectionError(OpenSearchException):
    """Raised when connection to OpenSearch cluster fails."""
    pass

class AuthenticationError(OpenSearchException):
    """Raised when authentication to OpenSearch cluster fails."""
    pass

class IndexCreationError(OpenSearchException):
    """Raised when creating an OpenSearch index fails."""
    pass

class ClusterUnavailable(OpenSearchException):
    """Raised when the OpenSearch cluster is unhealthy or unreachable."""
    pass
