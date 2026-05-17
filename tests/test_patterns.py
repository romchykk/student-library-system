"""
Unit тести для GoF-патернів та моделей.
Запуск: python -m unittest tests/test_patterns.py -v
або:    python -m unittest discover tests -v
"""
import sys
import os
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.entities import User, Document, Issuance


# ═══════════════════════════════════════════════════════════════════════════════
# STRATEGY
# ═══════════════════════════════════════════════════════════════════════════════

class TestStrategy(unittest.TestCase):

    def _users(self):
        return [
            User(1, "Іван",   "Петренко", "ПІ-41"),
            User(2, "Анна",   "Коваль",   "ІТ-31"),
            User(3, "Богдан", "Мельник",  "КН-21"),
        ]

    def _docs(self):
        return [
            Document(1, "Python основи",  "Лутц М.",   2020),
            Document(2, "Алгоритми",      "Кормен Т.", 2019),
            Document(3, "Бази даних",     "Дейт К.",   2021),
        ]

    def test_sort_by_last_name(self):
        from patterns.gof import SortByLastName, Sorter
        result = Sorter(SortByLastName()).sort(self._users())
        names  = [u.last_name for u in result]
        self.assertEqual(names, sorted(names, key=str.lower))

    def test_sort_by_first_name(self):
        from patterns.gof import SortByFirstName, Sorter
        result = Sorter(SortByFirstName()).sort(self._users())
        names  = [u.first_name for u in result]
        self.assertEqual(names, sorted(names, key=str.lower))

    def test_sort_by_group(self):
        from patterns.gof import SortByGroup, Sorter
        result = Sorter(SortByGroup()).sort(self._users())
        groups = [u.academic_group for u in result]
        self.assertEqual(groups, sorted(groups, key=str.lower))

    def test_sort_by_title(self):
        from patterns.gof import SortByTitle, Sorter
        result = Sorter(SortByTitle()).sort(self._docs())
        titles = [d.title for d in result]
        self.assertEqual(titles, sorted(titles, key=str.lower))

    def test_sort_by_author(self):
        from patterns.gof import SortByAuthor, Sorter
        result  = Sorter(SortByAuthor()).sort(self._docs())
        authors = [d.author for d in result]
        self.assertEqual(authors, sorted(authors, key=str.lower))

    def test_strategy_swap(self):
        """Стратегія змінюється динамічно без перестворення Sorter"""
        from patterns.gof import SortByLastName, SortByFirstName, Sorter
        sorter = Sorter(SortByLastName())
        r1     = sorter.sort(self._users())
        sorter.set_strategy(SortByFirstName())
        r2     = sorter.sort(self._users())
        self.assertEqual([u.last_name  for u in r1],
                         sorted([u.last_name  for u in self._users()], key=str.lower))
        self.assertEqual([u.first_name for u in r2],
                         sorted([u.first_name for u in self._users()], key=str.lower))

    def test_empty_list(self):
        from patterns.gof import SortByLastName, Sorter
        result = Sorter(SortByLastName()).sort([])
        self.assertEqual(result, [])


# ═══════════════════════════════════════════════════════════════════════════════
# OBSERVER
# ═══════════════════════════════════════════════════════════════════════════════

class TestObserver(unittest.TestCase):

    def test_subscribe_and_emit(self):
        from patterns.gof import EventBus
        bus = EventBus(); results = []
        bus.subscribe('test', lambda **kw: results.append(kw.get('val')))
        bus.emit('test', val=42)
        self.assertEqual(results, [42])

    def test_multiple_subscribers(self):
        from patterns.gof import EventBus
        bus = EventBus(); calls = []
        bus.subscribe('ev', lambda **kw: calls.append('A'))
        bus.subscribe('ev', lambda **kw: calls.append('B'))
        bus.emit('ev')
        self.assertEqual(calls, ['A', 'B'])

    def test_unsubscribe(self):
        from patterns.gof import EventBus
        bus = EventBus(); calls = []
        cb  = lambda **kw: calls.append(1)
        bus.subscribe('ev', cb)
        bus.unsubscribe('ev', cb)
        bus.emit('ev')
        self.assertEqual(calls, [])

    def test_unknown_event_no_error(self):
        from patterns.gof import EventBus
        bus = EventBus()
        bus.emit('nonexistent')  # не повинно кидати виключення

    def test_emit_with_kwargs(self):
        from patterns.gof import EventBus
        bus = EventBus(); received = {}
        bus.subscribe('data', lambda **kw: received.update(kw))
        bus.emit('data', user_id=5, doc_id=10)
        self.assertEqual(received, {'user_id': 5, 'doc_id': 10})


