"""
GoF ПАТЕРНИ — усі реалізації в одному файлі.
"""
from abc import ABC, abstractmethod
from typing import List, Callable
from models.entities import User, Document, Issuance


# ═══════════════════════════════════════════════════════════════════════════════
# 1. STRATEGY
# ═══════════════════════════════════════════════════════════════════════════════

class ISortStrategy(ABC):
    @abstractmethod
    def sort(self, items: list) -> list: ...

class SortByFirstName(ISortStrategy):
    def sort(self, users: List[User]) -> List[User]:
        return sorted(users, key=lambda u: u.first_name.lower())

class SortByLastName(ISortStrategy):
    def sort(self, users: List[User]) -> List[User]:
        return sorted(users, key=lambda u: u.last_name.lower())

class SortByGroup(ISortStrategy):
    def sort(self, users: List[User]) -> List[User]:
        return sorted(users, key=lambda u: u.academic_group.lower())

class SortByTitle(ISortStrategy):
    def sort(self, docs: List[Document]) -> List[Document]:
        return sorted(docs, key=lambda d: d.title.lower())

class SortByAuthor(ISortStrategy):
    def sort(self, docs: List[Document]) -> List[Document]:
        return sorted(docs, key=lambda d: d.author.lower())

class Sorter:
    def __init__(self, strategy: ISortStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: ISortStrategy):
        self._strategy = strategy

    def sort(self, items: list) -> list:
        return self._strategy.sort(items)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. OBSERVER
# ═══════════════════════════════════════════════════════════════════════════════

class EventBus:
    def __init__(self):
        self._listeners: dict = {}

    def subscribe(self, event: str, callback: Callable):
        self._listeners.setdefault(event, []).append(callback)

    def unsubscribe(self, event: str, callback: Callable):
        if event in self._listeners:
            self._listeners[event].remove(callback)

    def emit(self, event: str, **kwargs):
        for cb in self._listeners.get(event, []):
            cb(**kwargs)

event_bus = EventBus()


# ═══════════════════════════════════════════════════════════════════════════════
# 3. COMMAND
# ═══════════════════════════════════════════════════════════════════════════════

class ICommand(ABC):
    @abstractmethod
    def execute(self): ...
    @abstractmethod
    def undo(self): ...

class IssueDocumentCommand(ICommand):
    def __init__(self, issuance_repo, doc_repo, user_id: int, doc_id: int):
        self._issuance_repo = issuance_repo
        self._doc_repo      = doc_repo
        self._user_id       = user_id
        self._doc_id        = doc_id
        self._issue_id      = None

    def execute(self):
        issue = Issuance(user_id=self._user_id, doc_id=self._doc_id)
        self._issue_id = self._issuance_repo.save(issue)
        self._doc_repo.decrement_available(self._doc_id)
        event_bus.emit('issuance.created', user_id=self._user_id, doc_id=self._doc_id)

    def undo(self):
        if self._issue_id:
            self._issuance_repo.delete(self._issue_id)
            self._doc_repo.increment_available(self._doc_id)
            event_bus.emit('issuance.cancelled', issue_id=self._issue_id)
            self._issue_id = None

class ReturnDocumentCommand(ICommand):
    def __init__(self, issuance_repo, doc_repo, issue_id: int):
        self._issuance_repo = issuance_repo
        self._doc_repo      = doc_repo
        self._issue_id      = issue_id
        self._old_status    = None
        self._doc_id        = None

    def execute(self):
        from datetime import datetime
        issue = self._issuance_repo.find_by_id(self._issue_id)
        if issue:
            self._old_status  = issue.status
            self._doc_id      = issue.doc_id
            issue.status      = 'RETURNED'
            issue.returned_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self._issuance_repo.update(issue)
            self._doc_repo.increment_available(self._doc_id)
            event_bus.emit('issuance.returned', issue_id=self._issue_id)

    def undo(self):
        if self._doc_id and self._old_status:
            issue = self._issuance_repo.find_by_id(self._issue_id)
            if issue:
                issue.status      = self._old_status
                issue.returned_at = None
                self._issuance_repo.update(issue)
                self._doc_repo.decrement_available(self._doc_id)
                event_bus.emit('issuance.undo', issue_id=self._issue_id)

class CommandHistory:
    def __init__(self):
        self._stack: List[ICommand] = []

    def execute(self, command: ICommand):
        command.execute()
        self._stack.append(command)

    def undo(self):
        if self._stack:
            self._stack.pop().undo()

    def can_undo(self) -> bool:
        return len(self._stack) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# 4. VISITOR
# ═══════════════════════════════════════════════════════════════════════════════

class IDocumentVisitor(ABC):
    @abstractmethod
    def visit(self, document: Document): ...

