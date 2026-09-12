from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class AdmissionOffer:
    offer_id: str
    student_id: str
    program_id: str
    status: str  # "Issued", "Offer Accepted", "Admission Confirmed"
    expiration_date: datetime
    payment_required: bool
    payment_amount: float
    currency: str
    created_at: datetime
    updated_at: datetime
