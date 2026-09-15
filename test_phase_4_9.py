import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
import uuid
import json

from modules.entry_api.routers.entry_router import router as entry_router, get_admissions_agent as entry_get_adm
from modules.m_admissions.routers.admissions_router import router as adm_router, get_admissions_agent as adm_get_adm
from modules.m_fees_payments.routers.fees_payments_router import router as fees_router, get_fees_payments_agent as fees_get_fees
from xsc_lib.xsc_lib_common.agent_contracts import StudentPaymentRequest, StudentPaymentResult

app = FastAPI()
app.include_router(entry_router)
app.include_router(adm_router)
app.include_router(fees_router)

@app.get("/health")
def health():
    return {"status": "ok"}

# We use simple mock classes for the agents
class MockAdmissionsAgent:
    def invoke(self, payload):
        if payload.get("student_id") == "ERROR":
            return {"error": "Business rule violated", "final_result": {"status": "error"}}
        if payload.get("student_id") == "CRASH":
            raise Exception("Agent crashed")
        return {"final_result": {"status": "success", "message": "Admissions processed", "data": {"offer_id": payload.get("offer_id")}}}

class MockFeesPaymentsAgent:
    def invoke(self, payload):
        req = payload.get("request_payload", {})
        if req.get("StudentID") == "ERROR":
            return {"error": "Payment declined", "final_result": {"status": "error"}}
            
        result_data = {
            "ContractVersion": "1.0",
            "ReceiptID": "P-12345",
            "CorrelationID": payload.get("correlation_id", "test-corr"),
            "IdempotencyKey": req.get("IdempotencyKey", "test-idem"),
            "RequestStatus": "Completed",
            "PaymentStatus": "Success",
            "Timestamp": "2026-09-15T12:00:00Z"
        }
        return {"final_result": {"status": "success", "data": result_data}}

app.dependency_overrides[entry_get_adm] = lambda: MockAdmissionsAgent()
app.dependency_overrides[adm_get_adm] = lambda: MockAdmissionsAgent()
app.dependency_overrides[fees_get_fees] = lambda: MockFeesPaymentsAgent()

client = TestClient(app)

def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

def test_entry_api_valid_request():
    payload = {
        "user_request_id": "REQ-001",
        "student_id": "STU-001",
        "offer_id": "OFF-001"
    }
    resp = client.post("/api/v1/entry/process", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["user_request_id"] == "REQ-001"
    assert "correlation_id" in data
    assert data["message"] == "Admissions processed"

def test_entry_api_malformed_request():
    payload = {
        # missing student_id
        "offer_id": "OFF-001"
    }
    resp = client.post("/api/v1/entry/process", json=payload)
    assert resp.status_code == 422 # Pydantic validation error

def test_admissions_api_valid_request():
    payload = {
        "correlation_id": "corr-001",
        "student_id": "STU-001",
        "offer_id": "OFF-001"
    }
    resp = client.post("/api/v1/internal/admissions/process", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["message"] == "Admissions processed"

def test_admissions_api_agent_crash():
    payload = {
        "correlation_id": "corr-001",
        "student_id": "CRASH",
        "offer_id": "OFF-001"
    }
    resp = client.post("/api/v1/internal/admissions/process", json=payload)
    assert resp.status_code == 500
    assert "Internal agent failure" in resp.json()["detail"]

def test_fees_payments_api_unauthorized():
    # Canonical request
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
    
    payload = json.loads(req.model_dump_json(by_alias=True))
    resp = client.post("/api/v1/internal/fees-payments/process-payment", json=payload)
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Unauthorized caller identity"

def test_fees_payments_api_authorized_valid():
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
    
    headers = {"x-agent-identity": "agent.admissions.primary"}
    payload = json.loads(req.model_dump_json(by_alias=True))
    resp = client.post("/api/v1/internal/fees-payments/process-payment", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["ContractVersion"] == "1.0"
    assert data["ReceiptID"] == "P-12345"
    assert data["PaymentStatus"] == "Success"

def test_fees_payments_api_malformed():
    payload = {
        "ContractVersion": "1.0",
        "RequestingDomain": "Admissions",
        # missing fields
    }
    headers = {"x-agent-identity": "agent.admissions.primary"}
    resp = client.post("/api/v1/internal/fees-payments/process-payment", json=payload, headers=headers)
    assert resp.status_code == 422
