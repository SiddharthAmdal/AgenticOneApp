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
import sqlite3

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
                receipts = self.repo.get_receipts_for_obligation(existing_obligation.obligation_id)
                receipt_id = receipts[0].receipt_id if receipts else "UNKNOWN"
                return StudentPaymentResult(
                    ContractVersion="1.0",
                    CorrelationID=request.correlation_id,
                    IdempotencyKey=request.idempotency_key,
                    RequestStatus=RequestStatus.COMPLETED,
                    PaymentStatus=PaymentStatus.SUCCESS,
                    ReceiptID=receipt_id,
                    Timestamp=datetime.now(timezone.utc)
                )
            elif existing_obligation.status == "Failed":
                return StudentPaymentResult(
                    ContractVersion="1.0",
                    CorrelationID=request.correlation_id,
                    IdempotencyKey=request.idempotency_key,
                    RequestStatus=RequestStatus.COMPLETED,
                    PaymentStatus=PaymentStatus.DECLINED,
                    FailureReason="Previous execution declined",
                    Timestamp=datetime.now(timezone.utc)
                )
            else:
                # Concurrent race or stuck pending.
                # Returning a StateMutationError bubbles as HTTP 500 which triggers a transient retry.
                # The next attempt will likely see "Cleared" or "Failed".
                raise StateMutationError(f"Concurrent idempotency collision for key {request.idempotency_key}")

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
        try:
            self.repo.save_obligation(obligation)
        except sqlite3.IntegrityError:
            # Race condition: someone else inserted the IdempotencyKey between our read and write.
            # Bubbling as StateMutationError triggers a 500 -> retry -> catches existing_obligation above.
            raise StateMutationError(f"Concurrent insert idempotency collision for key {request.idempotency_key}")

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
