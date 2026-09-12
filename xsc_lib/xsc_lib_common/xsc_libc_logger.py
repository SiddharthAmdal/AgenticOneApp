import logging
import json
from datetime import datetime
from typing import Any, Dict

class StructuredJSONFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings for structured observability.
    Supports injecting standard and custom payload attributes.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger_name": record.name,
            "message": record.getMessage(),
        }
        
        # Merge any extra kwargs passed via the 'extra' dict in the log call
        if hasattr(record, "structured_payload") and isinstance(record.structured_payload, dict):
            log_obj.update(record.structured_payload)
            
        return json.dumps(log_obj)

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured structured logger.
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if already configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredJSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        # Prevent propagation to the root logger to avoid double logging
        logger.propagate = False
        
    return logger
