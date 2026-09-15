from typing import Type, Any, Dict
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

from xsc_lib.xsc_lib_common.agent_contracts import StudentPaymentRequest
from xsc_lib.xsc_lib_common.xsc_libc_exceptions import OneAppBaseException
from modules.m_fees_payments.capabilities.fees_payments_caps import FeesPaymentsCapabilities

# Input Schemas
class PaymentRequestInput(BaseModel):
    request_payload: Dict[str, Any] = Field(description="The canonical StudentPaymentRequest JSON payload dictionary.")

class FeesPaymentsBaseTool(BaseTool):
    caps: Any = Field(exclude=True)

    def _format_error(self, e: Exception) -> Dict[str, Any]:
        if isinstance(e, OneAppBaseException):
            return {"status": "error", "error_type": type(e).__name__, "message": str(e)}
        return {"status": "error", "error_type": "UnexpectedError", "message": str(e)}

class ValidatePaymentRequestTool(FeesPaymentsBaseTool):
    name: str = "validate_payment_request"
    description: str = "Deterministically validate a student payment request."
    args_schema: Type[BaseModel] = PaymentRequestInput

    def _run(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            request_obj = StudentPaymentRequest(**request_payload)
            self.caps.validate_payment_request(request_obj)
            return {"status": "success", "message": "Payment request is valid."}
        except Exception as e:
            return self._format_error(e)

class CollectStudentPaymentTool(FeesPaymentsBaseTool):
    name: str = "collect_student_payment"
    description: str = "Deterministically collect a student payment for a valid request and return the canonical result."
    args_schema: Type[BaseModel] = PaymentRequestInput

    def _run(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            request_obj = StudentPaymentRequest(**request_payload)
            result = self.caps.collect_student_payment(request_obj)
            return {
                "status": "success",
                "data": result.model_dump(mode='json', by_alias=True)
            }
        except Exception as e:
            return self._format_error(e)

def get_fees_payments_agent_tools(caps: FeesPaymentsCapabilities) -> list[BaseTool]:
    """Returns the authorized list of tools for the Fees & Payments Agent."""
    return [
        ValidatePaymentRequestTool(caps=caps),
        CollectStudentPaymentTool(caps=caps)
    ]
