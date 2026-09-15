import json
import os
import sqlite3
import httpx
import pytest
from datetime import datetime, timezone

from xsc_lib.xsc_lib_common.agent_contracts import StudentPaymentRequest
from modules.m_admissions.clients.fees_payments_client import FeesPaymentsClient, DelegationError
from modules.m_fees_payments.capabilities.fees_payments_caps import FeesPaymentsCapabilities
from modules.m_fees_payments.repositories.fees_payments_repo import FeesPaymentsRepository

# In tests, AppConfig will default to MAX_RETRY_ATTEMPTS=3, RETRY_DELAY_SECONDS=1.0.
# We patch os.environ to make it fast for testing.
@pytest.fixture(autouse=True)
def set_env_vars():
    os.environ["MAX_RETRY_ATTEMPTS"] = "3"
    os.environ["RETRY_DELAY_SECONDS"] = "0.0"
    yield
    os.environ.pop("MAX_RETRY_ATTEMPTS", None)
    os.environ.pop("RETRY_DELAY_SECONDS", None)

@pytest.fixture
def repo(tmp_path):
    db_path = tmp_path / "test_fees_payments.db"
    return FeesPaymentsRepository(str(db_path))

@pytest.fixture
def caps(repo):
    return FeesPaymentsCapabilities(repo)

@pytest.fixture
def sample_request():
    return StudentPaymentRequest(
        ContractVersion="1.0",
        RequestingDomain="Admissions",
        RequestingAgent="agent.admissions.primary",
        CorrelationID="corr-1",
        IdempotencyKey="idem-test",
        StudentID="S-1",
        ObligationType="AdmissionFee",
        Amount="500.0",
        Currency="USD",
        Timestamp="2026-09-15T10:00:00Z"
    )

