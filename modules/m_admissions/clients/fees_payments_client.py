import json
import httpx
from pydantic import ValidationError
from typing import Optional
from xsc_lib.xsc_lib_common.agent_contracts import StudentPaymentRequest, StudentPaymentResult
from xsc_lib.xsc_lib_common.xsc_libc_config import AppConfig
from xsc_lib.xsc_lib_common.xsc_libc_exceptions import OneAppBaseException

class DelegationError(OneAppBaseException):
    """Raised when an inter-domain delegation fails at the transport or contract level."""
    pass

class FeesPaymentsClient:
    """
    HTTP client for delegating payment requests to the Fees & Payments domain.
    """
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or AppConfig.get_fees_payments_service_url()
        self.endpoint = f"{self.base_url.rstrip('/')}/api/v1/internal/fees-payments/process-payment"

    def delegate_payment(self, request: StudentPaymentRequest) -> StudentPaymentResult:
        """
        Sends a StudentPaymentRequest to the Fees & Payments domain via HTTP.
        """
        payload = json.loads(request.model_dump_json(by_alias=True))
        headers = {
            "x-agent-identity": "agent.admissions.primary",
            "Content-Type": "application/json"
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.post(self.endpoint, json=payload, headers=headers)
        except httpx.RequestError as exc:
            raise DelegationError(f"HTTP transport error while delegating to Fees & Payments: {str(exc)}") from exc

        if response.status_code != 200:
            try:
                error_detail = response.json().get("detail", response.text)
            except Exception:
                error_detail = response.text
            raise DelegationError(f"Fees & Payments rejected request (HTTP {response.status_code}): {error_detail}")

        try:
            result_data = response.json()
            return StudentPaymentResult(**result_data)
        except ValidationError as ve:
            raise DelegationError(f"Malformed response contract from Fees & Payments: {ve.errors()}")
        except json.JSONDecodeError:
            raise DelegationError("Non-JSON response received from Fees & Payments on success status.")
