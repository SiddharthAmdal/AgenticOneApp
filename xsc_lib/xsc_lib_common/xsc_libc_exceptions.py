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
