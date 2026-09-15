import json
import httpx
import pytest
from datetime import datetime, timezone
from langchain_core.callbacks.manager import CallbackManagerForToolRun

from xsc_lib.xsc_lib_common.agent_contracts import StudentPaymentRequest, StudentPaymentResult
from modules.m_admissions.clients.fees_payments_client import FeesPaymentsClient, DelegationError
from modules.m_admissions.tools.admissions_tools import DelegateStudentPaymentTool
from xsc_lib.xsc_lib_common.xsc_libc_exceptions import ConfigurationError

def mock_transport_success(request: httpx.Request):
    # Ensure correct headers and url
    assert request.headers.get("x-agent-identity") == "agent.admissions.primary"
    assert "fees-payments" in str(request.url)
    
    payload = json.loads(request.read())
    
    result = {
        "ContractVersion": "1.0",
        "CorrelationID": payload.get("CorrelationID"),
        "IdempotencyKey": payload.get("IdempotencyKey"),
        "RequestStatus": "Completed",
        "PaymentStatus": "Success",
        "ReceiptID": "RCPT-1234",
        "Timestamp": datetime.now(timezone.utc).isoformat()
    }
    return httpx.Response(200, json=result)

def mock_transport_declined(request: httpx.Request):
    payload = json.loads(request.read())
    result = {
        "ContractVersion": "1.0",
        "CorrelationID": payload.get("CorrelationID"),
        "IdempotencyKey": payload.get("IdempotencyKey"),
        "RequestStatus": "Completed",
        "PaymentStatus": "Declined",
        "FailureReason": "Insufficient funds",
        "Timestamp": datetime.now(timezone.utc).isoformat()
    }
    return httpx.Response(200, json=result)

def mock_transport_503(request: httpx.Request):
    return httpx.Response(503, json={"detail": "Service Unavailable"})

def mock_transport_malformed(request: httpx.Request):
    return httpx.Response(200, json={"NotAContract": True})

def test_client_success():
    transport = httpx.MockTransport(mock_transport_success)
    # Patch httpx.Client in the module
    import modules.m_admissions.clients.fees_payments_client as fp_client_mod
    original_client = fp_client_mod.httpx.Client
    
    class MockHttpxClient(httpx.Client):
        def __init__(self, **kwargs):
            kwargs["transport"] = transport
            super().__init__(**kwargs)
            
    fp_client_mod.httpx.Client = MockHttpxClient
    
    try:
        client = FeesPaymentsClient(base_url="http://mock-service")
        req = StudentPaymentRequest(
            ContractVersion="1.0",
            RequestingDomain="Admissions",
            RequestingAgent="agent.admissions.primary",
            CorrelationID="corr-1",
            IdempotencyKey="idem-1",
            StudentID="S-1",
            ObligationType="AdmissionFee",
            Amount="500.0",
            Currency="USD",
            Timestamp="2026-09-15T10:00:00Z"
        )
        result = client.delegate_payment(req)
        assert result.correlation_id == "corr-1"
        assert result.payment_status.value == "Success"
        assert result.receipt_id == "RCPT-1234"
    finally:
        fp_client_mod.httpx.Client = original_client

def test_client_declined():
    transport = httpx.MockTransport(mock_transport_declined)
    import modules.m_admissions.clients.fees_payments_client as fp_client_mod
    original_client = fp_client_mod.httpx.Client
    class MockHttpxClient(httpx.Client):
        def __init__(self, **kwargs):
            kwargs["transport"] = transport
            super().__init__(**kwargs)
    fp_client_mod.httpx.Client = MockHttpxClient
    
    try:
        client = FeesPaymentsClient(base_url="http://mock-service")
        req = StudentPaymentRequest(
            ContractVersion="1.0",
            RequestingDomain="Admissions",
            RequestingAgent="agent.admissions.primary",
            CorrelationID="corr-1",
            IdempotencyKey="idem-1",
            StudentID="S-1",
            ObligationType="AdmissionFee",
            Amount="500.0",
            Currency="USD",
            Timestamp="2026-09-15T10:00:00Z"
        )
        result = client.delegate_payment(req)
        assert result.payment_status.value == "Declined"
        assert result.failure_reason == "Insufficient funds"
    finally:
        fp_client_mod.httpx.Client = original_client

