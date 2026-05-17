"""Репозиторій запитів студентів на книги."""
from typing import List
from database.connection import DatabaseConnection
from models.entities import BookRequest


class BookRequestRepository:

    def __init__(self):
        self._db = DatabaseConnection()

    def save(self, req: BookRequest) -> int:
        cur = self._db.execute(
            """INSERT INTO book_requests (doc_id, student_name, student_group, message)
               VALUES (?, ?, ?, ?)""",
            (req.doc_id, req.student_name, req.student_group, req.message)
        )
        self._db.commit()
        return cur.lastrowid

    def find_all(self) -> List[BookRequest]:
        rows = self._db.execute("""
            SELECT r.*, d.title AS doc_title
            FROM book_requests r
            LEFT JOIN documents d ON r.doc_id = d.doc_id
            ORDER BY r.created_at DESC
        """).fetchall()
        return [self._to_obj(r) for r in rows]

    def find_new(self) -> List[BookRequest]:
        rows = self._db.execute("""
            SELECT r.*, d.title AS doc_title
            FROM book_requests r
            LEFT JOIN documents d ON r.doc_id = d.doc_id
            WHERE r.status = 'NEW'
            ORDER BY r.created_at DESC
        """).fetchall()
        return [self._to_obj(r) for r in rows]

    def mark_processed(self, request_id: int):
        self._db.execute(
            "UPDATE book_requests SET status='PROCESSED' WHERE request_id=?",
            (request_id,)
        )
        self._db.commit()

    def count_new(self) -> int:
        row = self._db.execute(
            "SELECT COUNT(*) FROM book_requests WHERE status='NEW'"
        ).fetchone()
        return row[0]

    def _to_obj(self, row) -> BookRequest:
        keys = row.keys()
        return BookRequest(
            request_id=row['request_id'],
            doc_id=row['doc_id'],
            student_name=row['student_name'],
            student_group=row['student_group'],
            message=row['message'] or '',
            created_at=row['created_at'],
            status=row['status'],
            doc_title=row['doc_title'] if 'doc_title' in keys else None,
        )
