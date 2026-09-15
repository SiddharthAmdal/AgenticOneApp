import os
import json
import io
import logging

from xsc_lib.xsc_lib_common.xsc_libc_logger import get_logger
from xsc_lib.xsc_lib_common.xsc_libc_exceptions import ConfigurationError, OneAppBaseException
from xsc_lib.xsc_lib_common.xsc_libc_config import AppConfig

import modules.m_admissions
import modules.m_fees_payments
import main

def run_tests():
    print("--- Phase 4.2 Validation ---")

    # 1. Test existing Phase 4.1 packages import
    print("Phase 4.1 imports OK.")

    # 2. Test Configuration Handling
    os.environ["TEST_KEY"] = "TEST_VAL"
    assert AppConfig.get("TEST_KEY") == "TEST_VAL"
    assert AppConfig.require("TEST_KEY") == "TEST_VAL"
    
    try:
        AppConfig.require("MISSING_KEY")
        print("FAIL: Config require did not throw error")
    except ConfigurationError as e:
        print("Config require missing threw ConfigurationError OK.")

    # 3. Test Exceptions
    try:
        raise ConfigurationError("Test exception")
    except OneAppBaseException:
        print("Exceptions hierarchy OK.")

    # 4. Test Logger
    logger = get_logger("test_logger")
    log_capture_string = io.StringIO()
    handler = logging.StreamHandler(log_capture_string)
    
    # We must format using our formatter directly to capture it since the logger
    # adds a standard StreamHandler in its factory.
    from xsc_lib.xsc_lib_common.xsc_libc_logger import StructuredJSONFormatter
    handler.setFormatter(StructuredJSONFormatter())
    
    # Temporarily remove other handlers and add our capture handler
    logger.handlers = []
    logger.addHandler(handler)
    
    extra = {"structured_payload": {"correlation_id": "123", "action": "test_action"}}
    logger.info("This is a test log", extra=extra)
    
    log_content = log_capture_string.getvalue().strip()
    log_json = json.loads(log_content)
    
    assert log_json["message"] == "This is a test log"
    assert log_json["level"] == "INFO"
    assert log_json["correlation_id"] == "123"
    assert log_json["action"] == "test_action"
    assert "timestamp" in log_json
    print("Structured logging JSON output OK.")

if __name__ == "__main__":
    run_tests()