def test_client_503():
    transport = httpx.MockTransport(mock_transport_503)
    import modules.m_admissions.clients.fees_payments_client as fp_client_mod
    original_client = fp_client_mod.httpx.Client
    class MockHttpxClient(httpx.Client):
        def __init__(self, **kwargs):
            kwargs["transport"] = transport
            super().__init__(**kwargs)
    fp_client_mod.httpx.Client = MockHttpxClient
    
    try:
        client = FeesPaymentsClient(base_url="http://mock-service")
        req = StudentPaymentRequest(
            ContractVersion="1.0",
            RequestingDomain="Admissions",
            RequestingAgent="agent.admissions.primary",
            CorrelationID="corr-1",
            IdempotencyKey="idem-1",
            StudentID="S-1",
            ObligationType="AdmissionFee",
            Amount="500.0",
            Currency="USD",
            Timestamp="2026-09-15T10:00:00Z"
        )
        with pytest.raises(DelegationError) as exc_info:
            client.delegate_payment(req)
        assert "Service Unavailable" in str(exc_info.value)
    finally:
        fp_client_mod.httpx.Client = original_client

def test_client_malformed():
    transport = httpx.MockTransport(mock_transport_malformed)
    import modules.m_admissions.clients.fees_payments_client as fp_client_mod
    original_client = fp_client_mod.httpx.Client
    class MockHttpxClient(httpx.Client):
        def __init__(self, **kwargs):
            kwargs["transport"] = transport
            super().__init__(**kwargs)
    fp_client_mod.httpx.Client = MockHttpxClient
    
    try:
        client = FeesPaymentsClient(base_url="http://mock-service")
        req = StudentPaymentRequest(
            ContractVersion="1.0",
            RequestingDomain="Admissions",
            RequestingAgent="agent.admissions.primary",
            CorrelationID="corr-1",
            IdempotencyKey="idem-1",
            StudentID="S-1",
            ObligationType="AdmissionFee",
            Amount="500.0",
            Currency="USD",
            Timestamp="2026-09-15T10:00:00Z"
        )
        with pytest.raises(DelegationError) as exc_info:
            client.delegate_payment(req)
        assert "Malformed response contract" in str(exc_info.value)
    finally:
        fp_client_mod.httpx.Client = original_client

def test_tool_correlation_id_missing():
    tool = DelegateStudentPaymentTool(caps=None)
    res = tool.invoke({"student_id": "S-1", "amount": 100.0, "idempotency_key": "idem-1"})
    assert res["status"] == "error"
    assert "ConfigurationError" in res["error_type"]
    assert "correlation_id is missing" in res["message"]

def test_tool_execution_success():
    transport = httpx.MockTransport(mock_transport_success)
    import modules.m_admissions.clients.fees_payments_client as fp_client_mod
    original_client = fp_client_mod.httpx.Client
    class MockHttpxClient(httpx.Client):
        def __init__(self, **kwargs):
            kwargs["transport"] = transport
            super().__init__(**kwargs)
    fp_client_mod.httpx.Client = MockHttpxClient
    
    try:
        tool = DelegateStudentPaymentTool(caps=None)
        res = tool.invoke(
            {"student_id": "S-1", "amount": 100.0, "idempotency_key": "idem-1"},
            config={"metadata": {"correlation_id": "corr-1"}}
        )
        assert res["status"] == "success"
        assert res["data"]["CorrelationID"] == "corr-1"
        assert res["data"]["PaymentStatus"] == "Success"
    finally:
        fp_client_mod.httpx.Client = original_client
