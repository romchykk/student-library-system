"""Головне вікно — фінальна версія з управлінням персоналом."""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel, QComboBox, QStatusBar, QAction, QMessageBox,
    QFileDialog, QDialog, QTextEdit, QFrame,
    QPushButton, QCheckBox, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from datetime import datetime, timedelta

from services.facade  import LibraryFacade
from services.logger  import log_action, log_error, log
from services.config  import MAX_ISSUANCES, DEFAULT_LOAN_DAYS, LIBRARY_NAME
from patterns.gof     import event_bus
from gui.roles        import can, get_icon
from gui.styles       import (
    APP_STYLE, PRIMARY, PRIMARY_LIGHT, PRIMARY_DARK,
    SUCCESS_LIGHT, SUCCESS, DANGER_LIGHT, DANGER,
    WARNING_LIGHT, WARNING, PURPLE_LIGHT, PURPLE,
    GRAY_DARK, WHITE, BORDER, BG, TEXT, TEXT_LIGHT, btn_style
)
from gui.widgets          import StatCard, SearchBar
from gui.user_dialog      import UserDialog
from gui.document_dialog  import DocumentDialog
from gui.issuance_dialog  import IssueDialog
from gui.detail_dialogs   import UserDetailDialog, DocDetailDialog
from gui.print_dialog     import PrintCardDialog
from gui.staff_dialog     import StaffDialog

COLOR_OVERDUE = QColor("#FFEBEE")
COLOR_WARN    = QColor("#FFF8E1")
TEXT_OVERDUE  = QColor("#C62828")


def _btn(text, color=PRIMARY_LIGHT, hover=PRIMARY, tip="", h=36, enabled=True):
    b = QPushButton(text)
    b.setFixedHeight(h); b.setCursor(Qt.PointingHandCursor)
    b.setStyleSheet(btn_style(color, hover)); b.setEnabled(enabled)
    if tip: b.setToolTip(tip)
    return b

def _table(headers, stretch_cols=None):
    t = QTableWidget(0, len(headers))
    t.setHorizontalHeaderLabels(headers)
    hh = t.horizontalHeader()
    if stretch_cols:
        for c in range(len(headers)):
            hh.setSectionResizeMode(c, QHeaderView.Stretch if c in stretch_cols
                                    else QHeaderView.ResizeToContents)
    else:
        hh.setSectionResizeMode(QHeaderView.Stretch)
    t.setSelectionBehavior(QTableWidget.SelectRows)
    t.setEditTriggers(QTableWidget.NoEditTriggers)
    t.setAlternatingRowColors(True)
    t.verticalHeader().setVisible(False)
    t.setStyleSheet(f"""
        QTableWidget {{ border:1px solid {BORDER}; border-radius:10px;
                        background:white; gridline-color:#E8EEF4; outline:none; }}
        QTableWidget::item {{ padding:8px 10px; color:{TEXT}; }}
        QTableWidget::item:selected {{ background-color:{PRIMARY_LIGHT}; color:white; }}
        QTableWidget::item:alternate {{ background-color:#F0F7FF; color:{TEXT}; }}
        QTableWidget::item:alternate:selected {{ background-color:{PRIMARY_LIGHT}; color:white; }}
        QHeaderView::section {{ background:{PRIMARY}; color:white; padding:9px 10px;
                                font-weight:bold; font-size:12px; border:none;
                                border-right:1px solid #1A4A80; }}
        QHeaderView::section:last {{ border-right:none; }}
    """)
    return t


