from typing import Type, Optional, Any, Dict
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

from xsc_lib.xsc_lib_common.agent_contracts import StudentPaymentResult, StudentPaymentRequest
from xsc_lib.xsc_lib_common.xsc_libc_exceptions import OneAppBaseException
from modules.m_admissions.capabilities.admissions_caps import AdmissionsCapabilities

# Input Schemas
class GetAdmissionOfferInput(BaseModel):
    offer_id: str = Field(description="The unique identifier for the admission offer.")

class EvaluateAdmissionRequirementsInput(BaseModel):
    offer_id: str = Field(description="The unique identifier for the admission offer.")

class ConfirmAdmissionInput(BaseModel):
    offer_id: str = Field(description="The unique identifier for the admission offer.")
    payment_result: Optional[Dict[str, Any]] = Field(default=None, description="The payment result dictionary if a payment was processed.")

class DelegateStudentPaymentInput(BaseModel):
    student_id: str = Field(description="The student identifier.")
    amount: float = Field(description="The monetary amount to request.")
    currency: str = Field(default="USD", description="The currency for the payment.")
    idempotency_key: str = Field(description="A unique idempotency key for this payment request.")

# Base Tool for Admissions to handle exceptions
class AdmissionsBaseTool(BaseTool):
    caps: Any = Field(exclude=True)

    def _format_error(self, e: Exception) -> Dict[str, Any]:
        if isinstance(e, OneAppBaseException):
            return {"status": "error", "error_type": type(e).__name__, "message": str(e)}
        return {"status": "error", "error_type": "UnexpectedError", "message": str(e)}

# Tools
class GetAdmissionOfferTool(AdmissionsBaseTool):
    name: str = "get_admission_offer"
    description: str = "Retrieve an admission offer's current state and details."
    args_schema: Type[BaseModel] = GetAdmissionOfferInput

    def _run(self, offer_id: str) -> Dict[str, Any]:
        try:
            offer = self.caps.get_admission_offer(offer_id)
            return {
                "status": "success",
                "data": {
                    "offer_id": offer.offer_id,
                    "student_id": offer.student_id,
                    "program_id": offer.program_id,
                    "status": offer.status,
                    "payment_required": offer.payment_required,
                    "payment_amount": offer.payment_amount,
                    "currency": offer.currency,
                    "expiration_date": offer.expiration_date.isoformat() if offer.expiration_date and hasattr(offer.expiration_date, "isoformat") else offer.expiration_date
                }
            }
        except Exception as e:
            return self._format_error(e)

class EvaluateAdmissionRequirementsTool(AdmissionsBaseTool):
    name: str = "evaluate_admission_requirements"
    description: str = "Evaluate if an admission offer meets all requirements to proceed to confirmation."
    args_schema: Type[BaseModel] = EvaluateAdmissionRequirementsInput

    def _run(self, offer_id: str) -> Dict[str, Any]:
        try:
            result = self.caps.evaluate_admission_requirements(offer_id)
            return {"status": "success", "data": result}
        except Exception as e:
            return self._format_error(e)

class DelegateStudentPaymentTool(AdmissionsBaseTool):
    name: str = "delegate_student_payment"
    description: str = "Construct and delegate a student payment request to the Fees & Payments domain."
    args_schema: Type[BaseModel] = DelegateStudentPaymentInput

    def _run(self, student_id: str, amount: float, idempotency_key: str, currency: str = "USD", run_manager: Optional[Any] = None) -> Dict[str, Any]:
        try:
            from datetime import datetime, timezone
            from modules.m_admissions.clients.fees_payments_client import FeesPaymentsClient
            from xsc_lib.xsc_lib_common.xsc_libc_exceptions import ConfigurationError

            correlation_id = run_manager.metadata.get("correlation_id") if run_manager and run_manager.metadata else None
            if not correlation_id:
                raise ConfigurationError("correlation_id is missing from tool execution context.")

            # Construct the canonical inter-domain request
            request = StudentPaymentRequest(
                contract_version="1.0",
                requesting_domain="Admissions",
                requesting_agent="agent.admissions.primary",
                correlation_id=correlation_id,
                idempotency_key=idempotency_key,
                student_id=student_id,
                obligation_type="AdmissionFee",
                amount=amount,
                currency=currency,
                business_reason="Mandatory admission confirmation fee",
                timestamp=datetime.now(timezone.utc)
            )

            # Delegate via REST client
            client = FeesPaymentsClient()
            result = client.delegate_payment(request)
            return {
                "status": "success",
                "data": result.model_dump(mode='json', by_alias=True)
            }
        except Exception as e:
            return self._format_error(e)

class ConfirmAdmissionTool(AdmissionsBaseTool):
    name: str = "confirm_admission"
    description: str = "Confirm an admission offer, mutating its state if all rules and payments are satisfied."
    args_schema: Type[BaseModel] = ConfirmAdmissionInput

    def _run(self, offer_id: str, payment_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            parsed_result = None
            if payment_result:
                parsed_result = StudentPaymentResult(**payment_result)
            
            self.caps.confirm_admission(offer_id, parsed_result)
            return {"status": "success", "message": f"Admission for {offer_id} successfully confirmed."}
        except Exception as e:
            return self._format_error(e)

def get_admissions_agent_tools(caps: AdmissionsCapabilities) -> list[BaseTool]:
    """Returns the authorized list of tools for the Admissions Agent."""
    return [
        GetAdmissionOfferTool(caps=caps),
        EvaluateAdmissionRequirementsTool(caps=caps),
        DelegateStudentPaymentTool(caps=caps),
        ConfirmAdmissionTool(caps=caps)
    ]
