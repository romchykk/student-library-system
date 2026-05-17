"""
Діалоги детального перегляду:
- UserDetailDialog  — картка читача зі всіма видачами
- DocDetailDialog   — картка документу з статусом
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QFrame, QScrollArea, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from gui.styles import PRIMARY, PRIMARY_LIGHT, BORDER, WHITE, BG, TEXT, TEXT_LIGHT, btn_style


def _sep():
    line = QFrame(); line.setFrameShape(QFrame.HLine)
    line.setStyleSheet(f"background: {BORDER};"); line.setFixedHeight(1)
    return line

def _field(label, value, value_color=None):
    row = QHBoxLayout(); row.setSpacing(8)
    lbl = QLabel(f"{label}:")
    lbl.setStyleSheet(f"color: {TEXT_LIGHT}; font-size: 12px; min-width: 110px;")
    lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    val = QLabel(str(value or "—"))
    style = f"font-size: 13px; font-weight: 500; color: {value_color or TEXT};"
    val.setStyleSheet(style)
    val.setWordWrap(True)
    row.addWidget(lbl); row.addWidget(val, 1)
    return row


class UserDetailDialog(QDialog):
    """Детальний перегляд картки читача."""

    def __init__(self, parent, user, issuances, facade=None):
        super().__init__(parent)
        self.setWindowTitle(f"Картка читача — {user.full_name}")
        self.resize(640, 560)
        self.setStyleSheet(f"QDialog {{ background: {BG}; }}")
        self._user      = user
        self._issuances = issuances
        self._facade    = facade
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 16)
        layout.setSpacing(12)

        # Заголовок
        header = QHBoxLayout()
        avatar = QLabel("👤")
        avatar.setStyleSheet("font-size: 40px;")
        name_col = QVBoxLayout(); name_col.setSpacing(2)
        name_lbl = QLabel(self._user.full_name)
        name_lbl.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {PRIMARY};")
        group_lbl = QLabel(f"📚  {self._user.academic_group}")
        group_lbl.setStyleSheet(f"font-size: 13px; color: {TEXT_LIGHT};")
        name_col.addWidget(name_lbl); name_col.addWidget(group_lbl)
        header.addWidget(avatar); header.addLayout(name_col); header.addStretch()

        # Бейдж кількості активних видач
        active = sum(1 for i in self._issuances if i.status == "ACTIVE")
        badge = QLabel(f"📋  Активних видач: {active}")
        badge.setStyleSheet(f"""
            background: {'#E8F5E9' if active == 0 else '#FFF3E0'};
            color: {'#1E7E34' if active == 0 else '#E65100'};
            border-radius: 12px; padding: 6px 14px;
            font-weight: 600; font-size: 12px;
        """)
        header.addWidget(badge)
        layout.addLayout(header)
        layout.addWidget(_sep())

        # Контактна інформація
        info_title = QLabel("Контактна інформація")
        info_title.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {PRIMARY};")
        layout.addWidget(info_title)

        layout.addLayout(_field("ID читача",  self._user.user_id))
        layout.addLayout(_field("Email",      self._user.email))
        layout.addLayout(_field("Телефон",    self._user.phone))
        layout.addLayout(_field("Дата реєстрації", self._user.created_at))
        layout.addWidget(_sep())

        # Таблиця видач
        issues_title = QLabel(f"Історія видач  ({len(self._issuances)} записів)")
        issues_title.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {PRIMARY};")
        layout.addWidget(issues_title)

        tbl = QTableWidget(len(self._issuances), 4)
        tbl.setHorizontalHeaderLabels(["Документ", "Видано", "Повернено", "Статус"])
        tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        tbl.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        tbl.setSelectionBehavior(QTableWidget.SelectRows)
        tbl.setAlternatingRowColors(True)
        tbl.verticalHeader().setVisible(False)
        tbl.setStyleSheet(f"""
            QTableWidget {{ border: 1px solid {BORDER}; border-radius: 8px;
                            background: white; font-size: 12px; }}
            QHeaderView::section {{ background: {PRIMARY}; color: white;
                                     padding: 7px; font-size: 11px; border: none; }}
        """)

        for r, i in enumerate(self._issuances):
            tbl.setItem(r, 0, QTableWidgetItem(i.doc_title or "—"))
            tbl.setItem(r, 1, QTableWidgetItem(i.issued_at or "—"))
            tbl.setItem(r, 2, QTableWidgetItem(i.returned_at or "—"))
            status_item = QTableWidgetItem("✓ Повернуто" if i.status == "RETURNED" else "⏳ Активна")
            status_item.setForeground(
                QColor("#1E7E34") if i.status == "RETURNED" else QColor("#E65100")
            )
            tbl.setItem(r, 3, status_item)

        layout.addWidget(tbl)

        # Кнопка закрити
        btn_close = QPushButton("Закрити")
        btn_close.setFixedHeight(38)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{ background: white; color: {TEXT}; border: 1.5px solid {BORDER};
                           border-radius: 7px; font-size: 13px; padding: 0 20px; }}
            QPushButton:hover {{ background: #F5F5F5; }}
        """)
        btn_close.clicked.connect(self.close)
        btn_row = QHBoxLayout(); btn_row.addStretch(); btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)


