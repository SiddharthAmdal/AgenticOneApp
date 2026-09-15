import sqlite3
import os
from datetime import datetime
from typing import Optional
from modules.m_fees_payments.models.financial_obligation import FinancialObligation, Receipt
from xsc_lib.xsc_lib_common.xsc_libc_config import AppConfig
from xsc_lib.xsc_lib_common.xsc_libc_exceptions import EntityNotFoundError

class FeesPaymentsRepository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or AppConfig.get("FEES_PAYMENTS_DB_PATH", "fees_payments.db")
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS financial_obligations (
                    obligation_id TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT NOT NULL,
                    requesting_domain TEXT NOT NULL,
                    status TEXT NOT NULL,
                    idempotency_key TEXT UNIQUE NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS receipts (
                    receipt_id TEXT PRIMARY KEY,
                    obligation_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    transaction_reference TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (obligation_id) REFERENCES financial_obligations (obligation_id)
                )
            """)
            conn.commit()

    def get_obligation_by_idempotency_key(self, idempotency_key: str) -> Optional[FinancialObligation]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM financial_obligations WHERE idempotency_key = ?", (idempotency_key,))
            row = cursor.fetchone()
            if not row:
                return None
            return FinancialObligation(
                obligation_id=row[0],
                student_id=row[1],
                amount=row[2],
                currency=row[3],
                requesting_domain=row[4],
                status=row[5],
                idempotency_key=row[6],
                created_at=datetime.fromisoformat(row[7]),
                updated_at=datetime.fromisoformat(row[8])
            )

    def save_obligation(self, obligation: FinancialObligation):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO financial_obligations (obligation_id, student_id, amount, currency, requesting_domain, status, idempotency_key, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(obligation_id) DO UPDATE SET
                    status=excluded.status,
                    updated_at=excluded.updated_at
            """, (
                obligation.obligation_id, obligation.student_id, obligation.amount, 
                obligation.currency, obligation.requesting_domain, obligation.status, 
                obligation.idempotency_key, obligation.created_at.isoformat(), 
                obligation.updated_at.isoformat()
            ))
            conn.commit()

    def save_receipt(self, receipt: Receipt):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO receipts (receipt_id, obligation_id, status, transaction_reference, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                receipt.receipt_id, receipt.obligation_id, receipt.status, 
                receipt.transaction_reference, receipt.created_at.isoformat()
            ))
            conn.commit()
            
    def get_receipt(self, receipt_id: str) -> Optional[Receipt]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM receipts WHERE receipt_id = ?", (receipt_id,))
            row = cursor.fetchone()
            if row:
                return Receipt(
                    receipt_id=row[0],
                    obligation_id=row[1],
                    status=row[2],
                    transaction_reference=row[3],
                    created_at=datetime.fromisoformat(row[4]) if row[4] else None
                )
            return None

    def update_obligation_status(self, obligation_id: str, new_status: str):
        from datetime import timezone
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE financial_obligations SET status = ?, updated_at = ? WHERE obligation_id = ?",
                           (new_status, datetime.now(timezone.utc).isoformat(), obligation_id))
            conn.commit()

    def get_receipts_for_obligation(self, obligation_id: str) -> list[Receipt]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM receipts WHERE obligation_id = ?", (obligation_id,))
            rows = cursor.fetchall()
            receipts = []
            for row in rows:
                receipts.append(Receipt(
                    receipt_id=row[0],
                    obligation_id=row[1],
                    status=row[2],
                    transaction_reference=row[3],
                    created_at=datetime.fromisoformat(row[4]) if row[4] else None
                ))
            return receipts
