"""Схема БД з таблицею staff для управління персоналом."""
import hashlib
from database.connection import DatabaseConnection


def _hash(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()


def init_db():
    db = DatabaseConnection()

    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id        INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name     TEXT    NOT NULL,
            last_name      TEXT    NOT NULL,
            academic_group TEXT    NOT NULL,
            email          TEXT    UNIQUE,
            phone          TEXT,
            created_at     TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            doc_id           INTEGER PRIMARY KEY AUTOINCREMENT,
            title            TEXT    NOT NULL,
            author           TEXT    NOT NULL,
            year             INTEGER NOT NULL,
            isbn             TEXT    UNIQUE,
            total_copies     INTEGER DEFAULT 1,
            available_copies INTEGER DEFAULT 1
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS issuances (
            issue_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(user_id),
            doc_id      INTEGER NOT NULL REFERENCES documents(doc_id),
            issued_at   TEXT    DEFAULT (datetime('now','localtime')),
            due_date    TEXT,
            returned_at TEXT,
            status      TEXT    DEFAULT 'ACTIVE'
        )
    """)

    # due_date для існуючих БД
    try:
        db.execute("ALTER TABLE issuances ADD COLUMN due_date TEXT")
        db.commit()
    except Exception:
        pass

    db.execute("""
        CREATE TABLE IF NOT EXISTS book_requests (
            request_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id        INTEGER NOT NULL REFERENCES documents(doc_id),
            student_name  TEXT    NOT NULL,
            student_group TEXT    NOT NULL,
            message       TEXT,
            created_at    TEXT    DEFAULT (datetime('now','localtime')),
            status        TEXT    DEFAULT 'NEW'
        )
    """)

    # Таблиця персоналу
    db.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            staff_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    NOT NULL UNIQUE,
            password_hash TEXT  NOT NULL,
            role        TEXT    NOT NULL DEFAULT 'librarian',
            full_name   TEXT    NOT NULL,
            email       TEXT,
            is_active   INTEGER DEFAULT 1,
            created_at  TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    # Створюємо дефолтного адміна якщо немає жодного
    row = db.execute("SELECT COUNT(*) FROM staff WHERE role='admin'").fetchone()
    if row[0] == 0:
        db.execute("""
            INSERT INTO staff (username, password_hash, role, full_name, email)
            VALUES (?, ?, 'admin', 'Головний адміністратор', 'admin@library.ua')
        """, ('admin', _hash('admin123')))

    # Додаємо дефолтного бібліотекаря якщо немає
    row2 = db.execute("SELECT COUNT(*) FROM staff WHERE username='librarian'").fetchone()
    if row2[0] == 0:
        db.execute("""
            INSERT INTO staff (username, password_hash, role, full_name, email)
            VALUES (?, ?, 'librarian', 'Бібліотекар', 'lib@library.ua')
        """, ('librarian', _hash('lib123')))

    db.commit()