def test_business_failure_no_retry(sample_request):
    call_count = 0
    def mock_transport_declined(request: httpx.Request):
        nonlocal call_count
        call_count += 1
        return httpx.Response(200, json={
            "ContractVersion": "1.0",
            "CorrelationID": "corr-1",
            "IdempotencyKey": "idem-test",
            "RequestStatus": "Completed",
            "PaymentStatus": "Declined",
            "FailureReason": "Insufficient funds",
            "Timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    transport = httpx.MockTransport(mock_transport_declined)
    
    import modules.m_admissions.clients.fees_payments_client as fp_client_mod
    original_client = fp_client_mod.httpx.Client
    class MockHttpxClient(httpx.Client):
        def __init__(self, **kwargs):
            kwargs["transport"] = transport
            super().__init__(**kwargs)
    fp_client_mod.httpx.Client = MockHttpxClient
    
    try:
        client = FeesPaymentsClient(base_url="http://mock")
        res = client.delegate_payment(sample_request)
        assert res.payment_status.value == "Declined"
        assert call_count == 1  # No retries on legitimate business failure
    finally:
        fp_client_mod.httpx.Client = original_client

def test_validation_failure_no_retry(sample_request):
    call_count = 0
    def mock_transport_422(request: httpx.Request):
        nonlocal call_count
        call_count += 1
        return httpx.Response(422, json={"detail": "Bad amount"})
    
    transport = httpx.MockTransport(mock_transport_422)
    import modules.m_admissions.clients.fees_payments_client as fp_client_mod
    original_client = fp_client_mod.httpx.Client
    class MockHttpxClient(httpx.Client):
        def __init__(self, **kwargs):
            kwargs["transport"] = transport
            super().__init__(**kwargs)
    fp_client_mod.httpx.Client = MockHttpxClient
    
    try:
        client = FeesPaymentsClient(base_url="http://mock")
        with pytest.raises(DelegationError) as exc_info:
            client.delegate_payment(sample_request)
        assert "422" in str(exc_info.value)
        assert call_count == 1  # No retries on validation failure
    finally:
        fp_client_mod.httpx.Client = original_client

def test_transient_failure_retry(sample_request):
    call_count = 0
    def mock_transport_503(request: httpx.Request):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            return httpx.Response(503, json={"detail": "Service Unavailable"})
        return httpx.Response(200, json={
            "ContractVersion": "1.0",
            "CorrelationID": "corr-1",
            "IdempotencyKey": "idem-test",
            "RequestStatus": "Completed",
            "PaymentStatus": "Success",
            "ReceiptID": "RCPT-OK",
            "Timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    transport = httpx.MockTransport(mock_transport_503)
    import modules.m_admissions.clients.fees_payments_client as fp_client_mod
    original_client = fp_client_mod.httpx.Client
    class MockHttpxClient(httpx.Client):
        def __init__(self, **kwargs):
            kwargs["transport"] = transport
            super().__init__(**kwargs)
    fp_client_mod.httpx.Client = MockHttpxClient
    
    try:
        client = FeesPaymentsClient(base_url="http://mock")
        res = client.delegate_payment(sample_request)
        assert res.payment_status.value == "Success"
        assert res.receipt_id == "RCPT-OK"
        assert call_count == 3  # Two 503s + one 200
    finally:
        fp_client_mod.httpx.Client = original_client

def test_retry_exhaustion(sample_request):
    call_count = 0
    def mock_transport_504(request: httpx.Request):
        nonlocal call_count
        call_count += 1
        return httpx.Response(504, json={"detail": "Gateway Timeout"})
    
    transport = httpx.MockTransport(mock_transport_504)
    import modules.m_admissions.clients.fees_payments_client as fp_client_mod
    original_client = fp_client_mod.httpx.Client
    class MockHttpxClient(httpx.Client):
        def __init__(self, **kwargs):
            kwargs["transport"] = transport
            super().__init__(**kwargs)
    fp_client_mod.httpx.Client = MockHttpxClient
    
    try:
        client = FeesPaymentsClient(base_url="http://mock")
        with pytest.raises(DelegationError) as exc_info:
            client.delegate_payment(sample_request)
        assert "exhausted after 3 attempts" in str(exc_info.value)
        assert call_count == 3
    finally:
        fp_client_mod.httpx.Client = original_client

def test_direct_capability_idempotency(caps, repo, sample_request):
    # Attempt 1
    res1 = caps.collect_student_payment(sample_request)
    assert res1.payment_status.value == "Success"
    assert res1.receipt_id is not None
    r1 = res1.receipt_id
    
    # Check DB state
    with repo._get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM financial_obligations")
        ob_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM receipts")
        rc_count = c.fetchone()[0]
    
    assert ob_count == 1
    assert rc_count == 1
    
    # Attempt 2
    res2 = caps.collect_student_payment(sample_request)
    assert res2.payment_status.value == "Success"
    assert res2.receipt_id == r1  # Must return the identical receipt
    
    # Check DB state again - no new records
    with repo._get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM financial_obligations")
        assert c.fetchone()[0] == 1
        c.execute("SELECT COUNT(*) FROM receipts")
        assert c.fetchone()[0] == 1

def test_money_test(caps, repo, sample_request):
    """
    Attempt 1 -> Server executes -> Payment commits -> Timeout/Response Lost -> Client Retries ->
    Server receives retry -> Idempotency check catches it -> Returns original receipt -> Client succeeds.
    """
    call_count = 0
    
    def mock_transport_money_test(request: httpx.Request):
        nonlocal call_count
        call_count += 1
        
        # We manually decode the request and invoke the server capability
        payload = json.loads(request.read())
        req = StudentPaymentRequest(**payload)
        
        # Capability executes idempotently
        result = caps.collect_student_payment(req)
        
        if call_count == 1:
            # Simulate network timeout after successful server execution
            raise httpx.TimeoutException("Connection timed out after server execution")
        
        # Attempt 2: Server returns the result normally
        return httpx.Response(200, json=json.loads(result.model_dump_json(by_alias=True)))
    
    transport = httpx.MockTransport(mock_transport_money_test)
    import modules.m_admissions.clients.fees_payments_client as fp_client_mod
    original_client = fp_client_mod.httpx.Client
    class MockHttpxClient(httpx.Client):
        def __init__(self, **kwargs):
            kwargs["transport"] = transport
            super().__init__(**kwargs)
    fp_client_mod.httpx.Client = MockHttpxClient
    
    try:
        client = FeesPaymentsClient(base_url="http://mock")
        res = client.delegate_payment(sample_request)
        
        # The client should have succeeded on attempt 2
        assert res.payment_status.value == "Success"
        assert call_count == 2
        
        # Ensure only one payment was mutated
        with repo._get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM financial_obligations")
            assert c.fetchone()[0] == 1
            c.execute("SELECT COUNT(*) FROM receipts")
            assert c.fetchone()[0] == 1
            
    finally:
        fp_client_mod.httpx.Client = original_client
