import sqlite3
import os
from datetime import datetime
from typing import Optional
from modules.m_admissions.models.admission_offer import AdmissionOffer
from xsc_lib.xsc_lib_common.xsc_libc_config import AppConfig
from xsc_lib.xsc_lib_common.xsc_libc_exceptions import EntityNotFoundError, StateMutationError

class AdmissionsRepository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or AppConfig.get("ADMISSIONS_DB_PATH", "admissions.db")
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admission_offers (
                    offer_id TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL,
                    program_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    expiration_date TEXT NOT NULL,
                    payment_required BOOLEAN NOT NULL,
                    payment_amount REAL,
                    currency TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def get_offer(self, offer_id: str) -> Optional[AdmissionOffer]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admission_offers WHERE offer_id = ?", (offer_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return AdmissionOffer(
                offer_id=row[0],
                student_id=row[1],
                program_id=row[2],
                status=row[3],
                expiration_date=datetime.fromisoformat(row[4]),
                payment_required=bool(row[5]),
                payment_amount=row[6],
                currency=row[7],
                created_at=datetime.fromisoformat(row[8]),
                updated_at=datetime.fromisoformat(row[9])
            )

    def save_offer(self, offer: AdmissionOffer):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO admission_offers (offer_id, student_id, program_id, status, expiration_date, payment_required, payment_amount, currency, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(offer_id) DO UPDATE SET
                    status=excluded.status,
                    updated_at=excluded.updated_at
            """, (
                offer.offer_id, offer.student_id, offer.program_id, offer.status, 
                offer.expiration_date.isoformat(), int(offer.payment_required), 
                offer.payment_amount, offer.currency, 
                offer.created_at.isoformat(), offer.updated_at.isoformat()
            ))
            conn.commit()

    def update_offer_status(self, offer_id: str, new_status: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE admission_offers SET status = ?, updated_at = ? WHERE offer_id = ?", (new_status, datetime.utcnow().isoformat(), offer_id))
            if cursor.rowcount == 0:
                raise EntityNotFoundError(f"Offer {offer_id} not found")
            conn.commit()
