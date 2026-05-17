"""
Діалог додавання/редагування співробітника.
- При додаванні: пароль обов'язковий
- При редагуванні: пароль змінюється окремо через ChangePasswordDialog
- lock_role=True — роль не можна змінити (для себе)
- lock_active=True — статус не можна змінити (для себе)
"""
import re
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QCheckBox,
    QPushButton, QFrame, QGroupBox
)
from PyQt5.QtCore import Qt
from gui.styles import PRIMARY, PRIMARY_LIGHT, BORDER, WHITE, BG, TEXT, btn_style

RE_EMAIL = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')


def _inp(ph='', val='', password=False):
    f = QLineEdit(val)
    f.setPlaceholderText(ph)
    f.setFixedHeight(36)
    if password:
        f.setEchoMode(QLineEdit.Password)
    f.setStyleSheet(f"""
        QLineEdit {{ border:1.5px solid {BORDER}; border-radius:6px;
                     padding:0 10px; background:white; font-size:13px; }}
        QLineEdit:focus {{ border-color:{PRIMARY_LIGHT}; background:#F0F7FF; }}
    """)
    return f

def _inp_disabled(val=''):
    """Поле тільки для читання."""
    f = QLineEdit(val)
    f.setFixedHeight(36)
    f.setEnabled(False)
    f.setStyleSheet(f"""
        QLineEdit {{ border:1.5px solid {BORDER}; border-radius:6px;
                     padding:0 10px; background:#F5F5F5; font-size:13px;
                     color:#888; }}
    """)
    return f


