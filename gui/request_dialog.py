"""Діалог запиту студента на книгу — зберігається в БД."""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QFrame, QGroupBox
)
from PyQt5.QtCore import Qt
from gui.styles import PRIMARY, PRIMARY_LIGHT, BORDER, WHITE, BG, TEXT, btn_style
SUCCESS_LIGHT = "#28A745"
SUCCESS       = "#1E7E34"


class StudentRequestDialog(QDialog):
    """Студент подає запит на конкретну книгу."""

    def __init__(self, parent, doc):
        super().__init__(parent)
        self.setWindowTitle("Запит на книгу")
        self.setFixedWidth(440)
        self.setStyleSheet(f"QDialog {{ background:{BG}; }}")
        self._doc = doc
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20); lay.setSpacing(14)

        title = QLabel("📬  Запит на отримання книги")
        title.setStyleSheet(f"font-size:16px; font-weight:700; color:{PRIMARY};")
        lay.addWidget(title)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background:{BORDER};"); sep.setFixedHeight(1)
        lay.addWidget(sep)

        # Інфо про книгу
        book_frame = QFrame()
        book_frame.setStyleSheet(f"""
            QFrame {{ background:#EBF3FB; border-radius:8px;
                      border-left:4px solid {PRIMARY_LIGHT}; }}
        """)
        bf = QVBoxLayout(book_frame); bf.setContentsMargins(14,10,14,10); bf.setSpacing(3)
        bf.addWidget(QLabel(f"📖  {self._doc.title}"))
        bf.addWidget(QLabel(f"✍️   {self._doc.author} ({self._doc.year})"))
        avail = self._doc.available_copies
        avail_lbl = QLabel(f"{'✅' if avail > 0 else '❌'}  Доступно: {avail} прим.")
        avail_lbl.setStyleSheet(f"color:{'#1E7E34' if avail>0 else '#DC3545'}; font-weight:600;")
        bf.addWidget(avail_lbl)
        lay.addWidget(book_frame)

        # Форма студента
        grp = QGroupBox("Ваші дані")
        grp.setStyleSheet(f"""
            QGroupBox {{ border:1.5px solid {BORDER}; border-radius:8px;
                         margin-top:12px; padding:12px; background:{WHITE}; }}
            QGroupBox::title {{ subcontrol-origin:margin; left:10px;
                                padding:0 6px; color:{PRIMARY}; font-weight:bold; }}
        """)
        from PyQt5.QtWidgets import QFormLayout
        form = QFormLayout(grp); form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        def inp(ph):
            f = QLineEdit(); f.setPlaceholderText(ph); f.setFixedHeight(36)
            f.setStyleSheet(f"""
                QLineEdit {{ border:1.5px solid {BORDER}; border-radius:6px;
                             padding:0 10px; background:white; font-size:13px; }}
                QLineEdit:focus {{ border-color:{PRIMARY_LIGHT}; background:#F0F7FF; }}
            """)
            return f

        self.f_name  = inp("Наприклад: Іван Петренко")
        self.f_group = inp("Наприклад: ПІ-41")
        self.f_msg   = QTextEdit()
        self.f_msg.setPlaceholderText("Додатковий коментар (необов'язково)...")
        self.f_msg.setFixedHeight(70)
        self.f_msg.setStyleSheet(f"""
            QTextEdit {{ border:1.5px solid {BORDER}; border-radius:6px;
                         padding:6px 10px; background:white; font-size:13px; }}
            QTextEdit:focus {{ border-color:{PRIMARY_LIGHT}; }}
        """)

        form.addRow("Ім'я та прізвище *:", self.f_name)
        form.addRow("Академічна група *:", self.f_group)
        form.addRow("Коментар:",           self.f_msg)
        lay.addWidget(grp)

        self.err = QLabel("")
        self.err.setStyleSheet("color:#DC3545; font-size:12px;")
        lay.addWidget(self.err)

        # Кнопки
        row = QHBoxLayout(); row.setSpacing(10)
        ok = QPushButton("📬  Надіслати запит")
        ok.setFixedHeight(40); ok.setCursor(Qt.PointingHandCursor)
        ok.setStyleSheet(btn_style(SUCCESS_LIGHT, SUCCESS))
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
        if not self.f_name.text().strip():  errors.append("Введіть ім'я та прізвище")
        if not self.f_group.text().strip(): errors.append("Введіть групу")
        if errors:
            self.err.setText("⚠️  " + "  |  ".join(errors)); return
        self.accept()

    def get_data(self):
        return {
            'student_name':  self.f_name.text().strip(),
            'student_group': self.f_group.text().strip(),
            'message':       self.f_msg.toPlainText().strip(),
        }
