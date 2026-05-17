"""Діалог читача з валідацією email та телефону."""
import re
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QGroupBox
)
from PyQt5.QtCore import Qt
from gui.styles import PRIMARY, PRIMARY_LIGHT, BORDER, WHITE, BG, TEXT, btn_style

# Регулярні вирази
RE_EMAIL = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
RE_PHONE = re.compile(r'^\+?[\d\s\-()]{7,15}$')


def _field(ph, val=""):
    f = QLineEdit(val)
    f.setPlaceholderText(ph)
    f.setFixedHeight(36)
    f.setStyleSheet(f"""
        QLineEdit {{ border:1.5px solid {BORDER}; border-radius:6px;
                     padding:0 10px; background:white; font-size:13px; }}
        QLineEdit:focus {{ border-color:{PRIMARY_LIGHT}; background:#F0F7FF; }}
    """)
    return f

def _set_error(widget, is_error: bool):
    color = "#E74C3C" if is_error else BORDER
    widget.setStyleSheet(f"""
        QLineEdit {{ border:1.5px solid {color}; border-radius:6px;
                     padding:0 10px; background:{'#FFF5F5' if is_error else 'white'};
                     font-size:13px; }}
        QLineEdit:focus {{ border-color:{color}; }}
    """)


class UserDialog(QDialog):
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self._edit = user is not None
        self.setWindowTitle("Редагувати читача" if self._edit else "Новий читач")
        self.setFixedWidth(440)
        self.setStyleSheet(f"QDialog {{ background:{BG}; }}")
        self._setup_ui(user)

    def _setup_ui(self, user):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20); lay.setSpacing(14)

        t = QLabel("✏️  Редагування" if self._edit else "➕  Новий читач")
        t.setStyleSheet(f"font-size:16px; font-weight:700; color:{PRIMARY};")
        lay.addWidget(t)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background:{BORDER};"); sep.setFixedHeight(1)
        lay.addWidget(sep)

        grp = QGroupBox("Персональні дані")
        grp.setStyleSheet(f"""
            QGroupBox {{ border:1.5px solid {BORDER}; border-radius:8px;
                         margin-top:12px; padding:12px; background:{WHITE}; }}
            QGroupBox::title {{ subcontrol-origin:margin; left:10px;
                                padding:0 6px; color:{PRIMARY}; font-weight:bold; }}
        """)
        form = QFormLayout(grp); form.setSpacing(10); form.setLabelAlignment(Qt.AlignRight)

        self.f_last  = _field("Наприклад: Петренко",     user.last_name       if user else "")
        self.f_first = _field("Наприклад: Іван",          user.first_name      if user else "")
        self.f_group = _field("Наприклад: ПІ-41",         user.academic_group  if user else "")
        self.f_email = _field("example@gmail.com",        user.email  or ""    if user else "")
        self.f_phone = _field("+380XXXXXXXXX",            user.phone  or ""    if user else "")

        # Підказки поруч із полями
        def lbl(text, hint=""):
            l = QLabel(text)
            l.setStyleSheet(f"font-size:13px; color:{TEXT};")
            return l

        form.addRow(lbl("Прізвище *:"),  self.f_last)
        form.addRow(lbl("Ім'я *:"),      self.f_first)
        form.addRow(lbl("Група *:"),     self.f_group)
        form.addRow(lbl("Email:"),       self.f_email)
        form.addRow(lbl("Телефон:"),     self.f_phone)
        lay.addWidget(grp)

        # Блок помилок
        self.err = QLabel("")
        self.err.setStyleSheet("color:#DC3545; font-size:12px;")
        self.err.setWordWrap(True)
        lay.addWidget(self.err)

        # Кнопки
        row = QHBoxLayout(); row.setSpacing(10)
        ok = QPushButton("💾  Зберегти" if self._edit else "➕  Додати")
        ok.setFixedHeight(40); ok.setCursor(Qt.PointingHandCursor)
        ok.setStyleSheet(btn_style(PRIMARY_LIGHT, PRIMARY))
        ok.clicked.connect(self._validate)

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

    def _validate(self):
        errors = []

        # Обов'язкові поля
        for field, name in [(self.f_last,"Прізвище"),(self.f_first,"Ім'я"),(self.f_group,"Група")]:
            empty = not field.text().strip()
            _set_error(field, empty)
            if empty: errors.append(f"{name} обов'язкове")

        # Email — якщо заповнений
        email = self.f_email.text().strip()
        if email and not RE_EMAIL.match(email):
            _set_error(self.f_email, True)
            errors.append("Невірний формат email (example@mail.com)")
        else:
            _set_error(self.f_email, False)

        # Телефон — якщо заповнений
        phone = self.f_phone.text().strip()
        if phone and not RE_PHONE.match(phone):
            _set_error(self.f_phone, True)
            errors.append("Невірний формат телефону (+380XXXXXXXXX)")
        else:
            _set_error(self.f_phone, False)

        if errors:
            self.err.setText("⚠️  " + "  |  ".join(errors))
            return
        self.accept()

    def get_data(self):
        return {
            'last_name':  self.f_last.text().strip(),
            'first_name': self.f_first.text().strip(),
            'group':      self.f_group.text().strip(),
            'email':      self.f_email.text().strip(),
            'phone':      self.f_phone.text().strip(),
        }