# ═══════════════════════════════════════════════════════════════════════════════
# VISITOR
# ═══════════════════════════════════════════════════════════════════════════════

class TestVisitor(unittest.TestCase):

    def _docs(self):
        return [
            Document(1, "Книга A", "Автор", 2020, available_copies=2),
            Document(2, "Книга B", "Автор", 2021, available_copies=0),
            Document(3, "Книга C", "Автор", 2022, available_copies=1),
        ]

    def test_count_available(self):
        from patterns.gof import CountAvailableVisitor
        visitor = CountAvailableVisitor()
        for d in self._docs(): d.accept(visitor)
        self.assertEqual(visitor.count, 2)

    def test_count_zero_when_all_issued(self):
        from patterns.gof import CountAvailableVisitor
        docs = [Document(i, "X", "Y", 2020, available_copies=0) for i in range(3)]
        visitor = CountAvailableVisitor()
        for d in docs: d.accept(visitor)
        self.assertEqual(visitor.count, 0)

    def test_csv_export_header(self):
        from patterns.gof import CsvExportVisitor
        visitor = CsvExportVisitor()
        csv = visitor.get_csv()
        self.assertIn("Назва", csv)
        self.assertIn("Автор", csv)

    def test_csv_export_content(self):
        from patterns.gof import CsvExportVisitor
        visitor = CsvExportVisitor()
        for d in self._docs(): d.accept(visitor)
        csv = visitor.get_csv()
        self.assertIn("Книга A", csv)
        self.assertIn("Книга B", csv)
        lines = csv.strip().split('\n')
        self.assertEqual(len(lines), 4)  # заголовок + 3 документи

    def test_text_report_content(self):
        from patterns.gof import TextReportVisitor
        visitor = TextReportVisitor()
        for d in self._docs(): d.accept(visitor)
        report = visitor.get_report()
        self.assertIn("ЗВІТ", report)
        self.assertIn("Книга A", report)
        self.assertIn("доступна", report)


# ═══════════════════════════════════════════════════════════════════════════════
# ITERATOR
# ═══════════════════════════════════════════════════════════════════════════════

class TestIterator(unittest.TestCase):

    def _docs(self):
        return [
            Document(1, "A", "X", 2020, available_copies=3),
            Document(2, "B", "Y", 2021, available_copies=0),
            Document(3, "C", "Z", 2022, available_copies=1),
        ]

    def test_available_count(self):
        from patterns.gof import AvailableDocIterator
        result = list(AvailableDocIterator(self._docs()))
        self.assertEqual(len(result), 2)

    def test_available_all_positive(self):
        from patterns.gof import AvailableDocIterator
        result = list(AvailableDocIterator(self._docs()))
        self.assertTrue(all(d.available_copies > 0 for d in result))

    def test_issued_count(self):
        from patterns.gof import IssuedDocIterator
        result = list(IssuedDocIterator(self._docs()))
        self.assertEqual(len(result), 1)

    def test_issued_correct_doc(self):
        from patterns.gof import IssuedDocIterator
        result = list(IssuedDocIterator(self._docs()))
        self.assertEqual(result[0].doc_id, 2)

    def test_iterator_protocol(self):
        from patterns.gof import AvailableDocIterator
        it = AvailableDocIterator(self._docs())
        self.assertTrue(hasattr(it, '__iter__'))
        self.assertTrue(hasattr(it, '__next__'))

    def test_stop_iteration(self):
        from patterns.gof import AvailableDocIterator
        it = AvailableDocIterator([])
        with self.assertRaises(StopIteration):
            next(it)


