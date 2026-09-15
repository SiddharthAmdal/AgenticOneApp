import json
import os
import httpx
import pytest
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from xsc_lib.xsc_lib_common.nim_adapter import LLMResponse, LLMToolCall
from modules.entry_api.routers.entry_router import router as entry_router, get_admissions_agent
from modules.m_fees_payments.routers.fees_payments_router import router as fp_router, get_fees_payments_agent

from modules.m_admissions.repositories.admissions_repo import AdmissionsRepository
from modules.m_admissions.capabilities.admissions_caps import AdmissionsCapabilities
from modules.m_admissions.agents.admissions_agent import AdmissionsAgent

from modules.m_fees_payments.repositories.fees_payments_repo import FeesPaymentsRepository
from modules.m_fees_payments.capabilities.fees_payments_caps import FeesPaymentsCapabilities
from modules.m_fees_payments.agents.fees_payments_agent import FeesPaymentsAgent

# Mock AppConfig defaults for testing
@pytest.fixture(autouse=True)
def set_env_vars():
    os.environ["MAX_RETRY_ATTEMPTS"] = "3"
    os.environ["RETRY_DELAY_SECONDS"] = "0.0"
    os.environ["FEES_PAYMENTS_SERVICE_URL"] = "http://testserver"
    yield
    os.environ.pop("MAX_RETRY_ATTEMPTS", None)
    os.environ.pop("RETRY_DELAY_SECONDS", None)
    os.environ.pop("FEES_PAYMENTS_SERVICE_URL", None)

@pytest.fixture
def adm_repo(tmp_path):
    db_path = tmp_path / "test_admissions.db"
    return AdmissionsRepository(str(db_path))

@pytest.fixture
def fp_repo(tmp_path):
    db_path = tmp_path / "test_fees_payments.db"
    return FeesPaymentsRepository(str(db_path))

@pytest.fixture
def adm_caps(adm_repo):
    return AdmissionsCapabilities(adm_repo)

@pytest.fixture
def fp_caps(fp_repo):
    return FeesPaymentsCapabilities(fp_repo)

@pytest.fixture
def mock_nim_adapter():
    class MockAdapter:
        def generate_response(self, system_prompt, messages, tools, **kwargs):
            pass
    return MockAdapter()

@pytest.fixture
def adm_agent(adm_caps, mock_nim_adapter):
    return AdmissionsAgent(adm_caps, mock_nim_adapter)

@pytest.fixture
def fp_agent(fp_caps, mock_nim_adapter):
    return FeesPaymentsAgent(fp_caps, mock_nim_adapter)

@pytest.fixture
def app(adm_agent, fp_agent):
    app = FastAPI()
    app.include_router(entry_router)
    app.include_router(fp_router)
    app.dependency_overrides[get_admissions_agent] = lambda: adm_agent
    app.dependency_overrides[get_fees_payments_agent] = lambda: fp_agent
    return app

def setup_admissions_db(adm_repo):
    with adm_repo._get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO admission_offers (offer_id, student_id, program_id, status, payment_required, expiration_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("O-100", "S-100", "P-1", "Issued", 1, "2099-12-31T23:59:59Z", datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat()))
        conn.commit()

