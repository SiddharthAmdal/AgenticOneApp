from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class EntryRequest(BaseModel):
    user_request_id: Optional[str] = Field(default=None, description="External user request tracking ID")
    student_id: str = Field(description="The canonical ID of the student")
    offer_id: str = Field(description="The canonical ID of the admission offer to process")

class EntryResponse(BaseModel):
    status: str = Field(description="Workflow status: success or error")
    correlation_id: str = Field(description="Internal workflow correlation ID")
    user_request_id: Optional[str] = Field(default=None, description="Echoed external tracking ID")
    message: Optional[str] = Field(default=None, description="High-level description of outcome")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Structured outcome data")