# ═══════════════════════════════════════════════════════════════════════════════
# DECORATOR
# ═══════════════════════════════════════════════════════════════════════════════

class TestDecorator(unittest.TestCase):

    class MockRepo:
        def search(self, q):
            return [
                Document(1, "Python основи",   "Лутц",   2020, available_copies=2),
                Document(2, "Python advanced",  "Рамальо",2022, available_copies=0),
                Document(3, "Java основи",      "Блох",   2019, available_copies=1),
            ]

    def test_available_only_decorator(self):
        from patterns.gof import BaseDocumentSearch, AvailableOnlyDecorator
        svc    = AvailableOnlyDecorator(BaseDocumentSearch(self.MockRepo()))
        result = svc.search("x")
        self.assertTrue(all(d.available_copies > 0 for d in result))
        self.assertEqual(len(result), 2)

    def test_sorted_decorator(self):
        from patterns.gof import BaseDocumentSearch, SortedResultsDecorator
        svc    = SortedResultsDecorator(BaseDocumentSearch(self.MockRepo()))
        result = svc.search("x")
        titles = [d.title for d in result]
        self.assertEqual(titles, sorted(titles, key=str.lower))

    def test_chained_decorators(self):
        from patterns.gof import BaseDocumentSearch, AvailableOnlyDecorator, SortedResultsDecorator
        svc = SortedResultsDecorator(
              AvailableOnlyDecorator(
              BaseDocumentSearch(self.MockRepo())))
        result = svc.search("x")
        self.assertTrue(all(d.available_copies > 0 for d in result))
        titles = [d.title for d in result]
        self.assertEqual(titles, sorted(titles, key=str.lower))

    def test_decorator_wraps_correctly(self):
        """Декоратор не змінює оригінальний сервіс."""
        from patterns.gof import BaseDocumentSearch, AvailableOnlyDecorator
        base = BaseDocumentSearch(self.MockRepo())
        deco = AvailableOnlyDecorator(base)
        # base повертає всі, deco — тільки доступні
        self.assertEqual(len(base.search("x")), 3)
        self.assertEqual(len(deco.search("x")), 2)


# ═══════════════════════════════════════════════════════════════════════════════
# BUILDER
# ═══════════════════════════════════════════════════════════════════════════════

class TestBuilder(unittest.TestCase):

    def test_user_builder_all_fields(self):
        from patterns.gof import UserBuilder
        user = (UserBuilder()
                .set_name("Іван", "Петренко")
                .set_group("ПІ-41")
                .set_email("ivan@test.com")
                .set_phone("+380671234567")
                .build())
        self.assertEqual(user.first_name,     "Іван")
        self.assertEqual(user.last_name,      "Петренко")
        self.assertEqual(user.academic_group, "ПІ-41")
        self.assertEqual(user.email,          "ivan@test.com")
        self.assertEqual(user.phone,          "+380671234567")

    def test_user_builder_strips_whitespace(self):
        from patterns.gof import UserBuilder
        user = UserBuilder().set_name("  Іван  ", "  Петренко  ").set_group(" ПІ-41 ").build()
        self.assertEqual(user.first_name, "Іван")
        self.assertEqual(user.last_name,  "Петренко")

    def test_user_builder_missing_name_raises(self):
        from patterns.gof import UserBuilder
        with self.assertRaises(ValueError):
            UserBuilder().set_group("ПІ-41").build()

    def test_user_builder_missing_group_raises(self):
        from patterns.gof import UserBuilder
        with self.assertRaises(ValueError):
            UserBuilder().set_name("Іван", "Петренко").build()

    def test_document_builder_all_fields(self):
        from patterns.gof import DocumentBuilder
        doc = (DocumentBuilder()
               .set_title("Python")
               .set_author("Лутц")
               .set_year(2023)
               .set_isbn("978-0-596-51698-4")
               .set_copies(3)
               .build())
        self.assertEqual(doc.title,        "Python")
        self.assertEqual(doc.author,       "Лутц")
        self.assertEqual(doc.year,         2023)
        self.assertEqual(doc.total_copies, 3)

    def test_document_builder_missing_title_raises(self):
        from patterns.gof import DocumentBuilder
        with self.assertRaises(ValueError):
            DocumentBuilder().set_author("Автор").build()

    def test_document_builder_missing_author_raises(self):
        from patterns.gof import DocumentBuilder
        with self.assertRaises(ValueError):
            DocumentBuilder().set_title("Назва").build()

    def test_empty_email_becomes_none(self):
        from patterns.gof import UserBuilder
        user = UserBuilder().set_name("А","Б").set_group("Г").set_email("").build()
        self.assertIsNone(user.email)


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