# ── Вікно студента ────────────────────────────────────────────────────────────
class StudentWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.facade = LibraryFacade()
        self.setStyleSheet(APP_STYLE)
        self.setWindowTitle(f"📚 Каталог  —  🎓 Студент  |  {LIBRARY_NAME}")
        self.setMinimumSize(900, 620)
        self._setup_ui(); self._load()

    def closeEvent(self, event):
        if QMessageBox.question(self,"Вихід","Ви дійсно хочете вийти?",
                QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            event.accept()
        else: event.ignore()

    def _setup_ui(self):
        mb = self.menuBar(); m = mb.addMenu("Меню")
        a  = QAction("🚪  Змінити роль", self); a.triggered.connect(self._logout); m.addAction(a)

        root = QWidget(); self.setCentralWidget(root)
        lay  = QVBoxLayout(root); lay.setContentsMargins(20,14,20,14); lay.setSpacing(12)

        hdr = QHBoxLayout()
        title = QLabel("📖  Каталог книг")
        title.setStyleSheet(f"font-size:20px; font-weight:700; color:{PRIMARY};")
        hdr.addWidget(title); hdr.addStretch()
        self._avail_lbl = QLabel("")
        self._avail_lbl.setStyleSheet(f"""
            background:#E8F5E9; color:#1E7E34; border-radius:10px;
            padding:6px 14px; font-size:12px; font-weight:600;
        """)
        hdr.addWidget(self._avail_lbl); lay.addLayout(hdr)

        sr = QHBoxLayout(); sr.setSpacing(10)
        self._search = SearchBar("Пошук за назвою або автором...")
        self._search.connect(self._filter)
        self._chk = QCheckBox("Тільки доступні")
        self._chk.setStyleSheet(f"color:{TEXT}; font-size:13px;")
        self._chk.stateChanged.connect(self._filter)
        sr.addWidget(self._search); sr.addWidget(self._chk); lay.addLayout(sr)

        self._tbl = _table(["ID","Назва","Автор","Рік","ISBN","Наявність"], stretch_cols=[1,2])
        self._tbl.doubleClicked.connect(self._request_book)
        lay.addWidget(self._tbl)

        hint = QLabel("💡  Двічі клікніть на книгу щоб подати запит")
        hint.setStyleSheet(f"color:{TEXT_LIGHT}; font-size:11px; padding:2px 4px;")
        lay.addWidget(hint)

        self.statusbar = QStatusBar(); self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("🎓 Студент  |  Перегляд каталогу")

    def _load(self):
        self._all = self.facade.get_all_documents("title")
        self._fill(self._all)
        self._avail_lbl.setText(f"✅  Доступно: {sum(d.available_copies for d in self._all)} прим.")

    def _fill(self, docs):
        self._tbl.setRowCount(len(docs))
        for r, d in enumerate(docs):
            avail_text = f"✅  {d.available_copies} прим." if d.available_copies > 0 else "❌  Немає"
            for c, v in enumerate([str(d.doc_id),d.title,d.author,str(d.year),d.isbn or "",avail_text]):
                item = QTableWidgetItem(v)
                if c == 5:
                    item.setForeground(QColor("#1E7E34") if d.available_copies>0 else QColor("#DC3545"))
                    item.setFont(QFont("Segoe UI",10,QFont.Bold))
                self._tbl.setItem(r, c, item)

    def _filter(self):
        q = self._search.text().strip().lower(); avail = self._chk.isChecked()
        docs = self._all
        if q:     docs = [d for d in docs if q in d.title.lower() or q in d.author.lower()]
        if avail: docs = [d for d in docs if d.available_copies > 0]
        self._fill(docs)

    def _request_book(self):
        row = self._tbl.currentRow()
        if row < 0: return
        doc = self.facade.get_document(int(self._tbl.item(row,0).text()))
        if not doc: return
        from gui.request_dialog import StudentRequestDialog
        dlg = StudentRequestDialog(self, doc)
        if dlg.exec_():
            d = dlg.get_data()
            self.facade.add_book_request(doc.doc_id, d['student_name'], d['student_group'], d['message'])
            QMessageBox.information(self,"✅  Запит надіслано",
                f"Запит на «{doc.title}» зафіксовано.\n\nЗверніться до бібліотекаря.")

    def _logout(self):
        self.close()
        from gui.login_dialog import LoginDialog
        login = LoginDialog()
        if login.exec_() == LoginDialog.Accepted:
            _open_window(login.role, login.display_name, login.username, login.staff_id)


# ── Головне вікно ─────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):

    def __init__(self, role="admin", display_name="Адміністратор",
                 username="admin", staff_id=None):
        super().__init__()
        self.facade       = LibraryFacade()
        self.role         = role
        self.display_name = display_name
        self.username     = username
        self.staff_id     = staff_id

        from repositories.staff_repository import StaffRepository
        self._staff_repo  = StaffRepository()

        event_bus.subscribe('issuance.created',  self._on_data_changed)
        event_bus.subscribe('issuance.returned', self._on_data_changed)

        self.setStyleSheet(APP_STYLE)
        self._setup_ui()
        self._load_all()
        self._check_overdue_on_start()

    def _can(self, p): return can(self.role, p)

    def closeEvent(self, event):
        if QMessageBox.question(self,"Підтвердження виходу",
                "Ви дійсно хочете вийти із системи?",
                QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            log_action(self.role, self.username, "LOGOUT")
            event.accept()
        else: event.ignore()

    def _check_overdue_on_start(self):
        """Показує попередження якщо є прострочені видачі."""
        try:
            overdue = self.facade.get_overdue_count()
            if overdue > 0:
                QMessageBox.warning(self, "⚠️  Увага!",
                    f"У системі є {overdue} прострочених видач!\n\n"
                    f"Перейдіть на вкладку «Видачі» → фільтр «⚠️ Прострочені».")
        except Exception as e:
            log_error("MainWindow._check_overdue_on_start", e)

    # ── UI ────────────────────────────────────────────────────────────────────
    def _setup_ui(self):
        icon = get_icon(self.role)
        self.setWindowTitle(f"{LIBRARY_NAME}  —  {icon} {self.display_name}")
        self.setMinimumSize(1200, 740)
        self._build_menu()

        root = QWidget(); self.setCentralWidget(root)
        lay  = QVBoxLayout(root); lay.setContentsMargins(16,12,16,12); lay.setSpacing(12)
        lay.addLayout(self._stats_row())

        self.tabs = QTabWidget(); lay.addWidget(self.tabs)
        self.tabs.addTab(self._tab_users(),    "👥   Читачі")
        self.tabs.addTab(self._tab_docs(),     "📖   Документи")
        self.tabs.addTab(self._tab_issues(),   "📋   Видачі")
        self.tabs.addTab(self._tab_requests(), "📬   Запити")
        # Вкладка персоналу — тільки для адміна
        if self.role == 'admin':
            self.tabs.addTab(self._tab_staff(), "👤   Персонал")

        self.statusbar = QStatusBar(); self.setStatusBar(self.statusbar)
        self._set_status("Готово")

    def _build_menu(self):
        mb = self.menuBar(); m = mb.addMenu("Файл")
        for name, slot in [("📊  Звіт", self._show_report),
                            ("💾  Експорт CSV", self._export_csv)]:
            a = QAction(name,self); a.triggered.connect(slot); m.addAction(a)
        m.addSeparator()
        a = QAction("🚪  Вийти (змінити роль)", self)
        a.triggered.connect(self._logout); m.addAction(a)

    def _stats_row(self):
        self._sc_u = StatCard("👥","Читачів",        0, PRIMARY_LIGHT)
        self._sc_d = StatCard("📖","Документів",     0, SUCCESS)
        self._sc_i = StatCard("⏳","Активних видач", 0, WARNING)
        self._sc_o = StatCard("⚠️", "Прострочених",  0, "#C62828")
        row = QHBoxLayout(); row.setSpacing(12)
        for c in [self._sc_u,self._sc_d,self._sc_i,self._sc_o]: row.addWidget(c)
        return row

    # ── Вкладки ───────────────────────────────────────────────────────────────
    def _tab_users(self):
        w = QWidget(); lay = QVBoxLayout(w); lay.setContentsMargins(4,10,4,4); lay.setSpacing(10)
        ctrl = QHBoxLayout(); ctrl.setSpacing(8)
        self._u_add   = _btn("➕  Додати",    SUCCESS_LIGHT,SUCCESS,"Додати читача (ТЗ 1.1)",  enabled=self._can("user_add"))
        self._u_edit  = _btn("✏️  Редагувати",PRIMARY_LIGHT,PRIMARY,"Редагувати (ТЗ 1.3)",     enabled=self._can("user_edit"))
        self._u_del   = _btn("🗑  Видалити",  DANGER_LIGHT, DANGER, "Видалити — тільки адмін", enabled=self._can("user_delete"))
        self._u_view  = _btn("👁  Картка",    PURPLE_LIGHT, PURPLE, "Картка читача (ТЗ 1.4)",  enabled=self._can("user_view"))
        self._u_print = _btn("🖨  Формуляр",  GRAY_DARK,"#263238",  "Друк формуляру",           enabled=self._can("user_view"))
        self._u_add.clicked.connect(self._add_user);   self._u_edit.clicked.connect(self._edit_user)
        self._u_del.clicked.connect(self._delete_user);self._u_view.clicked.connect(self._view_user)
        self._u_print.clicked.connect(self._print_card)
        for b in [self._u_add,self._u_edit,self._u_del,self._u_view,self._u_print]: ctrl.addWidget(b)
        ctrl.addStretch()
        self._u_sort = QComboBox(); self._u_sort.addItems(["За прізвищем","За іменем","За групою"])
        self._u_sort.setFixedHeight(34); self._u_sort.currentIndexChanged.connect(self._load_users)
        ctrl.addWidget(QLabel("Сортування:")); ctrl.addWidget(self._u_sort); lay.addLayout(ctrl)
        self._u_search = SearchBar("Пошук за іменем, прізвищем або групою..."); self._u_search.connect(self._search_users)
        lay.addWidget(self._u_search)
        self._u_tbl = _table(["ID","Прізвище","Ім'я","Група","Email","Телефон","Дата реєстрації"], stretch_cols=[1,2,4])
        self._u_tbl.doubleClicked.connect(self._view_user); lay.addWidget(self._u_tbl)
        self._u_cnt = QLabel(""); self._u_cnt.setStyleSheet(f"color:{TEXT_LIGHT}; font-size:11px;"); lay.addWidget(self._u_cnt)
        return w

    def _tab_docs(self):
        w = QWidget(); lay = QVBoxLayout(w); lay.setContentsMargins(4,10,4,4); lay.setSpacing(10)
        ctrl = QHBoxLayout(); ctrl.setSpacing(8)
        self._d_add    = _btn("➕  Додати",    SUCCESS_LIGHT,SUCCESS, "Додати (ТЗ 2.1)",    enabled=self._can("doc_add"))
        self._d_edit   = _btn("✏️  Редагувати",PRIMARY_LIGHT,PRIMARY, "Редагувати (ТЗ 2.3)",enabled=self._can("doc_edit"))
        self._d_del    = _btn("🗑  Видалити",  DANGER_LIGHT, DANGER,  "Тільки адмін",       enabled=self._can("doc_delete"))
        self._d_view   = _btn("👁  Деталі",    PURPLE_LIGHT, PURPLE,  "Деталі (ТЗ 2.4)",   enabled=self._can("doc_view"))
        self._d_issue  = _btn("📤  Видати",    WARNING_LIGHT,WARNING, "Видати (ТЗ 3.1)",   enabled=self._can("issue"))
        self._d_status = _btn("📍  Де книга?", GRAY_DARK,"#263238",   "Місце (ТЗ 3.3)",   enabled=self._can("doc_view"))
        self._d_add.clicked.connect(self._add_doc);    self._d_edit.clicked.connect(self._edit_doc)
        self._d_del.clicked.connect(self._delete_doc); self._d_view.clicked.connect(self._view_doc)
        self._d_issue.clicked.connect(self._issue_doc);self._d_status.clicked.connect(self._doc_status)
        for b in [self._d_add,self._d_edit,self._d_del,self._d_view,self._d_issue,self._d_status]: ctrl.addWidget(b)
        ctrl.addStretch()
        self._d_sort = QComboBox(); self._d_sort.addItems(["За назвою","За автором"])
        self._d_sort.setFixedHeight(34); self._d_sort.currentIndexChanged.connect(self._load_docs)
        ctrl.addWidget(QLabel("Сортування:")); ctrl.addWidget(self._d_sort); lay.addLayout(ctrl)
        sr = QHBoxLayout(); sr.setSpacing(10)
        self._d_search = SearchBar("Пошук за назвою або автором..."); self._d_search.connect(self._search_docs)
        self._d_chk = QCheckBox("Тільки доступні"); self._d_chk.stateChanged.connect(self._search_docs)
        sr.addWidget(self._d_search); sr.addWidget(self._d_chk); lay.addLayout(sr)
        self._d_tbl = _table(["ID","Назва","Автор","Рік","ISBN","Всього","Доступно"], stretch_cols=[1,2])
        self._d_tbl.doubleClicked.connect(self._view_doc); lay.addWidget(self._d_tbl)
        self._d_cnt = QLabel(""); self._d_cnt.setStyleSheet(f"color:{TEXT_LIGHT}; font-size:11px;"); lay.addWidget(self._d_cnt)
        return w

    def _tab_issues(self):
        w = QWidget(); lay = QVBoxLayout(w); lay.setContentsMargins(4,10,4,4); lay.setSpacing(10)
        ctrl = QHBoxLayout(); ctrl.setSpacing(8)
        self._i_ret = _btn("📥  Повернути", SUCCESS_LIGHT,SUCCESS,"Повернути (ТЗ 3.4)", enabled=self._can("return_doc"))
        self._i_ref = _btn("🔄  Оновити",   GRAY_DARK,"#263238","Оновити список")
        if not self._can("return_doc"): self._i_ret.setToolTip("⛔ Недоступно для вашої ролі")
        self._i_ret.clicked.connect(self._return_doc); self._i_ref.clicked.connect(self._load_issuances)
        legend = QHBoxLayout(); legend.setSpacing(12)
        for col, txt in [("#FFEBEE","🔴 Прострочено"),("#FFF8E1","🟡 Скоро (< 2 дні)"),("#FFFFFF","⚪ В нормі")]:
            l = QLabel(txt); l.setStyleSheet(f"font-size:11px; color:{TEXT_LIGHT}; background:{col}; padding:3px 8px; border-radius:4px; border:1px solid #ddd;")
            legend.addWidget(l)
        legend.addStretch()
        self._i_filter = QComboBox(); self._i_filter.addItems(["Всі видачі","Активні","Повернуті","⚠️ Прострочені"])
        self._i_filter.setFixedHeight(34); self._i_filter.currentIndexChanged.connect(self._load_issuances)
        for b in [self._i_ret,self._i_ref]: ctrl.addWidget(b)
        ctrl.addStretch(); ctrl.addWidget(QLabel("Фільтр:")); ctrl.addWidget(self._i_filter)
        lay.addLayout(ctrl); lay.addLayout(legend)
        self._i_tbl = _table(["ID","Читач","Документ","Видано","Повернути до","Повернено","Статус"], stretch_cols=[1,2])
        lay.addWidget(self._i_tbl)
        self._i_cnt = QLabel(""); self._i_cnt.setStyleSheet(f"color:{TEXT_LIGHT}; font-size:11px;"); lay.addWidget(self._i_cnt)
        return w

    def _tab_requests(self):
        w = QWidget(); lay = QVBoxLayout(w); lay.setContentsMargins(4,10,4,4); lay.setSpacing(10)
        ctrl = QHBoxLayout(); ctrl.setSpacing(8)
        self._r_done = _btn("✅  Оброблено", SUCCESS_LIGHT,SUCCESS,"Позначити як оброблений")
        self._r_ref  = _btn("🔄  Оновити",   GRAY_DARK,"#263238")
        self._r_done.clicked.connect(self._process_request); self._r_ref.clicked.connect(self._load_requests)
        self._r_filter = QComboBox(); self._r_filter.addItems(["Всі запити","Нові","Оброблені"])
        self._r_filter.setFixedHeight(34); self._r_filter.currentIndexChanged.connect(self._load_requests)
        for b in [self._r_done,self._r_ref]: ctrl.addWidget(b)
        ctrl.addStretch(); ctrl.addWidget(QLabel("Фільтр:")); ctrl.addWidget(self._r_filter)
        lay.addLayout(ctrl)
        self._r_tbl = _table(["ID","Книга","Студент","Група","Коментар","Дата","Статус"], stretch_cols=[1,2,4])
        lay.addWidget(self._r_tbl)
        self._r_cnt = QLabel(""); self._r_cnt.setStyleSheet(f"color:{TEXT_LIGHT}; font-size:11px;"); lay.addWidget(self._r_cnt)
        return w

    def _tab_staff(self):
        """Вкладка управління персоналом — тільки для адміна."""
        w = QWidget(); lay = QVBoxLayout(w); lay.setContentsMargins(4,10,4,4); lay.setSpacing(10)
        ctrl = QHBoxLayout(); ctrl.setSpacing(8)
        self._s_add  = _btn("➕  Додати",    SUCCESS_LIGHT,SUCCESS,"Додати нового співробітника")
        self._s_edit = _btn("✏️  Редагувати",PRIMARY_LIGHT,PRIMARY,"Редагувати дані співробітника")
        self._s_pwd  = _btn("🔑  Змінити пароль",WARNING_LIGHT,WARNING,"Змінити пароль співробітника")
        self._s_del  = _btn("🗑  Видалити",  DANGER_LIGHT, DANGER, "Видалити співробітника")
        self._s_add.clicked.connect(self._add_staff)
        self._s_edit.clicked.connect(self._edit_staff)
        self._s_pwd.clicked.connect(self._change_password)
        self._s_del.clicked.connect(self._delete_staff)
        for b in [self._s_add,self._s_edit,self._s_pwd,self._s_del]: ctrl.addWidget(b)
        ctrl.addStretch()
        lay.addLayout(ctrl)

        # Інформаційна панель
        info = QLabel("👑  Тут ви можете управляти акаунтами бібліотекарів та адміністраторів системи.")
        info.setStyleSheet(f"""
            background:#EBF3FB; border-left:4px solid {PRIMARY_LIGHT};
            border-radius:6px; padding:10px 14px; color:{TEXT}; font-size:13px;
        """)
        lay.addWidget(info)

        self._s_tbl = _table(
            ["ID","Логін","ПІБ","Роль","Email","Статус","Дата створення"],
            stretch_cols=[1,2,4]
        )
        self._s_tbl.doubleClicked.connect(self._edit_staff)
        lay.addWidget(self._s_tbl)
        self._s_cnt = QLabel(""); self._s_cnt.setStyleSheet(f"color:{TEXT_LIGHT}; font-size:11px;"); lay.addWidget(self._s_cnt)
        return w

    # ═════════════════════════════════════════════════════════════════════════
    # Дані
    # ═════════════════════════════════════════════════════════════════════════
    def _load_all(self):
        self._load_users(); self._load_docs()
        self._load_issuances(); self._load_requests()
        if self.role == 'admin': self._load_staff()
        self._update_stats()

    def _update_stats(self):
        users  = self.facade.get_all_users()
        docs   = self.facade.get_all_documents()
        issues = self.facade.get_all_issuances()
        self._sc_u.set_value(len(users)); self._sc_d.set_value(len(docs))
        self._sc_i.set_value(sum(1 for i in issues if i.status=="ACTIVE"))
        self._sc_o.set_value(sum(1 for i in issues if i.is_overdue))
        new_req = self.facade.count_new_requests()
        self.tabs.setTabText(3,"📬   Запити" + (f"  ({new_req})" if new_req else ""))

    def _load_users(self):
        sm={0:"last_name",1:"first_name",2:"group"}
        self._fill_users(self.facade.get_all_users(sm.get(self._u_sort.currentIndex(),"last_name")))

    def _fill_users(self, users):
        self._u_tbl.setRowCount(len(users))
        for r,u in enumerate(users):
            for c,v in enumerate([str(u.user_id),u.last_name,u.first_name,
                                   u.academic_group,u.email or "",u.phone or "",u.created_at or ""]):
                self._u_tbl.setItem(r,c,QTableWidgetItem(v))
        self._u_cnt.setText(f"Знайдено: {len(users)} читачів")

    def _load_docs(self):
        sm={0:"title",1:"author"}
        self._fill_docs(self.facade.get_all_documents(sm.get(self._d_sort.currentIndex(),"title")))

    def _fill_docs(self, docs):
        self._d_tbl.setRowCount(len(docs))
        for r,d in enumerate(docs):
            for c,v in enumerate([str(d.doc_id),d.title,d.author,str(d.year),
                                   d.isbn or "",str(d.total_copies),str(d.available_copies)]):
                item=QTableWidgetItem(v)
                if c==6:
                    item.setForeground(QColor("#DC3545") if d.available_copies==0 else QColor("#1E7E34"))
                    if d.available_copies==0: item.setFont(QFont("Segoe UI",10,QFont.Bold))
                self._d_tbl.setItem(r,c,item)
        self._d_cnt.setText(f"Знайдено: {len(docs)} документів")

    def _load_issuances(self):
        all_i=self.facade.get_all_issuances()
        f=self._i_filter.currentIndex()
        if f==1:   items=[i for i in all_i if i.status=="ACTIVE"]
        elif f==2: items=[i for i in all_i if i.status=="RETURNED"]
        elif f==3: items=[i for i in all_i if i.is_overdue]
        else:      items=all_i
        self._i_tbl.setRowCount(len(items))
        soon=datetime.now()+timedelta(days=2)
        for r,i in enumerate(items):
            due_str=i.due_date[:10] if i.due_date else "—"
            st="✓ Повернуто" if i.status=="RETURNED" else ("⚠️ ПРОСТРОЧЕНО" if i.is_overdue else "⏳ Активна")
            for c,v in enumerate([str(i.issue_id),i.user_name or "",i.doc_title or "",
                                   i.issued_at or "",due_str,i.returned_at or "—",st]):
                item=QTableWidgetItem(v)
                if c==6:
                    if i.is_overdue: item.setForeground(TEXT_OVERDUE); item.setFont(QFont("Segoe UI",10,QFont.Bold))
                    elif i.status=="RETURNED": item.setForeground(QColor("#1E7E34"))
                    else: item.setForeground(QColor("#E65100"))
                if i.is_overdue and i.status=="ACTIVE": item.setBackground(COLOR_OVERDUE)
                elif i.status=="ACTIVE" and i.due_date:
                    try:
                        if datetime.strptime(i.due_date[:10],'%Y-%m-%d')<=soon: item.setBackground(COLOR_WARN)
                    except: pass
                self._i_tbl.setItem(r,c,item)
        active_n=sum(1 for i in items if i.status=="ACTIVE")
        overdue_n=sum(1 for i in items if i.is_overdue)
        self._i_cnt.setText(f"Записів:{len(items)}  |  Активних:{active_n}"+(f"  |  ⚠️ Прострочених:{overdue_n}" if overdue_n else ""))

    def _load_requests(self):
        all_r=self.facade.get_all_requests()
        f=self._r_filter.currentIndex()
        if f==1:   items=[r for r in all_r if r.status=="NEW"]
        elif f==2: items=[r for r in all_r if r.status=="PROCESSED"]
        else:      items=all_r
        self._r_tbl.setRowCount(len(items))
        for r,req in enumerate(items):
            st="🆕 Новий" if req.status=="NEW" else "✅ Оброблено"
            for c,v in enumerate([str(req.request_id),req.doc_title or "—",req.student_name,
                                   req.student_group,req.message or "—",req.created_at or "—",st]):
                item=QTableWidgetItem(v)
                if c==6:
                    item.setForeground(QColor("#1565C0") if req.status=="NEW" else QColor("#1E7E34"))
                    if req.status=="NEW": item.setFont(QFont("Segoe UI",10,QFont.Bold))
                if req.status=="NEW": item.setBackground(QColor("#E3F2FD"))
                self._r_tbl.setItem(r,c,item)
        self._r_cnt.setText(f"Записів:{len(items)}  |  Нових:{sum(1 for r in items if r.status=='NEW')}")

    def _load_staff(self):
        members = self._staff_repo.find_all()
        self._s_tbl.setRowCount(len(members))
        for r, m in enumerate(members):
            role_icon = "👑" if m.role=="admin" else "📚"
            for c, v in enumerate([str(m.staff_id), m.username, m.full_name,
                                    f"{role_icon} {m.role_display}", m.email or "",
                                    m.status_display, m.created_at or ""]):
                item = QTableWidgetItem(v)
                if c == 5:
                    item.setForeground(QColor("#1E7E34") if m.is_active else QColor("#DC3545"))
                if not m.is_active:
                    item.setForeground(QColor("#9E9E9E"))
                self._s_tbl.setItem(r, c, item)
        self._s_cnt.setText(f"Співробітників: {len(members)}")

    # ═════════════════════════════════════════════════════════════════════════
    # Дії: Читачі
    # ═════════════════════════════════════════════════════════════════════════
    def _add_user(self):
        dlg=UserDialog(self)
        if dlg.exec_():
            d=dlg.get_data()
            try:
                self.facade.add_user(d['first_name'],d['last_name'],d['group'],d['email'],d['phone'])
                self._load_all(); self._set_status("✅  Читача додано!")
                log_action(self.role,self.username,"ADD_USER",f"{d['last_name']} {d['first_name']}")
            except Exception as e: QMessageBox.warning(self,"Помилка",str(e)); log_error("add_user",e)

    def _edit_user(self):
        uid=self._sel(self._u_tbl)
        if uid is None: return
        user=self.facade.get_user(uid)
        if not user: return
        dlg=UserDialog(self,user)
        if dlg.exec_():
            d=dlg.get_data()
            user.first_name=d['first_name']; user.last_name=d['last_name']
            user.academic_group=d['group']; user.email=d['email'] or None; user.phone=d['phone'] or None
            self.facade.update_user(user); self._load_users(); self._set_status("✅  Дані оновлено!")
            log_action(self.role,self.username,"EDIT_USER",f"ID={uid}")

    def _delete_user(self):
        if not self._can("user_delete"): QMessageBox.warning(self,"Доступ заборонено","⛔ Тільки адміністратор!"); return
        uid=self._sel(self._u_tbl)
        if uid is None: return
        user=self.facade.get_user(uid)
        if QMessageBox.question(self,"Підтвердження",f"Видалити «{user.full_name}»?",
                QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            try:
                self.facade.delete_user(uid); self._load_all(); self._set_status("🗑  Читача видалено!")
                log_action(self.role,self.username,"DELETE_USER",f"ID={uid}")
            except ValueError as e: QMessageBox.warning(self,"Помилка",str(e))

    def _view_user(self):
        uid=self._sel(self._u_tbl)
        if uid is None: return
        UserDetailDialog(self,self.facade.get_user(uid),self.facade.get_user_issuances(uid)).exec_()

    def _print_card(self):
        uid=self._sel(self._u_tbl)
        if uid is None: return
        PrintCardDialog(self,self.facade.get_user(uid),self.facade.get_user_issuances(uid)).exec_()

    def _search_users(self):
        q=self._u_search.text().strip()
        self._fill_users(self.facade.search_users(q) if q else self.facade.get_all_users())

    # ═════════════════════════════════════════════════════════════════════════
    # Дії: Документи
    # ═════════════════════════════════════════════════════════════════════════
    def _add_doc(self):
        dlg=DocumentDialog(self)
        if dlg.exec_():
            d=dlg.get_data()
            try:
                self.facade.add_document(d['title'],d['author'],d['year'],d['isbn'],d['copies'])
                self._load_all(); self._set_status("✅  Документ додано!")
                log_action(self.role,self.username,"ADD_DOC",d['title'])
            except Exception as e: QMessageBox.warning(self,"Помилка",str(e))

    def _edit_doc(self):
        did=self._sel(self._d_tbl)
        if did is None: return
        doc=self.facade.get_document(did)
        if not doc: return
        dlg=DocumentDialog(self,doc)
        if dlg.exec_():
            d=dlg.get_data()
            doc.title=d['title']; doc.author=d['author']; doc.year=d['year']; doc.isbn=d['isbn'] or None
            self.facade.update_document(doc); self._load_docs(); self._set_status("✅  Документ оновлено!")
            log_action(self.role,self.username,"EDIT_DOC",f"ID={did}")

    def _delete_doc(self):
        if not self._can("doc_delete"): QMessageBox.warning(self,"Доступ заборонено","⛔ Тільки адміністратор!"); return
        did=self._sel(self._d_tbl)
        if did is None: return
        doc=self.facade.get_document(did)
        if QMessageBox.question(self,"Підтвердження",f"Видалити «{doc.title}»?",
                QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            try:
                self.facade.delete_document(did); self._load_all(); self._set_status("🗑  Документ видалено!")
                log_action(self.role,self.username,"DELETE_DOC",f"ID={did}")
            except ValueError as e: QMessageBox.warning(self,"Помилка",str(e))

    def _view_doc(self):
        did=self._sel(self._d_tbl)
        if did is None: return
        DocDetailDialog(self,self.facade.get_document(did),self.facade.get_document_status(did)).exec_()

    def _doc_status(self):
        did=self._sel(self._d_tbl)
        if did is None: return
        doc=self.facade.get_document(did)
        QMessageBox.information(self,f"📍 Де «{doc.title}»?",self.facade.get_document_status(did))

    def _issue_doc(self):
        if not self._can("issue"): QMessageBox.warning(self,"Доступ заборонено","⛔ Недоступно для вашої ролі!"); return
        did=self._sel(self._d_tbl)
        if did is None: return
        doc=self.facade.get_document(did); users=self.facade.get_all_users()
        if not users: QMessageBox.information(self,"Увага","Спочатку додайте читачів!"); return
        dlg=IssueDialog(self,doc,users)
        if dlg.exec_():
            try:
                self.facade.issue_document(dlg.get_user_id(),did,dlg.get_days())
                self._load_all(); self._set_status("📤  Документ видано!")
                log_action(self.role,self.username,"ISSUE_DOC",f"doc_id={did} user_id={dlg.get_user_id()}")
            except ValueError as e: QMessageBox.warning(self,"Помилка видачі",str(e))

    def _search_docs(self):
        q=self._d_search.text().strip(); avail=self._d_chk.isChecked()
        docs=self.facade.search_documents(q,only_available=avail) if q else self.facade.get_all_documents()
        if not q and avail: docs=[d for d in docs if d.available_copies>0]
        self._fill_docs(docs)

    def _return_doc(self):
        if not self._can("return_doc"): QMessageBox.warning(self,"Доступ заборонено","⛔ Недоступно!"); return
        iid=self._sel(self._i_tbl)
        if iid is None: return
        if QMessageBox.question(self,"Підтвердження","Підтвердити повернення?",
                QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            try:
                self.facade.return_document(iid); self._load_all(); self._set_status("📥  Документ повернуто!")
                log_action(self.role,self.username,"RETURN_DOC",f"issue_id={iid}")
            except Exception as e: QMessageBox.warning(self,"Помилка",str(e))

    def _process_request(self):
        rid=self._sel(self._r_tbl)
        if rid is None: return
        self.facade.mark_request_processed(rid)
        self._load_requests(); self._update_stats(); self._set_status("✅  Запит оброблено!")
        log_action(self.role,self.username,"PROCESS_REQUEST",f"ID={rid}")

    # ═════════════════════════════════════════════════════════════════════════
    # Дії: Персонал
    # ═════════════════════════════════════════════════════════════════════════
    def _add_staff(self):
        dlg = StaffDialog(self, staff_repo=self._staff_repo)
        if dlg.exec_():
            d = dlg.get_data()
            try:
                from models.staff import StaffMember
                m = StaffMember(
                    username=d['username'], role=d['role'],
                    full_name=d['full_name'], email=d['email'],
                    is_active=d['is_active']
                )
                self._staff_repo.save(m, d['password'])
                self._load_staff()
                self._set_status(f"✅  Співробітника «{d['full_name']}» додано!")
                log_action(self.role, self.username, "ADD_STAFF", f"{d['username']} ({d['role']})")
            except Exception as e:
                QMessageBox.warning(self, "Помилка", str(e))
                log_error("add_staff", e)

    def _edit_staff(self):
        sid = self._sel(self._s_tbl)
        if sid is None: return
        member = self._staff_repo.find_by_id(sid)
        if not member: return

        # Себе можна редагувати, але не можна змінити свою роль або заблокувати
        is_self = (sid == self.staff_id)

        dlg = StaffDialog(self, member=member, staff_repo=self._staff_repo,
                          lock_role=is_self, lock_active=is_self)
        if dlg.exec_():
            d = dlg.get_data()
            member.full_name = d['full_name']
            member.username  = d['username']
            member.email     = d['email']
            if not is_self:
                member.role      = d['role']
                member.is_active = d['is_active']
            try:
                self._staff_repo.update(member)
                self._load_staff()
                self._set_status("✅  Дані співробітника оновлено!")
                log_action(self.role, self.username, "EDIT_STAFF", f"ID={sid}")
            except Exception as e:
                QMessageBox.warning(self, "Помилка", str(e))
                log_error("edit_staff", e)

    def _change_password(self):
        sid = self._sel(self._s_tbl)
        if sid is None: return
        member = self._staff_repo.find_by_id(sid)
        if not member: return

        # Використовуємо нормальний діалог замість QInputDialog
        from gui.change_password_dialog import ChangePasswordDialog
        dlg = ChangePasswordDialog(self, member.full_name)
        if dlg.exec_():
            try:
                self._staff_repo.change_password(sid, dlg.get_password())
                self._set_status(f"✅  Пароль «{member.full_name}» змінено!")
                log_action(self.role, self.username, "CHANGE_PASSWORD", f"staff_id={sid}")
                QMessageBox.information(self, "Готово",
                    f"Пароль співробітника «{member.full_name}» успішно змінено.")
            except Exception as e:
                QMessageBox.warning(self, "Помилка", str(e))
                log_error("change_password", e)

    def _delete_staff(self):
        sid = self._sel(self._s_tbl)
        if sid is None: return

        # Захист: не можна видалити себе
        if sid == self.staff_id:
            QMessageBox.warning(self, "Неможливо видалити",
                "⛔ Ви не можете видалити власний акаунт!\n\n"
                "Попросіть іншого адміністратора.")
            return

        member = self._staff_repo.find_by_id(sid)
        if not member: return

        reply = QMessageBox.question(
            self, "Підтвердження видалення",
            f"Видалити співробітника «{member.full_name}» ({member.role_display})?\n\n"
            f"Логін: {member.username}\n"
            f"Цю дію не можна скасувати.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self._staff_repo.delete(sid)
                self._load_staff()
                self._set_status(f"🗑  Співробітника «{member.full_name}» видалено!")
                log_action(self.role, self.username, "DELETE_STAFF", f"ID={sid} {member.username}")
            except ValueError as e:
                QMessageBox.warning(self, "Неможливо видалити", str(e))

    # ═════════════════════════════════════════════════════════════════════════
    # Звіти / Observer / Допоміжні
    # ═════════════════════════════════════════════════════════════════════════
    def _export_csv(self):
        path,_=QFileDialog.getSaveFileName(self,"Зберегти CSV","documents.csv","CSV (*.csv)")
        if path:
            self.facade.export_documents_csv(path)
            QMessageBox.information(self,"Готово",f"Збережено:\n{path}")
            log_action(self.role,self.username,"EXPORT_CSV",path)

    def _show_report(self):
        dlg=QDialog(self); dlg.setWindowTitle("Звіт"); dlg.resize(700,520)
        dlg.setStyleSheet(f"background:{BG};"); lay=QVBoxLayout(dlg)
        te=QTextEdit(); te.setReadOnly(True); te.setPlainText(self.facade.get_text_report())
        te.setStyleSheet("font-size:13px; background:white; border-radius:8px;")
        lay.addWidget(te); dlg.exec_()

    def _on_data_changed(self,**kwargs):
        self._load_docs(); self._load_issuances(); self._update_stats()

    def _logout(self):
        self.close()

    def _sel(self, table):
        rows=table.selectedItems()
        if not rows: QMessageBox.information(self,"Увага","Оберіть рядок!"); return None
        return int(table.item(table.currentRow(),0).text())

    def _set_status(self,msg):
        icon=get_icon(self.role)
        self.statusbar.showMessage(f"{icon} {self.display_name}   |   {msg}")


# ── Фабрика вікон ─────────────────────────────────────────────────────────────
def _open_window(role, display_name, username="", staff_id=None):
    if role == "student":
        w = StudentWindow()
    else:
        w = MainWindow(role=role, display_name=display_name,
                       username=username, staff_id=staff_id)
    w.show()
    QApplication.instance()._main_window = w