class CountAvailableVisitor(IDocumentVisitor):
    def __init__(self):
        self.count = 0
    def visit(self, doc: Document):
        if doc.available_copies > 0:
            self.count += 1

class CsvExportVisitor(IDocumentVisitor):
    def __init__(self):
        self.rows: List[str] = ['ID,Назва,Автор,Рік,ISBN,Всього,Доступно']
    def visit(self, doc: Document):
        self.rows.append(
            f'{doc.doc_id},"{doc.title}","{doc.author}",'
            f'{doc.year},{doc.isbn or ""},'
            f'{doc.total_copies},{doc.available_copies}'
        )
    def get_csv(self) -> str:
        return '\n'.join(self.rows)

class TextReportVisitor(IDocumentVisitor):
    def __init__(self):
        self.lines: List[str] = ['=== ЗВІТ ПО ДОКУМЕНТАХ ===']
    def visit(self, doc: Document):
        status = '✓ доступна' if doc.available_copies > 0 else '✗ видана'
        self.lines.append(
            f'[{doc.doc_id}] {doc.title} / {doc.author} ({doc.year}) — {status}'
        )
    def get_report(self) -> str:
        return '\n'.join(self.lines)


# ═══════════════════════════════════════════════════════════════════════════════
# 5. ITERATOR
# ═══════════════════════════════════════════════════════════════════════════════

class AvailableDocIterator:
    def __init__(self, documents: List[Document]):
        self._docs  = [d for d in documents if d.available_copies > 0]
        self._index = 0
    def __iter__(self): return self
    def __next__(self) -> Document:
        if self._index >= len(self._docs): raise StopIteration
        doc = self._docs[self._index]; self._index += 1; return doc

class IssuedDocIterator:
    def __init__(self, documents: List[Document]):
        self._docs  = [d for d in documents if d.available_copies == 0]
        self._index = 0
    def __iter__(self): return self
    def __next__(self) -> Document:
        if self._index >= len(self._docs): raise StopIteration
        doc = self._docs[self._index]; self._index += 1; return doc


# ═══════════════════════════════════════════════════════════════════════════════
# 6. DECORATOR
# ═══════════════════════════════════════════════════════════════════════════════

class ISearchService(ABC):
    @abstractmethod
    def search(self, query: str) -> List[Document]: ...

class BaseDocumentSearch(ISearchService):
    def __init__(self, repo):
        self._repo = repo
    def search(self, query: str) -> List[Document]:
        return self._repo.search(query)

class SortedResultsDecorator(ISearchService):
    def __init__(self, wrapped: ISearchService):
        self._wrapped = wrapped
    def search(self, query: str) -> List[Document]:
        return sorted(self._wrapped.search(query), key=lambda d: d.title.lower())

class AvailableOnlyDecorator(ISearchService):
    def __init__(self, wrapped: ISearchService):
        self._wrapped = wrapped
    def search(self, query: str) -> List[Document]:
        return [d for d in self._wrapped.search(query) if d.available_copies > 0]


# ═══════════════════════════════════════════════════════════════════════════════
# 7. BUILDER
# ═══════════════════════════════════════════════════════════════════════════════

class UserBuilder:
    def __init__(self):
        self._user = User()

    def set_name(self, first: str, last: str) -> 'UserBuilder':
        self._user.first_name = first.strip()
        self._user.last_name  = last.strip()
        return self

    def set_group(self, group: str) -> 'UserBuilder':
        self._user.academic_group = group.strip()
        return self

    def set_email(self, email: str) -> 'UserBuilder':
        self._user.email = email.strip() or None
        return self

    def set_phone(self, phone: str) -> 'UserBuilder':
        self._user.phone = phone.strip() or None
        return self

    def build(self) -> User:
        if not self._user.first_name or not self._user.last_name:
            raise ValueError("Ім'я та прізвище обов'язкові!")
        if not self._user.academic_group:
            raise ValueError("Група обов'язкова!")
        return self._user


class DocumentBuilder:
    def __init__(self):
        self._doc = Document()

    def set_title(self, title: str) -> 'DocumentBuilder':
        self._doc.title = title.strip()
        return self

    def set_author(self, author: str) -> 'DocumentBuilder':
        self._doc.author = author.strip()
        return self

    def set_year(self, year: int) -> 'DocumentBuilder':
        self._doc.year = year
        return self

    def set_isbn(self, isbn: str) -> 'DocumentBuilder':
        self._doc.isbn = isbn.strip() or None
        return self

    def set_copies(self, count: int) -> 'DocumentBuilder':
        self._doc.total_copies = count
        return self

    def build(self) -> Document:
        if not self._doc.title:
            raise ValueError("Назва документу обов'язкова!")
        if not self._doc.author:
            raise ValueError("Автор документу обов'язковий!")
        return self._doc
