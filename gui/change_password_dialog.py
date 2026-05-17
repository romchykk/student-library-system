"""Діалог зміни пароля співробітника."""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QFrame
)
from PyQt5.QtCore import Qt
from gui.styles import PRIMARY, PRIMARY_LIGHT, BORDER, WHITE, BG, TEXT, btn_style


class ChangePasswordDialog(QDialog):

    def __init__(self, parent, member_name: str):
        super().__init__(parent)
        self.setWindowTitle("Зміна пароля")
        self.setFixedWidth(400)
        self.setStyleSheet(f"QDialog {{ background:{BG}; }}")
        self._setup_ui(member_name)

    def _setup_ui(self, name):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        title = QLabel(f"🔑  Зміна пароля")
        title.setStyleSheet(f"font-size:16px; font-weight:700; color:{PRIMARY};")
        lay.addWidget(title)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background:{BORDER};"); sep.setFixedHeight(1)
        lay.addWidget(sep)

        info = QLabel(f"Співробітник: {name}")
        info.setStyleSheet(f"""
            background:#EBF3FB; border-left:4px solid {PRIMARY_LIGHT};
            border-radius:6px; padding:10px 14px;
            color:{TEXT}; font-size:13px; font-weight:500;
        """)
        lay.addWidget(info)

        def inp(ph):
            f = QLineEdit()
            f.setPlaceholderText(ph)
            f.setEchoMode(QLineEdit.Password)
            f.setFixedHeight(38)
            f.setStyleSheet(f"""
                QLineEdit {{ border:1.5px solid {BORDER}; border-radius:6px;
                             padding:0 10px; background:white; font-size:13px; }}
                QLineEdit:focus {{ border-color:{PRIMARY_LIGHT}; background:#F0F7FF; }}
            """)
            return f

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)
        self.f_new  = inp("Мінімум 4 символи")
        self.f_conf = inp("Повторіть новий пароль")
        form.addRow("Новий пароль *:",    self.f_new)
        form.addRow("Підтвердження *:",   self.f_conf)
        lay.addLayout(form)

        self.err = QLabel("")
        self.err.setStyleSheet("color:#DC3545; font-size:12px;")
        self.err.setWordWrap(True)
        lay.addWidget(self.err)

        row = QHBoxLayout(); row.setSpacing(10)
        ok = QPushButton("💾  Зберегти пароль")
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
        self.f_conf.returnPressed.connect(self._validate)

        row.addStretch(); row.addWidget(cancel); row.addWidget(ok)
        lay.addLayout(row)

    def _validate(self):
        pwd  = self.f_new.text()
        conf = self.f_conf.text()
        if not pwd:
            self.err.setText("⚠️  Введіть новий пароль"); return
        if len(pwd) < 4:
            self.err.setText("⚠️  Пароль мінімум 4 символи"); return
        if pwd != conf:
            self.err.setText("⚠️  Паролі не співпадають")
            self.f_conf.clear(); self.f_conf.setFocus(); return
        self.accept()

    def get_password(self) -> str:
        return self.f_new.text()
