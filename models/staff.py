"""Модель співробітника бібліотеки."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class StaffMember:
    staff_id:      int           = 0
    username:      str           = ''
    password_hash: str           = ''
    role:          str           = 'librarian'
    full_name:     str           = ''
    email:         Optional[str] = None
    is_active:     bool          = True
    created_at:    Optional[str] = None

    @property
    def role_display(self) -> str:
        return {'admin': 'Адміністратор', 'librarian': 'Бібліотекар'}.get(self.role, self.role)

    @property
    def status_display(self) -> str:
        return 'Активний' if self.is_active else 'Заблокований'