def test_success_scenario(app, adm_repo, fp_repo, mock_nim_adapter, monkeypatch):
    """
    Test E2E Flow: Success
    """
    setup_admissions_db(adm_repo)
    import modules.m_admissions.clients.fees_payments_client as fp_client_mod
    tc = TestClient(app)
    class MockHttpxClient:
        def __init__(self, **kwargs): pass
        def __enter__(self): return tc
        def __exit__(self, *args): pass
    monkeypatch.setattr(fp_client_mod.httpx, "Client", MockHttpxClient)
    
    def mock_generate_response(messages, tools=None, trace_context=None):
        system_prompt = messages[0].content if messages else ""
        if "You are the Admissions Agent" in system_prompt:
            if len(messages) == 2:
                return LLMResponse(tool_calls=[LLMToolCall(id="t-1", type="function", function_name="evaluate_admission_requirements", arguments='{"offer_id": "O-100"}')])
            elif len(messages) == 4:
                return LLMResponse(tool_calls=[LLMToolCall(id="t-2", type="function", function_name="delegate_student_payment", arguments='{"student_id": "S-100", "amount": 500, "currency": "USD", "idempotency_key": "IDEM-1"}')])
            elif len(messages) == 6:
                last_msg = messages[-1].content
                print(f"DEBUG mock len=6: last_msg RAW={last_msg}")
                if "returned:" in last_msg:
                    last_msg = last_msg.split("returned:", 1)[1].strip()
                print(f"DEBUG mock len=6: last_msg STRIPPED={last_msg}")
                try:
                    res_dict = json.loads(last_msg)
                except Exception as e:
                    print(f"DEBUG mock len=6: json.loads failed: {e}")
                    import ast
                    try:
                        res_dict = ast.literal_eval(last_msg)
                    except Exception as e:
                        print(f"DEBUG mock len=6: ast failed: {e}")
                        res_dict = {}
                print(f"DEBUG mock len=6: res_dict={res_dict}")
                
                payment_result = res_dict.get("data", {})
                if isinstance(payment_result, str):
                    try:
                        payment_result = json.loads(payment_result)
                    except Exception:
                        pass
                arguments_str = json.dumps({"offer_id": "O-100", "payment_result": payment_result})
                print(f"DEBUG: sending arguments: {arguments_str}")
                return LLMResponse(tool_calls=[LLMToolCall(id="t-3", type="function", function_name="confirm_admission", arguments=arguments_str)])
            elif len(messages) == 8:
                last_msg = messages[-1].content
                if "error" in last_msg.lower():
                    raise ValueError(f"confirm_admission tool failed: {last_msg}")
                return LLMResponse(content=json.dumps({"status": "success", "message": "Admitted"}))
        else:
            import re, ast
            match = re.search(r"Request payload:\s*(\{.*?\})", system_prompt, re.DOTALL)
            payload = json.loads(match.group(1)) if match else {}
            print(f"DEBUG mock: parsed payload = {payload}")
            if len(messages) == 2:
                return LLMResponse(tool_calls=[LLMToolCall(id="f-1", type="function", function_name="validate_payment_request", arguments=json.dumps({"request_payload": payload}))])
            elif len(messages) == 4:
                return LLMResponse(tool_calls=[LLMToolCall(id="f-2", type="function", function_name="collect_student_payment", arguments=json.dumps({"request_payload": payload}))])
            elif len(messages) == 6:
                last_msg = messages[-1].content
                if "returned:" in last_msg:
                    last_msg = last_msg.split("returned:", 1)[1].strip()
                try:
                    try:
                        result_dict = json.loads(last_msg)
                    except Exception:
                        result_dict = ast.literal_eval(last_msg)
                    
                    if result_dict.get("status") == "success":
                        inner_data = result_dict.get("data", {})
                        if isinstance(inner_data, dict) and "data" in inner_data and "status" in inner_data:
                            inner_data = inner_data["data"]
                        return LLMResponse(content=json.dumps({"status": "success", "data": inner_data}))
                    else:
                        return LLMResponse(content=json.dumps({"status": "error", "message": result_dict.get("message", "unknown error")}))
                except Exception as e:
                    return LLMResponse(content=json.dumps({"status": "error", "message": f"Tool error: {str(e)} content: {messages[-1].content}"}))
        raise ValueError(f"Unexpected state: sys={system_prompt}, len={len(messages)}")

    mock_nim_adapter.generate_response = mock_generate_response

    client = TestClient(app)
    response = client.post("/api/v1/entry/process", json={"user_request_id": "REQ-1", "student_id": "S-100", "offer_id": "O-100"})
    
    assert response.status_code == 200
    res_data = response.json()
    print("SUCCESS TEST RESULT:", res_data)
    assert res_data["status"] == "success"
    
    with adm_repo._get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT status FROM admission_offers WHERE offer_id = 'O-100'")
        assert c.fetchone()[0] == "Admission Confirmed"
        
    with fp_repo._get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM financial_obligations")
        assert c.fetchone()[0] == 1
        c.execute("SELECT COUNT(*) FROM receipts")
        assert c.fetchone()[0] == 1

