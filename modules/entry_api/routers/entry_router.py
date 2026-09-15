import uuid
from fastapi import APIRouter, Depends, HTTPException
from modules.entry_api.schemas import EntryRequest, EntryResponse
from modules.m_admissions.agents.admissions_agent import AdmissionsAgent
from xsc_lib.xsc_lib_common.nim_adapter import LLMMessage

router = APIRouter(prefix="/api/v1/entry", tags=["Entry API"])

# Dependency
def get_admissions_agent() -> AdmissionsAgent:
    raise NotImplementedError("Dependency must be overridden in the FastAPI app")

@router.post("/process", response_model=EntryResponse)
def process_entry_request(request: EntryRequest, agent: AdmissionsAgent = Depends(get_admissions_agent)):
    try:
        # Establish internal correlation ID
        correlation_id = str(uuid.uuid4())
        
        # Construct initial context
        initial_msg = LLMMessage(role="user", content=f"Process admission for offer {request.offer_id}")
        
        # Invoke Admissions Agent directly via DI for the POC
        state = agent.invoke({
            "correlation_id": correlation_id,
            "student_id": request.student_id,
            "offer_id": request.offer_id,
            "messages": [initial_msg]
        })
        
        if state.get("error"):
            return EntryResponse(
                status="error",
                correlation_id=correlation_id,
                user_request_id=request.user_request_id,
                message=f"Agent workflow failed: {state['error']}",
                data=state.get("final_result")
            )
            
        final_result = state.get("final_result", {})
        return EntryResponse(
            status=final_result.get("status", "success"),
            correlation_id=correlation_id,
            user_request_id=request.user_request_id,
            message=final_result.get("message"),
            data=final_result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
