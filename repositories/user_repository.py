from typing import List, Optional
from database.connection import DatabaseConnection
from models.entities import User
from repositories.base_repository import IRepository


class UserRepository(IRepository):

    def __init__(self):
        self._db = DatabaseConnection()

    def find_by_id(self, id: int) -> Optional[User]:
        row = self._db.execute(
            "SELECT * FROM users WHERE user_id = ?", (id,)
        ).fetchone()
        return self._row_to_user(row) if row else None

    def find_all(self) -> List[User]:
        rows = self._db.execute("SELECT * FROM users").fetchall()
        return [self._row_to_user(r) for r in rows]

    def save(self, user: User) -> int:
        cur = self._db.execute(
            """INSERT INTO users (first_name, last_name, academic_group, email, phone)
               VALUES (?, ?, ?, ?, ?)""",
            (user.first_name, user.last_name, user.academic_group, user.email, user.phone)
        )
        self._db.commit()
        return cur.lastrowid

    def update(self, user: User) -> bool:
        self._db.execute(
            """UPDATE users
               SET first_name=?, last_name=?, academic_group=?, email=?, phone=?
               WHERE user_id=?""",
            (user.first_name, user.last_name, user.academic_group,
             user.email, user.phone, user.user_id)
        )
        self._db.commit()
        return True

    def delete(self, id: int) -> bool:
        self._db.execute("DELETE FROM users WHERE user_id = ?", (id,))
        self._db.commit()
        return True

    def has_active_issuances(self, user_id: int) -> bool:
        row = self._db.execute(
            "SELECT COUNT(*) FROM issuances WHERE user_id=? AND status='ACTIVE'",
            (user_id,)
        ).fetchone()
        return row[0] > 0

    def search(self, query: str) -> List[User]:
        q = f"%{query}%"
        rows = self._db.execute(
            """SELECT * FROM users
               WHERE first_name LIKE ? OR last_name LIKE ? OR academic_group LIKE ?""",
            (q, q, q)
        ).fetchall()
        return [self._row_to_user(r) for r in rows]

    def _row_to_user(self, row) -> User:
        return User(
            user_id=row['user_id'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            academic_group=row['academic_group'],
            email=row['email'],
            phone=row['phone'],
            created_at=row['created_at'],
        )
