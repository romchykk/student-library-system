"""Діалог додавання / редагування документу."""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QSpinBox, QPushButton, QFrame, QGroupBox
)
from PyQt5.QtCore import Qt
from gui.styles import PRIMARY, PRIMARY_LIGHT, BORDER, WHITE, BG, TEXT, btn_style


def _inp(placeholder="", val=""):
    f = QLineEdit(str(val) if val else "")
    f.setPlaceholderText(placeholder)
    f.setFixedHeight(36)
    f.setStyleSheet(f"""
        QLineEdit {{ border: 1.5px solid {BORDER}; border-radius: 6px;
                     padding: 0 10px; background: white; font-size: 13px; }}
        QLineEdit:focus {{ border-color: {PRIMARY_LIGHT}; background: #F0F7FF; }}
    """)
    return f

def _spin(mn, mx, val):
    s = QSpinBox(); s.setRange(mn, mx); s.setValue(val)
    s.setFixedHeight(36)
    s.setStyleSheet(f"""
        QSpinBox {{ border: 1.5px solid {BORDER}; border-radius: 6px;
                    padding: 0 10px; background: white; font-size: 13px; }}
        QSpinBox:focus {{ border-color: {PRIMARY_LIGHT}; }}
    """)
    return s


class DocumentDialog(QDialog):
    def __init__(self, parent=None, doc=None):
        super().__init__(parent)
        self._is_edit = doc is not None
        self.setWindowTitle("Редагувати документ" if self._is_edit else "Новий документ")
        self.setFixedWidth(460)
        self.setStyleSheet(f"QDialog {{ background: {BG}; }}")
        self._setup_ui(doc)

    def _setup_ui(self, doc):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("✏️  Редагування документу" if self._is_edit else "📖  Новий документ")
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {PRIMARY};")
        layout.addWidget(title)

        line = QFrame(); line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background: {BORDER};"); line.setFixedHeight(1)
        layout.addWidget(line)

        grp = QGroupBox("Відомості про документ")
        grp.setStyleSheet(f"""
            QGroupBox {{ border: 1.5px solid {BORDER}; border-radius: 8px;
                         margin-top: 12px; padding: 12px; background: {WHITE}; }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 10px;
                                padding: 0 6px; color: {PRIMARY}; font-weight: bold; }}
        """)
        form = QFormLayout(grp)
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.inp_title  = _inp("Наприклад: Алгоритми та структури даних", doc.title  if doc else "")
        self.inp_author = _inp("Наприклад: Кормен Т.",                     doc.author if doc else "")
        self.inp_year   = _spin(1800, 2100, doc.year   if doc else 2024)
        self.inp_isbn   = _inp("Наприклад: 978-3-16-148410-0",              doc.isbn or "" if doc else "")
        self.inp_copies = _spin(1, 100, doc.total_copies if doc else 1)
        if self._is_edit:
            self.inp_copies.setEnabled(False)
            self.inp_copies.setToolTip("Кількість примірників не можна змінити після створення")

        form.addRow("Назва *:",          self.inp_title)
        form.addRow("Автор *:",          self.inp_author)
        form.addRow("Рік видання:",      self.inp_year)
        form.addRow("ISBN:",             self.inp_isbn)
        form.addRow("Кількість прим.:",  self.inp_copies)
        layout.addWidget(grp)

        self.lbl_err = QLabel("")
        self.lbl_err.setStyleSheet("color: #DC3545; font-size: 12px;")
        layout.addWidget(self.lbl_err)

        btn_layout = QHBoxLayout(); btn_layout.setSpacing(10)
        self.btn_ok = QPushButton("💾  Зберегти" if self._is_edit else "➕  Додати")
        self.btn_ok.setFixedHeight(40)
        self.btn_ok.setCursor(Qt.PointingHandCursor)
        self.btn_ok.setStyleSheet(btn_style(PRIMARY_LIGHT, PRIMARY))
        self.btn_ok.clicked.connect(self._validate)

        btn_cancel = QPushButton("Скасувати")
        btn_cancel.setFixedHeight(40)
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{ background: white; color: {TEXT}; border: 1.5px solid {BORDER};
                           border-radius: 7px; font-size: 13px; padding: 0 16px; }}
            QPushButton:hover {{ background: #F5F5F5; }}
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_ok)
        layout.addLayout(btn_layout)

    def _validate(self):
        errors = []
        if not self.inp_title.text().strip():  errors.append("Назва обов'язкова")
        if not self.inp_author.text().strip(): errors.append("Автор обов'язковий")
        if errors:
            self.lbl_err.setText("⚠️  " + ";  ".join(errors))
            return
        self.accept()

    def get_data(self):
        return {
            'title':  self.inp_title.text().strip(),
            'author': self.inp_author.text().strip(),
            'year':   self.inp_year.value(),
            'isbn':   self.inp_isbn.text().strip(),
            'copies': self.inp_copies.value(),
        }