class StaffDialog(QDialog):

    def __init__(self, parent=None, member=None, staff_repo=None,
                 lock_role=False, lock_active=False):
        super().__init__(parent)
        self._edit        = member is not None
        self._member      = member
        self._repo        = staff_repo
        self._lock_role   = lock_role
        self._lock_active = lock_active
        self.setWindowTitle("Редагувати співробітника" if self._edit else "Новий співробітник")
        self.setFixedWidth(460)
        self.setStyleSheet(f"QDialog {{ background:{BG}; }}")
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        icon = "✏️" if self._edit else "➕"
        title = QLabel(f"{icon}  {'Редагування' if self._edit else 'Новий співробітник'}")
        title.setStyleSheet(f"font-size:16px; font-weight:700; color:{PRIMARY};")
        lay.addWidget(title)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background:{BORDER};"); sep.setFixedHeight(1)
        lay.addWidget(sep)

        # Попередження якщо редагуємо себе
        if self._edit and self._lock_role:
            warn = QLabel("ℹ️  Ви редагуєте власний акаунт. Роль і статус змінити неможливо.")
            warn.setStyleSheet(f"""
                background:#FFF8E1; border-left:4px solid #F57C00;
                border-radius:6px; padding:10px 14px;
                color:#E65100; font-size:12px;
            """)
            warn.setWordWrap(True)
            lay.addWidget(warn)

        # Основні дані
        grp = QGroupBox("Дані співробітника")
        grp.setStyleSheet(f"""
            QGroupBox {{ border:1.5px solid {BORDER}; border-radius:8px;
                         margin-top:12px; padding:12px; background:{WHITE}; }}
            QGroupBox::title {{ subcontrol-origin:margin; left:10px;
                                padding:0 6px; color:{PRIMARY}; font-weight:bold; }}
        """)
        form = QFormLayout(grp)
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        m = self._member
        self.f_name     = _inp("Наприклад: Іван Петренко", m.full_name if m else "")
        self.f_username = _inp("Логін для входу",          m.username  if m else "")
        self.f_email    = _inp("email@library.ua",          m.email or "" if m else "")

        # Роль
        if self._lock_role:
            role_display = {'admin': '👑  Адміністратор', 'librarian': '📚  Бібліотекар'}
            self.f_role = _inp_disabled(role_display.get(m.role, m.role) if m else "")
            self._role_value = m.role if m else 'librarian'
        else:
            self.f_role = QComboBox()
            self.f_role.setFixedHeight(36)
            self.f_role.addItem("📚  Бібліотекар",   "librarian")
            self.f_role.addItem("👑  Адміністратор", "admin")
            self.f_role.setStyleSheet(f"""
                QComboBox {{ border:1.5px solid {BORDER}; border-radius:6px;
                             padding:0 10px; background:white; font-size:13px; }}
                QComboBox:focus {{ border-color:{PRIMARY_LIGHT}; }}
                QComboBox QAbstractItemView {{ background:white;
                    selection-background-color:{PRIMARY_LIGHT}; selection-color:white; }}
            """)
            if m:
                idx = self.f_role.findData(m.role)
                if idx >= 0: self.f_role.setCurrentIndex(idx)

        # Статус активності
        if self._lock_active:
            self.f_active = None
            active_lbl = QLabel("✅  Активний (не змінюється для власного акаунту)")
            active_lbl.setStyleSheet(f"color:#1E7E34; font-size:12px;")
            form.addRow("ПІБ *:",    self.f_name)
            form.addRow("Логін *:",  self.f_username)
            form.addRow("Email:",    self.f_email)
            form.addRow("Роль:",     self.f_role)
            form.addRow("Статус:",   active_lbl)
        else:
            self.f_active = QCheckBox("Активний (може входити в систему)")
            self.f_active.setChecked(m.is_active if m else True)
            self.f_active.setStyleSheet(f"color:{TEXT}; font-size:13px;")
            form.addRow("ПІБ *:",    self.f_name)
            form.addRow("Логін *:",  self.f_username)
            form.addRow("Email:",    self.f_email)
            form.addRow("Роль:",     self.f_role)
            form.addRow("Статус:",   self.f_active)

        lay.addWidget(grp)

        # Пароль — тільки при ДОДАВАННІ
        if not self._edit:
            pwd_grp = QGroupBox("Пароль")
            pwd_grp.setStyleSheet(grp.styleSheet())
            pwd_form = QFormLayout(pwd_grp)
            pwd_form.setSpacing(10)
            pwd_form.setLabelAlignment(Qt.AlignRight)
            self.f_pwd  = _inp("Мінімум 4 символи", password=True)
            self.f_pwd2 = _inp("Повторіть пароль",  password=True)
            pwd_form.addRow("Пароль *:",      self.f_pwd)
            pwd_form.addRow("Підтвердження:", self.f_pwd2)
            lay.addWidget(pwd_grp)
        else:
            self.f_pwd  = None
            self.f_pwd2 = None
            # Підказка про зміну пароля
            hint = QLabel("🔑  Щоб змінити пароль — використайте кнопку «Змінити пароль» у таблиці.")
            hint.setStyleSheet(f"""
                background:#E8F5E9; border-left:4px solid #28A745;
                border-radius:6px; padding:10px 14px;
                color:#1E7E34; font-size:12px;
            """)
            hint.setWordWrap(True)
            lay.addWidget(hint)

        # Помилки
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

        if not self.f_name.text().strip():
            errors.append("ПІБ обов'язкове")
        if not self.f_username.text().strip():
            errors.append("Логін обов'язковий")

        # Перевірка унікальності логіну
        exclude_id = self._member.staff_id if self._member else 0
        username = self.f_username.text().strip()
        if self._repo and username:
            if self._repo.username_exists(username, exclude_id):
                errors.append(f"Логін «{username}» вже зайнятий")

        # Email
        email = self.f_email.text().strip()
        if email and not RE_EMAIL.match(email):
            errors.append("Невірний формат email")

        # Пароль — тільки при додаванні
        if not self._edit:
            pwd  = self.f_pwd.text()
            pwd2 = self.f_pwd2.text()
            if not pwd:
                errors.append("Пароль обов'язковий")
            elif len(pwd) < 4:
                errors.append("Пароль мінімум 4 символи")
            elif pwd != pwd2:
                errors.append("Паролі не співпадають")

        if errors:
            self.err.setText("⚠️  " + "  |  ".join(errors))
            return
        self.accept()

    def get_data(self) -> dict:
        # Отримуємо роль
        if self._lock_role:
            role = self._role_value
        else:
            role = self.f_role.currentData()

        # Отримуємо статус
        if self._lock_active or self.f_active is None:
            is_active = True
        else:
            is_active = self.f_active.isChecked()

        return {
            'full_name': self.f_name.text().strip(),
            'username':  self.f_username.text().strip(),
            'email':     self.f_email.text().strip() or None,
            'role':      role,
            'is_active': is_active,
            'password':  self.f_pwd.text() if self.f_pwd else None,
        }
