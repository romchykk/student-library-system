from typing import List, Optional
from database.connection import DatabaseConnection
from models.entities import Document
from repositories.base_repository import IRepository


class DocumentRepository(IRepository):

    def __init__(self):
        self._db = DatabaseConnection()

    def find_by_id(self, id: int) -> Optional[Document]:
        row = self._db.execute(
            "SELECT * FROM documents WHERE doc_id = ?", (id,)
        ).fetchone()
        return self._row_to_doc(row) if row else None

    def find_all(self) -> List[Document]:
        rows = self._db.execute("SELECT * FROM documents").fetchall()
        return [self._row_to_doc(r) for r in rows]

    def save(self, doc: Document) -> int:
        cur = self._db.execute(
            """INSERT INTO documents (title, author, year, isbn, total_copies, available_copies)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (doc.title, doc.author, doc.year, doc.isbn,
             doc.total_copies, doc.total_copies)
        )
        self._db.commit()
        return cur.lastrowid

    def update(self, doc: Document) -> bool:
        self._db.execute(
            """UPDATE documents
               SET title=?, author=?, year=?, isbn=?, total_copies=?, available_copies=?
               WHERE doc_id=?""",
            (doc.title, doc.author, doc.year, doc.isbn,
             doc.total_copies, doc.available_copies, doc.doc_id)
        )
        self._db.commit()
        return True

    def delete(self, id: int) -> bool:
        self._db.execute("DELETE FROM documents WHERE doc_id = ?", (id,))
        self._db.commit()
        return True

    def has_active_issuances(self, doc_id: int) -> bool:
        row = self._db.execute(
            "SELECT COUNT(*) FROM issuances WHERE doc_id=? AND status='ACTIVE'",
            (doc_id,)
        ).fetchone()
        return row[0] > 0

    def decrement_available(self, doc_id: int):
        self._db.execute(
            "UPDATE documents SET available_copies = available_copies - 1 WHERE doc_id = ?",
            (doc_id,)
        )
        self._db.commit()

    def increment_available(self, doc_id: int):
        self._db.execute(
            "UPDATE documents SET available_copies = available_copies + 1 WHERE doc_id = ?",
            (doc_id,)
        )
        self._db.commit()

    def search(self, query: str) -> List[Document]:
        q = f"%{query}%"
        rows = self._db.execute(
            "SELECT * FROM documents WHERE title LIKE ? OR author LIKE ?",
            (q, q)
        ).fetchall()
        return [self._row_to_doc(r) for r in rows]

    def _row_to_doc(self, row) -> Document:
        return Document(
            doc_id=row['doc_id'],
            title=row['title'],
            author=row['author'],
            year=row['year'],
            isbn=row['isbn'],
            total_copies=row['total_copies'],
            available_copies=row['available_copies'],
        )
