from datetime import datetime, timezone
from typing import Optional, Dict, Any

from xsc_lib.xsc_lib_common.xsc_libc_exceptions import ValidationException, StateMutationError, EntityNotFoundError
from xsc_lib.xsc_lib_common.agent_contracts import StudentPaymentResult, PaymentStatus

from modules.m_admissions.repositories.admissions_repo import AdmissionsRepository
from modules.m_admissions.models.admission_offer import AdmissionOffer

class AdmissionsCapabilities:
    """
    Deterministic capability layer for Admissions.
    Enforces business rules ADM-R01 to ADM-R05.
    """
    def __init__(self, repo: AdmissionsRepository):
        self.repo = repo

    def get_admission_offer(self, offer_id: str) -> AdmissionOffer:
        """
        Deterministically retrieve an admission offer from the Admissions-owned persistence store.
        """
        offer = self.repo.get_offer(offer_id)
        if not offer:
            raise EntityNotFoundError(f"Admission offer not found: {offer_id}")
        return offer

    def evaluate_admission_requirements(self, offer_id: str) -> Dict[str, Any]:
        """
        ADM-R02: Evaluate the admission requirements relevant to the POC.
        Returns a structured deterministic result indicating if payment is required.
        """
        offer = self.get_admission_offer(offer_id)
        
        # Check if the offer is expired
        is_expired = False
        if offer.expiration_date:
            # Assuming expiration_date is a datetime object or parseable ISO string (from SQLite)
            if isinstance(offer.expiration_date, str):
                try:
                    exp_date = datetime.fromisoformat(offer.expiration_date.replace("Z", "+00:00"))
                except ValueError:
                    exp_date = None
            else:
                exp_date = offer.expiration_date
                
            if exp_date and datetime.now(timezone.utc) > exp_date:
                is_expired = True
                
        return {
            "offer_id": offer.offer_id,
            "status": offer.status,
            "payment_required": offer.payment_required,
            "is_expired": is_expired,
            "can_proceed": offer.status in ["Issued", "Offer Accepted"] and not is_expired
        }

    def confirm_admission(self, offer_id: str, payment_result: Optional[StudentPaymentResult] = None) -> AdmissionOffer:
        """
        ADM-R01, ADM-R03, ADM-R04, ADM-R05: Perform the authoritative Admission Confirmation state mutation.
        """
        offer = self.get_admission_offer(offer_id)
        evaluation = self.evaluate_admission_requirements(offer_id)
        
        # ADM-R01: Offer must be valid
        if not evaluation["can_proceed"]:
            raise StateMutationError(f"Offer is not eligible for confirmation. Status: {offer.status}, Expired: {evaluation['is_expired']}")

        # ADM-R03: Mandatory payment blocks Admission Confirmed
        if offer.payment_required:
            if not payment_result:
                raise StateMutationError("Payment is mandatory but no payment result was provided")
            
            if payment_result.payment_status != PaymentStatus.SUCCESS:
                # ADM-R04: Payment failure leaves Offer Accepted / Pending Payment
                if offer.status == "Issued":
                    offer.status = "Offer Accepted"
                    self.repo.update_offer_status(offer_id, "Offer Accepted")
                raise StateMutationError(f"Cannot confirm admission: Payment did not succeed (Status: {payment_result.payment_status})")
        
        # All checks passed, perform the authoritative state transition
        offer.status = "Admission Confirmed"
        self.repo.update_offer_status(offer_id, "Admission Confirmed")
        
        return offer
