from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class FinancialObligation:
    obligation_id: str
    student_id: str
    amount: float
    currency: str
    requesting_domain: str
    status: str  # "Pending", "Cleared", "Failed"
    idempotency_key: str
    created_at: datetime
    updated_at: datetime

@dataclass
class Receipt:
    receipt_id: str
    obligation_id: str
    status: str # "Success", "Failed"
    transaction_reference: Optional[str]
    created_at: datetime
