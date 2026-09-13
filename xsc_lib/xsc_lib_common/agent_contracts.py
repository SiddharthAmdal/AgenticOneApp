from datetime import datetime
from decimal import Decimal
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, condecimal, constr

class RequestStatus(str, Enum):
    COMPLETED = "Completed"
    INVALID = "Invalid"
    FAILED = "Failed"

class PaymentStatus(str, Enum):
    SUCCESS = "Success"
    DECLINED = "Declined"
    PENDING = "Pending"
    NOT_ATTEMPTED = "NotAttempted"

class StudentPaymentRequest(BaseModel):
    """
    Contract representing a request from Admissions to Fees & Payments
    to execute a financial obligation.
    """
    contract_version: str = Field(default="1.0", alias="ContractVersion", pattern=r"^1\.0$")
    requesting_domain: str = Field(alias="RequestingDomain")
    requesting_agent: str = Field(alias="RequestingAgent")
    correlation_id: str = Field(alias="CorrelationID", min_length=1)
    idempotency_key: str = Field(alias="IdempotencyKey", min_length=1)
    student_id: str = Field(alias="StudentID")
    obligation_type: str = Field(alias="ObligationType")
    amount: Decimal = Field(alias="Amount", decimal_places=2)
    currency: str = Field(alias="Currency")
    business_reason: Optional[str] = Field(default=None, alias="BusinessReason")
    timestamp: datetime = Field(alias="Timestamp")

    class Config:
        populate_by_name = True
        extra = "ignore"
        json_encoders = {
            Decimal: lambda v: str(v)
        }

class StudentPaymentResult(BaseModel):
    """
    Contract representing the result of a StudentPaymentRequest returned
    from Fees & Payments to Admissions.
    """
    contract_version: str = Field(default="1.0", alias="ContractVersion", pattern=r"^1\.0$")
    correlation_id: str = Field(alias="CorrelationID", min_length=1)
    idempotency_key: str = Field(alias="IdempotencyKey", min_length=1)
    request_status: RequestStatus = Field(alias="RequestStatus")
    payment_status: PaymentStatus = Field(alias="PaymentStatus")
    receipt_id: Optional[str] = Field(default=None, alias="ReceiptID")
    failure_reason: Optional[str] = Field(default=None, alias="FailureReason")
    timestamp: datetime = Field(alias="Timestamp")

    class Config:
        populate_by_name = True
        extra = "ignore"