class DocDetailDialog(QDialog):
    """Детальний перегляд картки документу."""

    def __init__(self, parent, doc, status_text, issuance=None):
        super().__init__(parent)
        self.setWindowTitle(f"Документ — {doc.title}")
        self.setFixedWidth(500)
        self.setStyleSheet(f"QDialog {{ background: {BG}; }}")
        self._setup_ui(doc, status_text, issuance)

    def _setup_ui(self, doc, status_text, issuance):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # Заголовок
        icon = QLabel("📖")
        icon.setStyleSheet("font-size: 36px;")
        title_lbl = QLabel(doc.title)
        title_lbl.setStyleSheet(f"font-size: 17px; font-weight: 700; color: {PRIMARY};")
        title_lbl.setWordWrap(True)
        author_lbl = QLabel(f"✍️  {doc.author}")
        author_lbl.setStyleSheet(f"font-size: 13px; color: {TEXT_LIGHT};")

        h = QHBoxLayout()
        h.addWidget(icon)
        col = QVBoxLayout(); col.setSpacing(2)
        col.addWidget(title_lbl); col.addWidget(author_lbl)
        h.addLayout(col, 1)
        layout.addLayout(h)
        layout.addWidget(_sep())

        # Деталі
        details_title = QLabel("Відомості про документ")
        details_title.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {PRIMARY};")
        layout.addWidget(details_title)

        layout.addLayout(_field("ID документу", doc.doc_id))
        layout.addLayout(_field("Рік видання",  doc.year))
        layout.addLayout(_field("ISBN",          doc.isbn))
        layout.addLayout(_field("Всього прим.",  doc.total_copies))

        avail_color = "#1E7E34" if doc.available_copies > 0 else "#DC3545"
        layout.addLayout(_field("Доступно прим.", doc.available_copies, avail_color))
        layout.addWidget(_sep())

        # Статус
        status_title = QLabel("Поточний статус")
        status_title.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {PRIMARY};")
        layout.addWidget(status_title)

        status_lbl = QLabel(status_text)
        is_avail = doc.available_copies > 0
        status_lbl.setStyleSheet(f"""
            background: {'#E8F5E9' if is_avail else '#FFF3E0'};
            color: {'#1E7E34' if is_avail else '#E65100'};
            border-radius: 8px; padding: 10px 14px;
            font-size: 13px; font-weight: 500;
        """)
        status_lbl.setWordWrap(True)
        layout.addWidget(status_lbl)

        # Кнопка
        btn_close = QPushButton("Закрити")
        btn_close.setFixedHeight(38)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{ background: white; color: {TEXT}; border: 1.5px solid {BORDER};
                           border-radius: 7px; font-size: 13px; padding: 0 20px; }}
            QPushButton:hover {{ background: #F5F5F5; }}
        """)
        btn_close.clicked.connect(self.close)
        btn_row = QHBoxLayout(); btn_row.addStretch(); btn_row.addWidget(btn_close)
        layout.addStretch()
        layout.addLayout(btn_row)
