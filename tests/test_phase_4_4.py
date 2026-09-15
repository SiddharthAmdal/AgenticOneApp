import json
from decimal import Decimal
from datetime import datetime, timezone
from pydantic import ValidationError

from xsc_lib.xsc_lib_common.agent_contracts import (
    StudentPaymentRequest,
    StudentPaymentResult,
    RequestStatus,
    PaymentStatus
)

def run_tests():
    print("--- Phase 4.4 Validation ---")

    # A. Valid StudentPaymentRequest
    req_data = {
        "ContractVersion": "1.0",
        "RequestingDomain": "Admissions",
        "RequestingAgent": "AdmissionsAgent",
        "CorrelationID": "CORR-123",
        "IdempotencyKey": "IDEMP-999",
        "StudentID": "STU-001",
        "ObligationType": "AdmissionDeposit",
        "Amount": 500.50, # Pydantic will convert to Decimal
        "Currency": "USD",
        "Timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    req = StudentPaymentRequest(**req_data)
    print("A. Valid StudentPaymentRequest OK.")

    # B. Invalid StudentPaymentRequest (missing required)
    invalid_data = req_data.copy()
    del invalid_data["Amount"]
    try:
        StudentPaymentRequest(**invalid_data)
        print("FAIL: Accepted missing Amount")
    except ValidationError:
        print("B. Invalid StudentPaymentRequest rejection OK.")

    # C. Valid StudentPaymentResult
    res_data = {
        "ContractVersion": "1.0",
        "CorrelationID": "CORR-123",
        "IdempotencyKey": "IDEMP-999",
        "RequestStatus": "Completed",
        "PaymentStatus": "Success",
        "Timestamp": datetime.now(timezone.utc).isoformat()
    }
    res = StudentPaymentResult(**res_data)
    print("C. Valid StudentPaymentResult OK.")

    # D. Invalid statuses
    invalid_status_data = res_data.copy()
    invalid_status_data["PaymentStatus"] = "SomethingElse"
    try:
        StudentPaymentResult(**invalid_status_data)
        print("FAIL: Accepted invalid PaymentStatus")
    except ValidationError:
        print("D. Invalid statuses rejection OK.")

    # E. Identifier distinction
    assert req.correlation_id != req.idempotency_key
    print("E. Identifier distinction OK.")

    # F. Optional fields
    # Testing missing (already tested above) and present
    req_data_optional = req_data.copy()
    req_data_optional["BusinessReason"] = "Late payment"
    req_opt = StudentPaymentRequest(**req_data_optional)
    assert req_opt.business_reason == "Late payment"
    
    res_data_optional = res_data.copy()
    res_data_optional["ReceiptID"] = "REC-444"
    res_data_optional["FailureReason"] = "N/A"
    res_opt = StudentPaymentResult(**res_data_optional)
    assert res_opt.receipt_id == "REC-444"
    assert res_opt.failure_reason == "N/A"
    print("F. Optional fields parsing OK.")

    # G. Contract version
    invalid_version_data = req_data.copy()
    invalid_version_data["ContractVersion"] = "2.0"
    try:
        StudentPaymentRequest(**invalid_version_data)
        print("FAIL: Accepted invalid ContractVersion")
    except ValidationError:
        print("G. Contract version validation OK.")

    # G.2 Extra Fields
    # Verify consumers ignore unrecognized fields as per canonical contract
    extra_field_data = req_data.copy()
    extra_field_data["FutureUnknownField"] = "Should Be Ignored"
    req_extra = StudentPaymentRequest(**extra_field_data)
    assert not hasattr(req_extra, "FutureUnknownField"), "Extra fields should be ignored/dropped"
    assert not hasattr(req_extra, "future_unknown_field"), "Extra fields should be ignored/dropped"
    print("G.2 Extra fields ignored OK.")

    # H. JSON round trip & I. Monetary representation
    # Using Decimal explicitly
    req_data_exact = req_data.copy()
    req_data_exact["Amount"] = "500.50"
    req_exact = StudentPaymentRequest(**req_data_exact)
    
    json_str = req_exact.model_dump_json(by_alias=True)
    json_dict = json.loads(json_str)
    
    req_roundtrip = StudentPaymentRequest(**json_dict)
    assert req_roundtrip.amount == Decimal("500.50"), f"Expected 500.50, got {req_roundtrip.amount}"
    # Python decimal to json converts to string or float depending on config,
    # but we just need to ensure the semantic value survives.
    assert req_roundtrip.correlation_id == "CORR-123"
    print("H. JSON round trip & I. Monetary representation OK.")

    # J. Contract isolation
    import sys
    assert 'sqlite3' not in sys.modules, "sqlite3 should not be loaded by contracts"
    assert 'm_admissions.repositories' not in sys.modules, "repositories should not be loaded"
    print("J. Contract isolation OK.")

if __name__ == "__main__":
    run_tests()
