"""Репозиторій персоналу."""
import hashlib
from typing import List, Optional
from database.connection import DatabaseConnection
from models.staff import StaffMember


def _hash(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()


class StaffRepository:

    def __init__(self):
        self._db = DatabaseConnection()

    def find_by_credentials(self, username: str, password: str) -> Optional[StaffMember]:
        """Знайти співробітника за логіном і паролем."""
        row = self._db.execute(
            "SELECT * FROM staff WHERE username=? AND password_hash=? AND is_active=1",
            (username, _hash(password))
        ).fetchone()
        return self._to_obj(row) if row else None

    def find_all(self) -> List[StaffMember]:
        rows = self._db.execute(
            "SELECT * FROM staff ORDER BY role, full_name"
        ).fetchall()
        return [self._to_obj(r) for r in rows]

    def find_by_id(self, staff_id: int) -> Optional[StaffMember]:
        row = self._db.execute(
            "SELECT * FROM staff WHERE staff_id=?", (staff_id,)
        ).fetchone()
        return self._to_obj(row) if row else None

    def username_exists(self, username: str, exclude_id: int = 0) -> bool:
        row = self._db.execute(
            "SELECT COUNT(*) FROM staff WHERE username=? AND staff_id!=?",
            (username, exclude_id)
        ).fetchone()
        return row[0] > 0

    def save(self, member: StaffMember, password: str) -> int:
        cur = self._db.execute(
            """INSERT INTO staff (username, password_hash, role, full_name, email, is_active)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (member.username, _hash(password), member.role,
             member.full_name, member.email, 1 if member.is_active else 0)
        )
        self._db.commit()
        return cur.lastrowid

    def update(self, member: StaffMember) -> bool:
        self._db.execute(
            """UPDATE staff SET role=?, full_name=?, email=?, is_active=?
               WHERE staff_id=?""",
            (member.role, member.full_name, member.email,
             1 if member.is_active else 0, member.staff_id)
        )
        self._db.commit()
        return True

    def change_password(self, staff_id: int, new_password: str) -> bool:
        self._db.execute(
            "UPDATE staff SET password_hash=? WHERE staff_id=?",
            (_hash(new_password), staff_id)
        )
        self._db.commit()
        return True

    def delete(self, staff_id: int) -> bool:
        # Перевіряємо щоб не видалити останнього адміна
        row = self._db.execute(
            "SELECT role FROM staff WHERE staff_id=?", (staff_id,)
        ).fetchone()
        if row and row['role'] == 'admin':
            count = self._db.execute(
                "SELECT COUNT(*) FROM staff WHERE role='admin' AND is_active=1"
            ).fetchone()[0]
            if count <= 1:
                raise ValueError("Неможливо видалити останнього адміністратора!")
        self._db.execute("DELETE FROM staff WHERE staff_id=?", (staff_id,))
        self._db.commit()
        return True

    def _to_obj(self, row) -> StaffMember:
        return StaffMember(
            staff_id=row['staff_id'],
            username=row['username'],
            password_hash=row['password_hash'],
            role=row['role'],
            full_name=row['full_name'],
            email=row['email'],
            is_active=bool(row['is_active']),
            created_at=row['created_at'],
        )
