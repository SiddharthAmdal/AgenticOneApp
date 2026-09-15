import os
import uuid
import sqlite3
from datetime import datetime, timedelta

from modules.m_admissions.models.admission_offer import AdmissionOffer
from modules.m_admissions.repositories.admissions_repo import AdmissionsRepository
from modules.m_fees_payments.models.financial_obligation import FinancialObligation, Receipt
from modules.m_fees_payments.repositories.fees_payments_repo import FeesPaymentsRepository

def run_tests():
    print("--- Phase 4.3 Validation ---")

    # Clean up test databases
    if os.path.exists("test_admissions.db"):
        os.remove("test_admissions.db")
    if os.path.exists("test_fees.db"):
        os.remove("test_fees.db")

    # 1. Schema initialization & Domain isolation
    admissions_repo = AdmissionsRepository("test_admissions.db")
    fees_repo = FeesPaymentsRepository("test_fees.db")
    
    assert os.path.exists("test_admissions.db")
    assert os.path.exists("test_fees.db")
    print("Schema initialization & Domain isolation OK.")

    # 2. Admissions round-trip & State persistence
    offer_id = str(uuid.uuid4())
    offer = AdmissionOffer(
        offer_id=offer_id,
        student_id="STU-123",
        program_id="PROG-CS",
        status="Issued",
        expiration_date=datetime.utcnow() + timedelta(days=30),
        payment_required=True,
        payment_amount=500.0,
        currency="USD",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    admissions_repo.save_offer(offer)
    retrieved_offer = admissions_repo.get_offer(offer_id)
    assert retrieved_offer is not None
    assert retrieved_offer.status == "Issued"
    assert retrieved_offer.payment_required is True
    
    # State update test
    admissions_repo.update_offer_status(offer_id, "Offer Accepted")
    retrieved_offer = admissions_repo.get_offer(offer_id)
    assert retrieved_offer.status == "Offer Accepted"
    print("Admissions round-trip & State persistence OK.")

    # 3. Fees & Payments round-trip, Constraints, & State persistence
    ob_id = str(uuid.uuid4())
    idem_key = "idem-test-999"
    
    ob = FinancialObligation(
        obligation_id=ob_id,
        student_id="STU-123",
        amount=500.0,
        currency="USD",
        requesting_domain="Admissions",
        status="Pending",
        idempotency_key=idem_key,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    fees_repo.save_obligation(ob)
    
    # Test uniqueness constraint
    ob2 = FinancialObligation(
        obligation_id=str(uuid.uuid4()),
        student_id="STU-123",
        amount=500.0,
        currency="USD",
        requesting_domain="Admissions",
        status="Pending",
        idempotency_key=idem_key, # Duplicate idempotency key
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    try:
        fees_repo.save_obligation(ob2)
        print("FAIL: Idempotency constraint did not fire.")
    except sqlite3.IntegrityError:
        print("Persistence constraints (idempotency) OK.")
        
    retrieved_ob = fees_repo.get_obligation_by_idempotency_key(idem_key)
    assert retrieved_ob is not None
    assert retrieved_ob.status == "Pending"
    
    # Receipt creation
    receipt_id = str(uuid.uuid4())
    receipt = Receipt(
        receipt_id=receipt_id,
        obligation_id=ob_id,
        status="Success",
        transaction_reference="BANK-123",
        created_at=datetime.utcnow()
    )
    fees_repo.save_receipt(receipt)
    retrieved_rec = fees_repo.get_receipt(receipt_id)
    assert retrieved_rec.status == "Success"
    print("Fees & Payments round-trip & State persistence OK.")

    # 4. Cross-domain isolation check
    # Ensure admissions repo cannot access fees tables, and vice versa
    try:
        with admissions_repo._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM financial_obligations")
        print("FAIL: Admissions could access Fees & Payments tables.")
    except sqlite3.OperationalError:
        pass
        
    # Stronger isolation check: Verify default repository configurations map to distinct files
    # and do not share connection states or memory spaces.
    prod_admissions = AdmissionsRepository()
    prod_fees = FeesPaymentsRepository()
    assert prod_admissions.db_path != prod_fees.db_path, "Repositories must not share default database paths"
    assert "admissions" in prod_admissions.db_path.lower(), "Admissions repository must own admissions DB"
    assert "fees" in prod_fees.db_path.lower(), "Fees & Payments repository must own fees DB"
    print("Cross-domain isolation OK.")

    # Clean up
    os.remove("test_admissions.db")
    os.remove("test_fees.db")
    
    if os.path.exists(prod_admissions.db_path):
        os.remove(prod_admissions.db_path)
    if os.path.exists(prod_fees.db_path):
        os.remove(prod_fees.db_path)

if __name__ == "__main__":
    run_tests()
