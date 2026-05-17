"""
Facade
"""
from datetime import datetime, timedelta
from repositories.user_repository     import UserRepository
from repositories.document_repository import DocumentRepository
from repositories.issuance_repository import IssuanceRepository
from repositories.request_repository  import BookRequestRepository
from models.entities import User, Document, Issuance, BookRequest
from patterns.gof import (
    Sorter, SortByLastName, SortByFirstName, SortByGroup,
    SortByTitle, SortByAuthor,
    CsvExportVisitor, TextReportVisitor, CountAvailableVisitor,
    UserBuilder, DocumentBuilder,
    BaseDocumentSearch, SortedResultsDecorator, AvailableOnlyDecorator,
    event_bus,
)

MAX_ISSUANCES  = 4    # максимум активних видач на читача
DEFAULT_DAYS   = 14   # стандартний термін видачі в днях


class LibraryFacade:

    def __init__(self):
        self._users    = UserRepository()
        self._docs     = DocumentRepository()
        self._issues   = IssuanceRepository()
        self._requests = BookRequestRepository()

    # ── Користувачі ──────────────────────────────────────────────────────────

    def get_all_users(self, sort_by='last_name'):
        users = self._users.find_all()
        sm = {'first_name': SortByFirstName(), 'last_name': SortByLastName(),
              'group': SortByGroup()}
        return Sorter(sm.get(sort_by, SortByLastName())).sort(users)

    def get_user(self, user_id: int):
        return self._users.find_by_id(user_id)

    def add_user(self, first_name, last_name, group, email='', phone='') -> int:
        user = (UserBuilder()
                .set_name(first_name, last_name)
                .set_group(group)
                .set_email(email)
                .set_phone(phone)
                .build())
        return self._users.save(user)

    def update_user(self, user: User) -> bool:
        return self._users.update(user)

    def delete_user(self, user_id: int) -> bool:
        if self._users.has_active_issuances(user_id):
            raise ValueError("Неможливо видалити читача — є активні видачі!")
        return self._users.delete(user_id)

    def search_users(self, query: str):
        return self._users.search(query)

    # ── Документи ────────────────────────────────────────────────────────────

    def get_all_documents(self, sort_by='title'):
        docs = self._docs.find_all()
        sm = {'title': SortByTitle(), 'author': SortByAuthor()}
        return Sorter(sm.get(sort_by, SortByTitle())).sort(docs)

    def get_document(self, doc_id: int):
        return self._docs.find_by_id(doc_id)

    def add_document(self, title, author, year, isbn='', copies=1) -> int:
        doc = (DocumentBuilder()
               .set_title(title).set_author(author).set_year(year)
               .set_isbn(isbn).set_copies(copies).build())
        return self._docs.save(doc)

    def update_document(self, doc: Document) -> bool:
        return self._docs.update(doc)

    def delete_document(self, doc_id: int) -> bool:
        if self._docs.has_active_issuances(doc_id):
            raise ValueError("Неможливо видалити документ — є активні видачі!")
        return self._docs.delete(doc_id)

    def search_documents(self, query, only_available=False, sorted_results=True):
        svc = BaseDocumentSearch(self._docs)
        if only_available: svc = AvailableOnlyDecorator(svc)
        if sorted_results:  svc = SortedResultsDecorator(svc)
        return svc.search(query)

    def get_document_status(self, doc_id: int) -> str:
        doc = self._docs.find_by_id(doc_id)
        if not doc: return "Документ не знайдено"
        if doc.available_copies > 0:
            return f"✅  У бібліотеці ({doc.available_copies} з {doc.total_copies} доступно)"
        issue = self._issues.find_active_by_doc(doc_id)
        if issue:
            overdue = " ⚠️ ПРОСТРОЧЕНО!" if issue.is_overdue else ""
            due = f", повернути до: {issue.due_date[:10]}" if issue.due_date else ""
            return f"📤  Виданий: {issue.user_name} (від {issue.issued_at}{due}){overdue}"
        return "Статус невідомий"

    # ── Видача ────────────────────────────────────────────────────────────────

    def issue_document(self, user_id: int, doc_id: int, days: int = DEFAULT_DAYS):
        active = self._issues.count_active_by_user(user_id)
        if active >= MAX_ISSUANCES:
            raise ValueError(
                f"Читач вже має {active} активних видач. Максимум — {MAX_ISSUANCES}!"
            )
        doc = self._docs.find_by_id(doc_id)
        if not doc or doc.available_copies <= 0:
            raise ValueError("Документ недоступний для видачі!")

        due_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        issue = Issuance(user_id=user_id, doc_id=doc_id, due_date=due_date)
        issue_id = self._issues.save(issue)
        self._docs.decrement_available(doc_id)
        event_bus.emit('issuance.created', user_id=user_id, doc_id=doc_id)

    def return_document(self, issue_id: int):
        issue = self._issues.find_by_id(issue_id)
        if not issue:
            raise ValueError("Видачу не знайдено!")
        if issue.status == 'RETURNED':
            raise ValueError("Документ вже повернуто!")
        issue.status      = 'RETURNED'
        issue.returned_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._issues.update(issue)
        self._docs.increment_available(issue.doc_id)
        event_bus.emit('issuance.returned', issue_id=issue_id)

    def get_all_issuances(self):
        return self._issues.find_all()

    def get_user_issuances(self, user_id: int):
        return self._issues.find_by_user(user_id)

    def get_overdue_count(self) -> int:
        return sum(1 for i in self._issues.find_all() if i.is_overdue)

    # ── Запити студентів ──────────────────────────────────────────────────────

    def add_book_request(self, doc_id: int, student_name: str,
                         student_group: str, message: str = '') -> int:
        req = BookRequest(
            doc_id=doc_id,
            student_name=student_name,
            student_group=student_group,
            message=message
        )
        return self._requests.save(req)

    def get_all_requests(self):
        return self._requests.find_all()

    def get_new_requests(self):
        return self._requests.find_new()

    def mark_request_processed(self, request_id: int):
        self._requests.mark_processed(request_id)

    def count_new_requests(self) -> int:
        return self._requests.count_new()

    # ── Звіти ─────────────────────────────────────────────────────────────────

    def export_documents_csv(self, filepath: str):
        docs = self._docs.find_all()
        visitor = CsvExportVisitor()
        for doc in docs: doc.accept(visitor)
        with open(filepath, 'w', encoding='utf-8-sig') as f:
            f.write(visitor.get_csv())

    def get_text_report(self) -> str:
        docs = self._docs.find_all()
        tv = TextReportVisitor()
        cv = CountAvailableVisitor()
        for doc in docs:
            doc.accept(tv)
            doc.accept(cv)
        report = tv.get_report()
        issues = self._issues.find_all()
        overdue = [i for i in issues if i.is_overdue]
        report += f'\n\nДоступно: {cv.count} з {len(docs)} документів'
        report += f'\nПрострочених видач: {len(overdue)}'
        if overdue:
            report += '\n\n⚠️  ПРОСТРОЧЕНІ ВИДАЧІ:'
            for i in overdue:
                report += f'\n  [{i.issue_id}] {i.doc_title} → {i.user_name} (до {i.due_date})'
        return report
