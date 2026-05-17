"""
ПАТЕРН: Singleton
Гарантує, що існує лише ОДНЕ підключення до бази даних SQLite
у всьому застосунку. Будь-який код що викликає DatabaseConnection()
отримає той самий об'єкт.
"""
import sqlite3
import os
from threading import Lock


class DatabaseConnection:
    _instance = None   # зберігаємо єдиний екземпляр
    _lock = Lock()     # захист від одночасного створення в кількох потоках

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                # визначаємо шлях до файлу БД поруч із папкою проєкту
                db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'library.db')
                cls._instance._conn = sqlite3.connect(
                    os.path.abspath(db_path),
                    check_same_thread=False
                )
                cls._instance._conn.row_factory = sqlite3.Row  # рядки як словники
                cls._instance._conn.execute("PRAGMA foreign_keys = ON")
        return cls._instance

    @property
    def conn(self) -> sqlite3.Connection:
        return self._conn

    def execute(self, sql: str, params=()):
        return self._conn.execute(sql, params)

    def executemany(self, sql: str, params_list):
        return self._conn.executemany(sql, params_list)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()