def test_business_decline_scenario(app, adm_repo, fp_repo, mock_nim_adapter, monkeypatch):
    """
    Test E2E Flow: Business Decline
    """
    setup_admissions_db(adm_repo)
    import modules.m_admissions.clients.fees_payments_client as fp_client_mod
    tc = TestClient(app)
    class MockHttpxClient:
        def __init__(self, **kwargs): pass
        def __enter__(self): return tc
        def __exit__(self, *args): pass
    monkeypatch.setattr(fp_client_mod.httpx, "Client", MockHttpxClient)
    
    # We patch the FeesPaymentsCapabilities to always fail business validation
    import modules.m_fees_payments.capabilities.fees_payments_caps as fp_caps_mod
    original_validate = fp_caps_mod.FeesPaymentsCapabilities.validate_payment_request
    
    def mock_validate(*args, **kwargs):
        raise fp_caps_mod.ValidationException("Student not eligible for payment")
    
    monkeypatch.setattr(fp_caps_mod.FeesPaymentsCapabilities, "validate_payment_request", mock_validate)

    def mock_generate_response(messages, tools=None, trace_context=None):
        system_prompt = messages[0].content if messages else ""
        if "You are the Admissions Agent" in system_prompt:
            if len(messages) == 2:
                return LLMResponse(tool_calls=[LLMToolCall(id="t-1", type="function", function_name="evaluate_admission_requirements", arguments='{"offer_id": "O-100"}')])
            elif len(messages) == 4:
                return LLMResponse(tool_calls=[LLMToolCall(id="t-2", type="function", function_name="delegate_student_payment", arguments='{"student_id": "S-100", "amount": 500, "currency": "USD", "idempotency_key": "IDEM-1"}')])
            elif len(messages) == 6:
                last_msg = messages[-1].content
                return LLMResponse(content=json.dumps({"status": "error", "message": f"Delegation failed: {last_msg}"}))
        else:
            import re, ast
            match = re.search(r"Request payload:\s*(\{.*?\})", system_prompt, re.DOTALL)
            payload = json.loads(match.group(1)) if match else {}
            print(f"DEBUG mock: parsed payload = {payload}")
            if len(messages) == 2:
                return LLMResponse(tool_calls=[LLMToolCall(id="f-1", type="function", function_name="validate_payment_request", arguments=json.dumps({"request_payload": payload}))])
            elif len(messages) == 6:
                last_msg = messages[-1].content
                if "returned:" in last_msg:
                    last_msg = last_msg.split("returned:", 1)[1].strip()
                result = json.loads(last_msg)
                return LLMResponse(content=json.dumps({"status": "error", "message": result.get("error", "Failed")}))
        raise ValueError(f"Unexpected state: sys={system_prompt}, len={len(messages)}")

    mock_nim_adapter.generate_response = mock_generate_response

    client = TestClient(app)
    response = client.post("/api/v1/entry/process", json={"user_request_id": "REQ-1", "student_id": "S-100", "offer_id": "O-100"})
    
    assert response.status_code == 200
    res_data = response.json()
    print("BUSINESS DECLINE TEST RESULT:", res_data)
    assert res_data["status"] == "error"
    
    # State verification
    with adm_repo._get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT status FROM admission_offers WHERE offer_id = 'O-100'")
        # Adm status remains 'Issued' or 'Offer Accepted' depending on when it failed. In our setup it remains 'Issued' because confirm wasn't called.
        # Actually it remains 'Issued'
        assert c.fetchone()[0] == "Issued"
        
    with fp_repo._get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM financial_obligations")
        assert c.fetchone()[0] == 0
        c.execute("SELECT COUNT(*) FROM receipts")
        assert c.fetchone()[0] == 0

def test_technical_retry_exhaustion(app, adm_repo, fp_repo, mock_nim_adapter, monkeypatch):
    """
    Test E2E Flow: Technical Failure (503) resulting in retry exhaustion
    """
    setup_admissions_db(adm_repo)
    
    call_count = 0
    import modules.m_admissions.clients.fees_payments_client as fp_client_mod
    class FailClient:
        def post(self, *args, **kwargs):
            nonlocal call_count
            call_count += 1
            return httpx.Response(503, request=httpx.Request("POST", "http://test"))
    class MockHttpxClient:
        def __init__(self, **kwargs): pass
        def __enter__(self): return FailClient()
        def __exit__(self, *args): pass
    monkeypatch.setattr(fp_client_mod.httpx, "Client", MockHttpxClient)
    
    def mock_generate_response(messages, tools=None, trace_context=None):
        system_prompt = messages[0].content if messages else ""
        if "You are the Admissions Agent" in system_prompt:
            if len(messages) == 2:
                return LLMResponse(tool_calls=[LLMToolCall(id="t-1", type="function", function_name="evaluate_admission_requirements", arguments='{"offer_id": "O-100"}')])
            elif len(messages) == 4:
                return LLMResponse(tool_calls=[LLMToolCall(id="t-2", type="function", function_name="delegate_student_payment", arguments='{"student_id": "S-100", "amount": 500, "currency": "USD", "idempotency_key": "IDEM-1"}')])
            elif len(messages) == 6:
                return LLMResponse(content=json.dumps({"status": "error", "message": "Failed due to transport error"}))
        raise ValueError(f"Unexpected state: sys={system_prompt}, len={len(messages)}")

    mock_nim_adapter.generate_response = mock_generate_response

    client = TestClient(app)
    response = client.post("/api/v1/entry/process", json={"user_request_id": "REQ-1", "student_id": "S-100", "offer_id": "O-100"})
    
    assert response.status_code == 200
    res_data = response.json()
    print("RETRY TEST RESULT:", res_data)
    assert res_data["status"] == "error"
    assert call_count == 3  # Verified retries
    
    with adm_repo._get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT status FROM admission_offers WHERE offer_id = 'O-100'")
        assert c.fetchone()[0] == "Issued"

