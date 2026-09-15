import os
from typing import Any
from .xsc_libc_exceptions import ConfigurationError

class AppConfig:
    """
    Minimal configuration handler for the OneApp Agentic Platform.
    Sources configuration primarily from the environment.
    """
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Retrieve an optional configuration value.
        """
        return os.environ.get(key, default)
    
    @classmethod
    def require(cls, key: str) -> str:
        """
        Retrieve a required configuration value.
        Raises ConfigurationError if the key is missing or empty.
        """
        val = os.environ.get(key)
        if not val or not val.strip():
            raise ConfigurationError(f"Missing required configuration key: {key}")
        return val

    # Centralized configuration accessors can be added below as needed by later phases
    @classmethod
    def get_llm_api_key(cls) -> str:
        return cls.require("NVIDIA_NIM_API_KEY")

    @classmethod
    def get_fees_payments_service_url(cls) -> str:
        """
        Retrieves the base URL for the Fees & Payments internal API.
        Defaults to http://localhost:8000 matching the standard FastAPI local dev port
        where the POC's unified entry point runs.
        """
        return cls.get("FEES_PAYMENTS_SERVICE_URL", "http://localhost:8000")
