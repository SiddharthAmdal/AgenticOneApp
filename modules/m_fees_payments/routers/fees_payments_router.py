from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from xsc_lib.xsc_lib_common.agent_contracts import StudentPaymentRequest, StudentPaymentResult
from xsc_lib.xsc_lib_common.nim_adapter import LLMMessage
from modules.m_fees_payments.agents.fees_payments_agent import FeesPaymentsAgent
from pydantic import ValidationError

router = APIRouter(prefix="/api/v1/internal/fees-payments", tags=["Fees & Payments Agent"])

# Dependency
def get_fees_payments_agent() -> FeesPaymentsAgent:
    raise NotImplementedError("Dependency must be overridden in the FastAPI app")

@router.post("/process-payment", response_model=StudentPaymentResult)
def process_payment(
    request: StudentPaymentRequest, 
    x_agent_identity: Optional[str] = Header(None, description="Identity of calling agent"),
    agent: FeesPaymentsAgent = Depends(get_fees_payments_agent)
):
    try:
        # Caller identity check logic (POC trust-based)
        if not x_agent_identity or x_agent_identity != "agent.admissions.primary":
            raise HTTPException(status_code=403, detail="Unauthorized caller identity")
            
        # The Fees & Payments Agent receives the raw contract as dict payload
        state = agent.invoke({
            "correlation_id": request.correlation_id,
            "request_payload": request.model_dump(mode='json', by_alias=True),
            "messages": [LLMMessage(role="user", content="Process payment request")]
        })
        
        if state.get("error"):
            raise HTTPException(status_code=400, detail=state["error"])
            
        final_result = state.get("final_result", {})
        
        if final_result.get("status") == "error":
             raise HTTPException(status_code=400, detail=final_result.get("message", "Payment processing failed"))
             
        # Extract the structured data returned by capability
        payment_data = final_result.get("data", {})
        
        try:
            # Validate output matches the canonical contract
            result_contract = StudentPaymentResult(**payment_data)
            return result_contract
        except ValidationError as ve:
            # Contract violation on return
            raise HTTPException(status_code=500, detail=f"Invalid payment result structure: {ve.errors()}")
            
    except HTTPException:
        raise
    except Exception as e:
        # Catch internal technical errors
        raise HTTPException(status_code=500, detail="Internal server error")
