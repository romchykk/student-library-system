from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    user_id:        int           = 0
    first_name:     str           = ''
    last_name:      str           = ''
    academic_group: str           = ''
    email:          Optional[str] = None
    phone:          Optional[str] = None
    created_at:     Optional[str] = None

    @property
    def full_name(self): return f"{self.last_name} {self.first_name}"


@dataclass
class Document:
    doc_id:           int           = 0
    title:            str           = ''
    author:           str           = ''
    year:             int           = 2024
    isbn:             Optional[str] = None
    total_copies:     int           = 1
    available_copies: int           = 1

    def accept(self, visitor): visitor.visit(self)

    @property
    def is_available(self): return self.available_copies > 0


@dataclass
class Issuance:
    issue_id:    int           = 0
    user_id:     int           = 0
    doc_id:      int           = 0
    issued_at:   Optional[str] = None
    due_date:    Optional[str] = None
    returned_at: Optional[str] = None
    status:      str           = 'ACTIVE'
    user_name:   Optional[str] = None
    doc_title:   Optional[str] = None

    @property
    def is_overdue(self):
        if self.status != 'ACTIVE' or not self.due_date:
            return False
        from datetime import datetime
        try:
            return datetime.now() > datetime.strptime(self.due_date[:10], '%Y-%m-%d')
        except Exception:
            return False


@dataclass
class BookRequest:
    request_id:    int           = 0
    doc_id:        int           = 0
    student_name:  str           = ''
    student_group: str           = ''
    message:       str           = ''
    created_at:    Optional[str] = None
    status:        str           = 'NEW'
    doc_title:     Optional[str] = None