class TestSingleton(unittest.TestCase):

    def test_same_instance(self):
        from database.connection import DatabaseConnection
        db1 = DatabaseConnection()
        db2 = DatabaseConnection()
        self.assertIs(db1, db2)

    def test_connection_works(self):
        from database.connection import DatabaseConnection
        db  = DatabaseConnection()
        cur = db.execute("SELECT 1").fetchone()
        self.assertEqual(cur[0], 1)

    def test_multiple_queries(self):
        from database.connection import DatabaseConnection
        db = DatabaseConnection()
        db.execute("SELECT 1")
        db.execute("SELECT 2")  # повинно працювати без помилок


# ═══════════════════════════════════════════════════════════════════════════════
# ISSUANCE MODEL
# ═══════════════════════════════════════════════════════════════════════════════

class TestIssuanceModel(unittest.TestCase):

    def test_not_overdue_when_returned(self):
        issue = Issuance(status='RETURNED', due_date='2000-01-01')
        self.assertFalse(issue.is_overdue)

    def test_not_overdue_without_due_date(self):
        issue = Issuance(status='ACTIVE', due_date=None)
        self.assertFalse(issue.is_overdue)

    def test_overdue_past_date(self):
        issue = Issuance(status='ACTIVE', due_date='2000-01-01')
        self.assertTrue(issue.is_overdue)

    def test_not_overdue_future_date(self):
        future = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
        issue  = Issuance(status='ACTIVE', due_date=future)
        self.assertFalse(issue.is_overdue)

    def test_overdue_boundary_today(self):
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        issue = Issuance(status='ACTIVE', due_date=yesterday)
        self.assertTrue(issue.is_overdue)


# ═══════════════════════════════════════════════════════════════════════════════
# USER & DOCUMENT MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class TestModels(unittest.TestCase):

    def test_user_full_name(self):
        user = User(first_name="Іван", last_name="Петренко")
        self.assertEqual(user.full_name, "Петренко Іван")

    def test_document_is_available_true(self):
        self.assertTrue(Document(available_copies=3).is_available)

    def test_document_is_available_false(self):
        self.assertFalse(Document(available_copies=0).is_available)

    def test_document_accept_visitor(self):
        """Document.accept() викликає visit() на visitor."""
        class MockVisitor:
            def __init__(self): self.visited = []
            def visit(self, doc): self.visited.append(doc.doc_id)
        doc = Document(doc_id=7)
        v   = MockVisitor()
        doc.accept(v)
        self.assertEqual(v.visited, [7])


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

class TestConfig(unittest.TestCase):

    def test_max_issuances_positive_int(self):
        from services.config import MAX_ISSUANCES
        self.assertIsInstance(MAX_ISSUANCES, int)
        self.assertGreater(MAX_ISSUANCES, 0)

    def test_default_loan_days_positive_int(self):
        from services.config import DEFAULT_LOAN_DAYS
        self.assertIsInstance(DEFAULT_LOAN_DAYS, int)
        self.assertGreater(DEFAULT_LOAN_DAYS, 0)

    def test_library_name_non_empty_string(self):
        from services.config import LIBRARY_NAME
        self.assertIsInstance(LIBRARY_NAME, str)
        self.assertGreater(len(LIBRARY_NAME), 0)

    def test_get_function(self):
        from services.config import get
        val = get('library', 'name', 'default')
        self.assertIsInstance(val, str)

    def test_get_int_function(self):
        from services.config import get_int
        val = get_int('library', 'max_issuances', 4)
        self.assertIsInstance(val, int)


if __name__ == '__main__':
    unittest.main(verbosity=2)
