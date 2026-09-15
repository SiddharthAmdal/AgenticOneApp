class OneAppBaseException(Exception):
    """
    Base exception for all custom OneApp exceptions.
    Ensures all platform exceptions can be caught uniformly if needed.
    """
    pass

class ConfigurationError(OneAppBaseException):
    """Raised when a required configuration value is missing or invalid."""
    pass

class ValidationException(OneAppBaseException):
    """Raised when structural or logical validation fails."""
    pass

class EntityNotFoundError(OneAppBaseException):
    """Raised when a requested business or state entity cannot be found."""
    pass

class StateMutationError(OneAppBaseException):
    """Raised when an illegal or failed state mutation is attempted."""
    pass

class LLMProviderError(OneAppBaseException):
    """Base exception for all LLM provider related errors."""
    pass

class ProviderAuthenticationError(LLMProviderError):
    """Raised when authentication with the provider fails (e.g. invalid API key)."""
    pass

class ProviderTimeoutError(LLMProviderError):
    """Raised when a request to the provider times out."""
    pass

class ProviderServerError(LLMProviderError):
    """Raised when the provider encounters an internal server error or is unavailable."""
    pass

class ProviderRequestError(LLMProviderError):
    """Raised when a request to the provider is malformed or invalid."""
    pass
