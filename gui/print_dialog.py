"""Друк читацького формуляру (через QTextEdit + QPrinter)."""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit
)
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtCore import Qt
from gui.styles import PRIMARY, PRIMARY_LIGHT, BORDER, WHITE, BG, TEXT, btn_style


def _card_html(user, issuances) -> str:
    rows = ""
    for idx, i in enumerate(issuances, 1):
        status     = "Повернуто" if i.status == "RETURNED" else "На руках"
        status_col = "#1E7E34"   if i.status == "RETURNED" else "#E65100"
        returned   = i.returned_at or "—"
        rows += f"""<tr>
            <td style='padding:6px 8px;border-bottom:1px solid #eee;'>{idx}</td>
            <td style='padding:6px 8px;border-bottom:1px solid #eee;'>{i.doc_title or '—'}</td>
            <td style='padding:6px 8px;border-bottom:1px solid #eee;'>{i.issued_at or '—'}</td>
            <td style='padding:6px 8px;border-bottom:1px solid #eee;'>{returned}</td>
            <td style='padding:6px 8px;border-bottom:1px solid #eee;color:{status_col};font-weight:600;'>{status}</td>
        </tr>"""

    if not rows:
        rows = "<tr><td colspan='5' style='text-align:center;color:#888;padding:12px;'>Видач не знайдено</td></tr>"

    active = sum(1 for i in issuances if i.status == "ACTIVE")

    return f"""
<html><body style='font-family:Arial,sans-serif;margin:0;padding:20px;color:#1a1a1a;'>
<div style='text-align:center;border-bottom:3px solid #1A3C5E;padding-bottom:12px;margin-bottom:20px;'>
  <h2 style='color:#1A3C5E;margin:0;'>📚 Студентська бібліотека</h2>
  <p style='color:#546E7A;margin:4px 0 0;'>Читацький формуляр</p>
</div>

<table style='width:100%;margin-bottom:20px;'>
  <tr>
    <td style='width:50%;vertical-align:top;'>
      <table>
        <tr><td style='color:#546E7A;font-size:12px;padding:3px 8px 3px 0;'>ПІБ:</td>
            <td style='font-weight:600;'>{user.last_name} {user.first_name}</td></tr>
        <tr><td style='color:#546E7A;font-size:12px;padding:3px 8px 3px 0;'>Група:</td>
            <td style='font-weight:600;'>{user.academic_group}</td></tr>
        <tr><td style='color:#546E7A;font-size:12px;padding:3px 8px 3px 0;'>ID:</td>
            <td>{user.user_id}</td></tr>
      </table>
    </td>
    <td style='width:50%;vertical-align:top;'>
      <table>
        <tr><td style='color:#546E7A;font-size:12px;padding:3px 8px 3px 0;'>Email:</td>
            <td>{user.email or '—'}</td></tr>
        <tr><td style='color:#546E7A;font-size:12px;padding:3px 8px 3px 0;'>Телефон:</td>
            <td>{user.phone or '—'}</td></tr>
        <tr><td style='color:#546E7A;font-size:12px;padding:3px 8px 3px 0;'>На руках:</td>
            <td style='color:{"#E65100" if active>0 else "#1E7E34"};font-weight:600;'>{active} документів</td></tr>
      </table>
    </td>
  </tr>
</table>

<h3 style='color:#1A3C5E;border-bottom:2px solid #1A3C5E;padding-bottom:6px;'>Історія видач</h3>
<table style='width:100%;border-collapse:collapse;font-size:13px;'>
  <thead>
    <tr style='background:#1A3C5E;color:white;'>
      <th style='padding:8px;text-align:left;'>#</th>
      <th style='padding:8px;text-align:left;'>Документ</th>
      <th style='padding:8px;text-align:left;'>Видано</th>
      <th style='padding:8px;text-align:left;'>Повернено</th>
      <th style='padding:8px;text-align:left;'>Статус</th>
    </tr>
  </thead>
  <tbody>{rows}</tbody>
</table>

<p style='margin-top:24px;font-size:11px;color:#999;text-align:center;border-top:1px solid #eee;padding-top:10px;'>
  Дата реєстрації: {user.created_at or '—'}  |  Сформовано системою обліку бібліотеки
</p>
</body></html>"""


class PrintCardDialog(QDialog):
    def __init__(self, parent, user, issuances):
        super().__init__(parent)
        self.setWindowTitle(f"Формуляр — {user.last_name} {user.first_name}")
        self.resize(660, 520)
        self.setStyleSheet(f"QDialog {{ background: {BG}; }}")
        self._html = _card_html(user, issuances)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        # Кнопки
        btn_row = QHBoxLayout()
        btn_print = QPushButton("🖨️  Друкувати")
        btn_print.setFixedHeight(36)
        btn_print.setCursor(Qt.PointingHandCursor)
        btn_print.setStyleSheet(btn_style(PRIMARY_LIGHT, PRIMARY))
        btn_print.clicked.connect(self._print)

        btn_close = QPushButton("Закрити")
        btn_close.setFixedHeight(36)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{ background: white; color: {TEXT}; border: 1.5px solid {BORDER};
                           border-radius: 7px; font-size: 13px; padding: 0 16px; }}
            QPushButton:hover {{ background: #F5F5F5; }}
        """)
        btn_close.clicked.connect(self.close)
        btn_row.addWidget(btn_print); btn_row.addStretch(); btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

        # Перегляд
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setHtml(self._html)
        self.preview.setStyleSheet(f"""
            QTextEdit {{ border: 1px solid {BORDER}; border-radius: 8px;
                         background: white; font-size: 13px; }}
        """)
        layout.addWidget(self.preview)

    def _print(self):
        try:
            printer = QPrinter(QPrinter.HighResolution)
            dlg = QPrintDialog(printer, self)
            if dlg.exec_() == QPrintDialog.Accepted:
                self.preview.print_(printer)
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Помилка друку", str(e))
