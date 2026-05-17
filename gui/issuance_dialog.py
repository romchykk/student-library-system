"""Діалог видачі з вибором терміну повернення."""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QSpinBox, QPushButton, QFrame, QGroupBox
)
from PyQt5.QtCore import Qt
from datetime import datetime, timedelta
from gui.styles import PRIMARY, PRIMARY_LIGHT, BORDER, WHITE, BG, TEXT, SUCCESS_LIGHT, SUCCESS, btn_style


class IssueDialog(QDialog):
    def __init__(self, parent, doc, users):
        super().__init__(parent)
        self.setWindowTitle("Видача документу")
        self.setFixedWidth(460)
        self.setStyleSheet(f"QDialog {{ background:{BG}; }}")
        self._users = users
        self._setup_ui(doc)

    def _setup_ui(self, doc):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20); lay.setSpacing(14)

        title = QLabel("📤  Видача документу")
        title.setStyleSheet(f"font-size:16px; font-weight:700; color:{PRIMARY};")
        lay.addWidget(title)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background:{BORDER};"); sep.setFixedHeight(1)
        lay.addWidget(sep)

        # Інфо про документ
        doc_grp = QGroupBox("Документ")
        doc_grp.setStyleSheet(f"""
            QGroupBox {{ border:1.5px solid {BORDER}; border-radius:8px;
                         margin-top:12px; padding:10px; background:{WHITE}; }}
            QGroupBox::title {{ subcontrol-origin:margin; left:10px;
                                padding:0 6px; color:{PRIMARY}; font-weight:bold; }}
        """)
        dlay = QVBoxLayout(doc_grp); dlay.setSpacing(4)

        for label, value in [("Назва", doc.title), ("Автор", doc.author), ("Рік", str(doc.year))]:
            row = QHBoxLayout()
            l = QLabel(f"{label}:"); l.setStyleSheet(f"color:#546E7A; font-size:12px; min-width:70px;")
            v = QLabel(value); v.setStyleSheet(f"color:{TEXT}; font-size:13px; font-weight:500;")
            row.addWidget(l); row.addWidget(v); row.addStretch(); dlay.addLayout(row)

        # Доступно
        row = QHBoxLayout()
        l = QLabel("Доступно:"); l.setStyleSheet(f"color:#546E7A; font-size:12px; min-width:70px;")
        color = "#1E7E34" if doc.available_copies > 0 else "#DC3545"
        v = QLabel(str(doc.available_copies))
        v.setStyleSheet(f"color:{color}; font-size:13px; font-weight:700;")
        row.addWidget(l); row.addWidget(v); row.addStretch(); dlay.addLayout(row)
        lay.addWidget(doc_grp)

        # Читач
        reader_grp = QGroupBox("Читач")
        reader_grp.setStyleSheet(doc_grp.styleSheet())
        rlay = QVBoxLayout(reader_grp)
        self.combo = QComboBox()
        self.combo.setFixedHeight(38)
        self.combo.setStyleSheet(f"""
            QComboBox {{ border:1.5px solid {BORDER}; border-radius:6px;
                         padding:0 12px; background:white; font-size:13px; }}
            QComboBox:focus {{ border-color:{PRIMARY_LIGHT}; }}
            QComboBox QAbstractItemView {{ background:white;
                selection-background-color:{PRIMARY_LIGHT}; selection-color:white; }}
        """)
        for u in self._users:
            self.combo.addItem(f"{u.full_name}  —  {u.academic_group}", u.user_id)
        rlay.addWidget(self.combo)
        lay.addWidget(reader_grp)

        # Термін повернення
        term_grp = QGroupBox("Термін повернення")
        term_grp.setStyleSheet(doc_grp.styleSheet())
        tlay = QHBoxLayout(term_grp)

        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 90)
        self.days_spin.setValue(14)
        self.days_spin.setSuffix(" днів")
        self.days_spin.setFixedHeight(36)
        self.days_spin.setFixedWidth(120)
        self.days_spin.setStyleSheet(f"""
            QSpinBox {{ border:1.5px solid {BORDER}; border-radius:6px;
                        padding:0 10px; background:white; font-size:13px; }}
            QSpinBox:focus {{ border-color:{PRIMARY_LIGHT}; }}
        """)
        self.days_spin.valueChanged.connect(self._update_due_label)

        self.due_label = QLabel()
        self.due_label.setStyleSheet(f"color:#1E7E34; font-size:13px; font-weight:600;")
        self._update_due_label()

        tlay.addWidget(QLabel("Термін:"))
        tlay.addWidget(self.days_spin)
        tlay.addWidget(QLabel("  Повернути до:"))
        tlay.addWidget(self.due_label)
        tlay.addStretch()
        lay.addWidget(term_grp)

        # Кнопки
        row = QHBoxLayout(); row.setSpacing(10)
        ok = QPushButton("📤  Видати")
        ok.setFixedHeight(40); ok.setCursor(Qt.PointingHandCursor)
        ok.setStyleSheet(btn_style(SUCCESS_LIGHT, SUCCESS))
        ok.clicked.connect(self.accept)

        cancel = QPushButton("Скасувати")
        cancel.setFixedHeight(40); cancel.setCursor(Qt.PointingHandCursor)
        cancel.setStyleSheet(f"""
            QPushButton {{ background:white; color:{TEXT}; border:1.5px solid {BORDER};
                           border-radius:7px; font-size:13px; padding:0 16px; }}
            QPushButton:hover {{ background:#F5F5F5; }}
        """)
        cancel.clicked.connect(self.reject)
        row.addStretch(); row.addWidget(cancel); row.addWidget(ok)
        lay.addLayout(row)

    def _update_due_label(self):
        days = self.days_spin.value()
        due  = (datetime.now() + timedelta(days=days)).strftime('%d.%m.%Y')
        self.due_label.setText(due)

    def get_user_id(self) -> int:
        return self.combo.currentData()

    def get_days(self) -> int:
        return self.days_spin.value()
