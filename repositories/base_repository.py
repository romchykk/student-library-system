"""
ПАТЕРН: Repository
Абстрактний базовий клас для всіх репозиторіїв.
Визначає інтерфейс CRUD — кожен репозиторій ЗОБОВ'ЯЗАНИЙ
реалізувати ці методи (завдяки @abstractmethod).
"""
from abc import ABC, abstractmethod
from typing import List, Optional


class IRepository(ABC):

    @abstractmethod
    def find_by_id(self, id: int):
        """Знайти запис за ID."""
        ...

    @abstractmethod
    def find_all(self) -> List:
        """Повернути всі записи."""
        ...

    @abstractmethod
    def save(self, entity) -> int:
        """Зберегти новий запис, повернути його ID."""
        ...

    @abstractmethod
    def update(self, entity) -> bool:
        """Оновити існуючий запис."""
        ...

    @abstractmethod
    def delete(self, id: int) -> bool:
        """Видалити запис за ID."""
        ...
