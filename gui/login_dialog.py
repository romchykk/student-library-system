"""Вікно входу — читає акаунти з таблиці staff у БД."""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QTabWidget, QWidget
)
from PyQt5.QtCore import Qt

PRIMARY       = "#1A3C5E"
PRIMARY_LIGHT = "#2E6DA4"
PRIMARY_DARK  = "#0F2A45"
BG            = "#F5F7FA"
BORDER        = "#CFD8DC"
TEXT          = "#1A1A2E"


def _inp_style():
    return f"""
        QLineEdit {{ border:1.5px solid {BORDER}; border-radius:7px;
                     padding:8px 14px; font-size:13px; background:white; }}
        QLineEdit:focus {{ border-color:{PRIMARY_LIGHT}; background:#F0F7FF; }}
    """

def _btn_style(bg, hover):
    return f"""
        QPushButton {{ background:{bg}; color:white; border:none;
                       border-radius:7px; font-size:14px; font-weight:600; padding:0 20px; }}
        QPushButton:hover {{ background:{hover}; }}
        QPushButton:pressed {{ background:{PRIMARY_DARK}; }}
    """


class LoginDialog(QDialog):

    def __init__(self):
        super().__init__()
        self.role         = None
        self.display_name = None
        self.username     = None
        self.staff_id     = None
        self._setup_ui()

    def _setup_ui(self):
        from services.config import LIBRARY_NAME
        self.setWindowTitle(f"Вхід — {LIBRARY_NAME}")
        self.setFixedSize(420, 490)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.setStyleSheet(f"QDialog {{ background:{BG}; }}")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Шапка
        header = QFrame()
        header.setFixedHeight(110)
        header.setStyleSheet(f"""
            QFrame {{ background:qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 {PRIMARY_LIGHT},stop:1 {PRIMARY_DARK}); }}
        """)
        hl = QVBoxLayout(header); hl.setAlignment(Qt.AlignCenter); hl.setSpacing(4)

        ico = QLabel("📚"); ico.setStyleSheet("font-size:32px; background:transparent;")
        ico.setAlignment(Qt.AlignCenter)
        tl = QLabel(LIBRARY_NAME)
        tl.setStyleSheet("color:white; font-size:17px; font-weight:700; background:transparent;")
        tl.setAlignment(Qt.AlignCenter)
        sl = QLabel("Система обліку літератури")
        sl.setStyleSheet("color:#AED6F1; font-size:11px; background:transparent;")
        sl.setAlignment(Qt.AlignCenter)

        hl.addWidget(ico); hl.addWidget(tl); hl.addWidget(sl)
        lay.addWidget(header)

        # Вміст
        content = QWidget(); content.setStyleSheet(f"background:{BG};")
        cl = QVBoxLayout(content); cl.setContentsMargins(28, 20, 28, 20); cl.setSpacing(14)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border:1.5px solid {BORDER}; border-radius:8px;
                                background:white; padding:16px; }}
            QTabBar::tab {{ background:#E8EEF4; color:#546E7A; padding:8px 24px;
                            font-size:13px; font-weight:600;
                            border-top-left-radius:6px; border-top-right-radius:6px; margin-right:3px; }}
            QTabBar::tab:selected {{ background:{PRIMARY}; color:white; }}
        """)
        self.tabs.addTab(self._staff_tab(),   "👤  Персонал")
        self.tabs.addTab(self._student_tab(), "🎓  Студент")
        cl.addWidget(self.tabs)

        hint = QLabel("Персонал: admin/admin123  або  librarian/lib123")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("color:#90A4AE; font-size:10px;")
        cl.addWidget(hint)
        lay.addWidget(content)

    def _staff_tab(self) -> QWidget:
        w = QWidget(); w.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(w); lay.setSpacing(10); lay.setContentsMargins(0,0,0,0)

        lbl_l = QLabel("Логін:"); lbl_l.setStyleSheet(f"font-weight:600; color:{TEXT}; font-size:13px;")
        self.inp_login = QLineEdit(); self.inp_login.setPlaceholderText("Введіть логін")
        self.inp_login.setFixedHeight(40); self.inp_login.setStyleSheet(_inp_style())

        lbl_p = QLabel("Пароль:"); lbl_p.setStyleSheet(f"font-weight:600; color:{TEXT}; font-size:13px;")
        self.inp_pass = QLineEdit(); self.inp_pass.setPlaceholderText("Введіть пароль")
        self.inp_pass.setEchoMode(QLineEdit.Password)
        self.inp_pass.setFixedHeight(40); self.inp_pass.setStyleSheet(_inp_style())
        self.inp_pass.returnPressed.connect(self._login_staff)

        self.lbl_err = QLabel(""); self.lbl_err.setStyleSheet("color:#DC3545; font-size:12px;")
        self.lbl_err.setAlignment(Qt.AlignCenter)

        btn = QPushButton("🔐  Увійти"); btn.setFixedHeight(44)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(_btn_style(PRIMARY_LIGHT, PRIMARY))
        btn.clicked.connect(self._login_staff)

        lay.addWidget(lbl_l); lay.addWidget(self.inp_login)
        lay.addWidget(lbl_p); lay.addWidget(self.inp_pass)
        lay.addWidget(self.lbl_err); lay.addWidget(btn); lay.addStretch()
        return w

    def _student_tab(self) -> QWidget:
        w = QWidget(); w.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(w); lay.setSpacing(14)
        lay.setContentsMargins(0, 10, 0, 0); lay.setAlignment(Qt.AlignTop)

        ico = QLabel("🎓"); ico.setStyleSheet("font-size:40px; background:transparent;")
        ico.setAlignment(Qt.AlignCenter)

        info = QLabel("Студент може переглядати каталог книг\n"
                      "та подавати запити на отримання видань.\n\n"
                      "Авторизація не потрібна.")
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet(f"color:{TEXT}; font-size:13px; line-height:1.6;")
        info.setWordWrap(True)

        btn = QPushButton("🎓  Увійти як студент"); btn.setFixedHeight(44)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(_btn_style("#1E7E34", "#155724"))
        btn.clicked.connect(self._login_student)

        lay.addWidget(ico); lay.addWidget(info); lay.addStretch(); lay.addWidget(btn)
        return w

    def _login_staff(self):
        login = self.inp_login.text().strip()
        pwd   = self.inp_pass.text()
        if not login or not pwd:
            self.lbl_err.setText("⚠️  Заповніть усі поля"); return

        # Перевіряємо через БД
        try:
            from repositories.staff_repository import StaffRepository
            repo   = StaffRepository()
            member = repo.find_by_credentials(login, pwd)
            if member:
                self.role         = member.role
                self.display_name = member.full_name
                self.username     = member.username
                self.staff_id     = member.staff_id

                from services.logger import log_action
                log_action(member.role, member.username, "LOGIN", "Успішний вхід")
                self.accept()
            else:
                self.inp_pass.clear()
                self.lbl_err.setText("⚠️  Невірний логін або пароль")
                from services.logger import log
                log.warning(f"Невдала спроба входу: username='{login}'")
        except Exception as e:
            from services.logger import log_error
            log_error("LoginDialog._login_staff", e)
            self.lbl_err.setText("⚠️  Помилка підключення до БД")

    def _login_student(self):
        self.role         = "student"
        self.display_name = "Студент"
        self.username     = "student"
        self.staff_id     = None
        self.accept()
