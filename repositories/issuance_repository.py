"""Репозиторій видач — підтримує due_date."""
from typing import List, Optional
from database.connection import DatabaseConnection
from models.entities import Issuance
from repositories.base_repository import IRepository


class IssuanceRepository(IRepository):

    def __init__(self):
        self._db = DatabaseConnection()

    def find_by_id(self, id: int) -> Optional[Issuance]:
        row = self._db.execute(
            "SELECT * FROM issuances WHERE issue_id = ?", (id,)
        ).fetchone()
        return self._to_obj(row) if row else None

    def find_all(self) -> List[Issuance]:
        rows = self._db.execute("""
            SELECT i.*, u.first_name||' '||u.last_name AS user_name, d.title AS doc_title
            FROM issuances i
            JOIN users u ON i.user_id=u.user_id
            JOIN documents d ON i.doc_id=d.doc_id
            ORDER BY i.issued_at DESC
        """).fetchall()
        return [self._to_obj(r) for r in rows]

    def find_by_user(self, user_id: int) -> List[Issuance]:
        rows = self._db.execute("""
            SELECT i.*, u.first_name||' '||u.last_name AS user_name, d.title AS doc_title
            FROM issuances i
            JOIN users u ON i.user_id=u.user_id
            JOIN documents d ON i.doc_id=d.doc_id
            WHERE i.user_id=?
            ORDER BY i.issued_at DESC
        """, (user_id,)).fetchall()
        return [self._to_obj(r) for r in rows]

    def find_active_by_doc(self, doc_id: int) -> Optional[Issuance]:
        row = self._db.execute("""
            SELECT i.*, u.first_name||' '||u.last_name AS user_name, d.title AS doc_title
            FROM issuances i
            JOIN users u ON i.user_id=u.user_id
            JOIN documents d ON i.doc_id=d.doc_id
            WHERE i.doc_id=? AND i.status='ACTIVE'
        """, (doc_id,)).fetchone()
        return self._to_obj(row) if row else None

    def count_active_by_user(self, user_id: int) -> int:
        row = self._db.execute(
            "SELECT COUNT(*) FROM issuances WHERE user_id=? AND status='ACTIVE'",
            (user_id,)
        ).fetchone()
        return row[0]

    def save(self, issuance: Issuance) -> int:
        cur = self._db.execute(
            "INSERT INTO issuances (user_id, doc_id, due_date) VALUES (?, ?, ?)",
            (issuance.user_id, issuance.doc_id, issuance.due_date)
        )
        self._db.commit()
        return cur.lastrowid

    def update(self, issuance: Issuance) -> bool:
        self._db.execute(
            "UPDATE issuances SET returned_at=?, status=?, due_date=? WHERE issue_id=?",
            (issuance.returned_at, issuance.status, issuance.due_date, issuance.issue_id)
        )
        self._db.commit()
        return True

    def delete(self, id: int) -> bool:
        self._db.execute("DELETE FROM issuances WHERE issue_id=?", (id,))
        self._db.commit()
        return True

    def _to_obj(self, row) -> Issuance:
        keys = row.keys()
        return Issuance(
            issue_id=row['issue_id'],
            user_id=row['user_id'],
            doc_id=row['doc_id'],
            issued_at=row['issued_at'],
            due_date=row['due_date'] if 'due_date' in keys else None,
            returned_at=row['returned_at'],
            status=row['status'],
            user_name=row['user_name'] if 'user_name' in keys else None,
            doc_title=row['doc_title'] if 'doc_title' in keys else None,
        )
