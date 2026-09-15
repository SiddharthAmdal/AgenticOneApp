from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from xsc_lib.xsc_lib_common.nim_adapter import LLMMessage
from modules.m_admissions.agents.admissions_agent import AdmissionsAgent

router = APIRouter(prefix="/api/v1/internal/admissions", tags=["Admissions Agent"])

class AdmissionsAgentRequest(BaseModel):
    correlation_id: str = Field(description="Workflow correlation ID")
    student_id: str = Field(description="The student ID")
    offer_id: str = Field(description="The admission offer ID")

class AdmissionsAgentResponse(BaseModel):
    status: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# We use a dependency to get the agent. In tests, we override this dependency.
def get_admissions_agent() -> AdmissionsAgent:
    raise NotImplementedError("Dependency must be overridden in the FastAPI app")

@router.post("/process", response_model=AdmissionsAgentResponse)
def process_admission(request: AdmissionsAgentRequest, agent: AdmissionsAgent = Depends(get_admissions_agent)):
    try:
        # Construct initial message
        initial_msg = LLMMessage(role="user", content=f"Process admission for offer {request.offer_id}")
        
        # Invoke LangGraph agent
        state = agent.invoke({
            "correlation_id": request.correlation_id,
            "student_id": request.student_id,
            "offer_id": request.offer_id,
            "messages": [initial_msg]
        })
        
        if state.get("error"):
            return AdmissionsAgentResponse(status="error", error=state["error"])
            
        final_result = state.get("final_result", {})
        return AdmissionsAgentResponse(
            status=final_result.get("status", "success"),
            message=final_result.get("message"),
            data=final_result
        )
    except Exception as e:
        # Catch internal agent failure
        raise HTTPException(status_code=500, detail=f"Internal agent failure: {str(e)}")