def test_lost_response_idempotency(app, adm_repo, fp_repo, mock_nim_adapter, monkeypatch):
    """
    Test E2E Flow: Lost Response / Idempotency
    """
    setup_admissions_db(adm_repo)
    
    call_count = 0
    asgi_transport = httpx.ASGITransport(app=app)
    
    import modules.m_admissions.clients.fees_payments_client as fp_client_mod
    tc = TestClient(app)
    class TimeoutClient:
        def post(self, *args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                tc.post(*args, **kwargs)
                raise httpx.TimeoutException("Network timeout after server execution")
            return tc.post(*args, **kwargs)
    class MockHttpxClient:
        def __init__(self, **kwargs): pass
        def __enter__(self): return TimeoutClient()
        def __exit__(self, *args): pass
    monkeypatch.setattr(fp_client_mod.httpx, "Client", MockHttpxClient)
    
    def mock_generate_response(messages, tools=None, trace_context=None):
        system_prompt = messages[0].content if messages else ""
        if "You are the Admissions Agent" in system_prompt:
            if len(messages) == 2:
                return LLMResponse(tool_calls=[LLMToolCall(id="t-1", type="function", function_name="evaluate_admission_requirements", arguments='{"offer_id": "O-100"}')])
            elif len(messages) == 4:
                return LLMResponse(tool_calls=[LLMToolCall(id="t-2", type="function", function_name="delegate_student_payment", arguments='{"student_id": "S-100", "amount": 500, "currency": "USD", "idempotency_key": "IDEM-LOST"}')])
            elif len(messages) == 6:
                last_msg = messages[-1].content
                print(f"DEBUG mock len=6: last_msg RAW={last_msg}")
                if "returned:" in last_msg:
                    last_msg = last_msg.split("returned:", 1)[1].strip()
                print(f"DEBUG mock len=6: last_msg STRIPPED={last_msg}")
                try:
                    res_dict = json.loads(last_msg)
                except Exception as e:
                    print(f"DEBUG mock len=6: json.loads failed: {e}")
                    import ast
                    try:
                        res_dict = ast.literal_eval(last_msg)
                    except Exception as e:
                        print(f"DEBUG mock len=6: ast failed: {e}")
                        res_dict = {}
                print(f"DEBUG mock len=6: res_dict={res_dict}")
                
                payment_result = res_dict.get("data", {})
                if isinstance(payment_result, str):
                    try:
                        payment_result = json.loads(payment_result)
                    except Exception:
                        pass
                return LLMResponse(tool_calls=[LLMToolCall(id="t-3", type="function", function_name="confirm_admission", arguments=json.dumps({"offer_id": "O-100", "payment_result": payment_result}))])
            elif len(messages) == 8:
                last_msg = messages[-1].content
                if "error" in last_msg.lower():
                    raise ValueError(f"confirm_admission tool failed: {last_msg}")
                return LLMResponse(content=json.dumps({"status": "success", "message": "Admitted"}))
        else:
            import re, ast
            match = re.search(r"Request payload:\s*(\{.*?\})", system_prompt, re.DOTALL)
            payload = json.loads(match.group(1)) if match else {}
            if len(messages) == 2:
                return LLMResponse(tool_calls=[LLMToolCall(id="f-1", type="function", function_name="validate_payment_request", arguments=json.dumps({"request_payload": payload}))])
            elif len(messages) == 4:
                return LLMResponse(tool_calls=[LLMToolCall(id="f-2", type="function", function_name="collect_student_payment", arguments=json.dumps({"request_payload": payload}))])
            elif len(messages) == 6:
                last_msg = messages[-1].content
                if "returned:" in last_msg:
                    last_msg = last_msg.split("returned:", 1)[1].strip()
                result = json.loads(last_msg)
                inner_data = result.get("data", {})
                if isinstance(inner_data, dict) and "data" in inner_data and "status" in inner_data:
                    inner_data = inner_data["data"]
                return LLMResponse(content=json.dumps({"status": "success", "data": inner_data}))
        raise ValueError(f"Unexpected state: sys={system_prompt}, len={len(messages)}")

    mock_nim_adapter.generate_response = mock_generate_response

    client = TestClient(app)
    response = client.post("/api/v1/entry/process", json={"user_request_id": "REQ-1", "student_id": "S-100", "offer_id": "O-100"})
    
    assert response.status_code == 200
    res_data = response.json()
    print("LOST RESPONSE TEST RESULT:", res_data)
    assert res_data["status"] == "success"
    
    assert call_count == 2
    
    # Verify exact exactly-once semantics
    with adm_repo._get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT status FROM admission_offers WHERE offer_id = 'O-100'")
        assert c.fetchone()[0] == "Admission Confirmed"
        
    with fp_repo._get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM financial_obligations")
        assert c.fetchone()[0] == 1
        c.execute("SELECT COUNT(*) FROM receipts")
        assert c.fetchone()[0] == 1
