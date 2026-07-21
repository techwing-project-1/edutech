class HODAnalyticsException(Exception):
    """Base exception for HOD Analytics module."""
    pass

class HODValidationException(HODAnalyticsException):
    """Raised when incoming analytics data fails structural validation."""
    pass

class HODLLMException(HODAnalyticsException):
    """Raised when the LLM fails to generate insights."""
    pass
