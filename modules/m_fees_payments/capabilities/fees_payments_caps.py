import uuid
from datetime import datetime, timezone
from typing import Optional

from xsc_lib.xsc_lib_common.xsc_libc_exceptions import ValidationException, StateMutationError
from xsc_lib.xsc_lib_common.agent_contracts import (
    StudentPaymentRequest, 
    StudentPaymentResult, 
    RequestStatus, 
    PaymentStatus
)
from modules.m_fees_payments.repositories.fees_payments_repo import FeesPaymentsRepository
from modules.m_fees_payments.models.financial_obligation import FinancialObligation, Receipt

class FeesPaymentsCapabilities:
    """
    Deterministic capability layer for Fees & Payments.
    Enforces business rules FNP-R01 to FNP-R05.
    """
    def __init__(self, repo: FeesPaymentsRepository):
        self.repo = repo

    def validate_payment_request(self, request: StudentPaymentRequest) -> None:
        """
        FNP-R01, FNP-R02: Deterministically validate a Student Payment Request 
        before financial execution.
        """
        if request.requesting_domain != "Admissions":
            raise ValidationException(f"Unauthorized requesting domain: {request.requesting_domain}")
        if request.amount <= 0:
            raise ValidationException("Payment amount must be greater than zero")
        if not request.idempotency_key:
            raise ValidationException("Idempotency key is required")

    def collect_student_payment(self, request: StudentPaymentRequest) -> StudentPaymentResult:
        """
        FNP-R03, FNP-R04, FNP-R05: Deterministically execute the POC student payment flow.
        """
        self.validate_payment_request(request)

        # FNP-R03: Duplicate Idempotency Key must not result in duplicate collection
        existing_obligation = self.repo.get_obligation_by_idempotency_key(request.idempotency_key)
        if existing_obligation:
            if existing_obligation.status == "Cleared":
                # Note: Full replay behavior belongs to Phase 4.12, but we must return
                # *something* deterministic here to avoid a duplicate charge.
                # Since we don't have full replay infrastructure, we just reject duplicates for now
                # or return a generic success if we can find the receipt. Let's strictly reject 
                # duplicate active attempts as instructed by FNP-R03 to prevent double charging.
                raise StateMutationError(f"Idempotency violation: Payment already cleared for key {request.idempotency_key}")
            else:
                raise StateMutationError(f"Idempotency violation: Payment already processed or pending for key {request.idempotency_key}")

        now_dt = datetime.now(timezone.utc)
        obligation_id = str(uuid.uuid4())
        obligation = FinancialObligation(
            obligation_id=obligation_id,
            student_id=request.student_id,
            amount=float(request.amount),
            currency=request.currency,
            requesting_domain=request.requesting_domain,
            status="Pending",
            idempotency_key=request.idempotency_key,
            created_at=now_dt,
            updated_at=now_dt
        )
        self.repo.save_obligation(obligation)

        # MOCK PAYMENT EXECUTION (FNP-R04)
        # In a real system, this calls a gateway. For POC, it is immediate.
        payment_successful = True # Mocking deterministic success
        
        if payment_successful:
            obligation.status = "Cleared"
            self.repo.update_obligation_status(obligation.obligation_id, "Cleared")
            
            receipt_id = str(uuid.uuid4())
            receipt = Receipt(
                receipt_id=receipt_id,
                obligation_id=obligation.obligation_id,
                status="Success",
                transaction_reference=f"TXN-{receipt_id[:8]}",
                created_at=now_dt
            )
            self.repo.save_receipt(receipt)

            return StudentPaymentResult(
                ContractVersion="1.0",
                CorrelationID=request.correlation_id,
                IdempotencyKey=request.idempotency_key,
                RequestStatus=RequestStatus.COMPLETED,
                PaymentStatus=PaymentStatus.SUCCESS,
                ReceiptID=receipt_id,
                Timestamp=datetime.now(timezone.utc)
            )
        else:
            # Code path if we were mocking a decline
            obligation.status = "Failed"
            self.repo.update_obligation_status(obligation.obligation_id, "Failed")
            return StudentPaymentResult(
                ContractVersion="1.0",
                CorrelationID=request.correlation_id,
                IdempotencyKey=request.idempotency_key,
                RequestStatus=RequestStatus.COMPLETED,
                PaymentStatus=PaymentStatus.DECLINED,
                FailureReason="Gateway mock declined payment",
                Timestamp=datetime.now(timezone.utc)
            )
