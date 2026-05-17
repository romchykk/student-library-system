"""
Перевикористовувані UI-компоненти.
"""
from PyQt5.QtWidgets import (
    QPushButton, QFrame, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QSizePolicy, QWidget, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor
from gui.styles import (
    btn_style, PRIMARY, PRIMARY_LIGHT, SUCCESS, SUCCESS_LIGHT,
    DANGER, DANGER_LIGHT, WARNING, WARNING_LIGHT, PURPLE, PURPLE_LIGHT,
    GRAY_DARK, WHITE, BORDER, BG, TEXT, TEXT_LIGHT, PRIMARY_DARK
)


# ── Кнопки ────────────────────────────────────────────────────────────────────

class Btn(QPushButton):
    """Стандартна кнопка з tooltip."""
    def __init__(self, text, color=PRIMARY_LIGHT, hover=PRIMARY,
                 tooltip="", height=36, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(height)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(btn_style(color, hover))
        if tooltip:
            self.setToolTip(tooltip)


class BtnAdd(Btn):
    def __init__(self, text="➕  Додати", tooltip="Додати новий запис", **kw):
        super().__init__(text, SUCCESS_LIGHT, SUCCESS, tooltip, **kw)

class BtnEdit(Btn):
    def __init__(self, text="✏️  Редагувати", tooltip="Редагувати вибраний запис", **kw):
        super().__init__(text, PRIMARY_LIGHT, PRIMARY, tooltip, **kw)

class BtnDelete(Btn):
    def __init__(self, text="🗑  Видалити", tooltip="Видалити вибраний запис", **kw):
        super().__init__(text, DANGER_LIGHT, DANGER, tooltip, **kw)

class BtnAction(Btn):
    def __init__(self, text, tooltip="", **kw):
        super().__init__(text, WARNING_LIGHT, WARNING, tooltip, **kw)

class BtnPurple(Btn):
    def __init__(self, text, tooltip="", **kw):
        super().__init__(text, PURPLE_LIGHT, PURPLE, tooltip, **kw)

class BtnGray(Btn):
    def __init__(self, text, tooltip="", **kw):
        super().__init__(text, GRAY_DARK, "#263238", tooltip, **kw)


# ── Статистична картка ────────────────────────────────────────────────────────

class StatCard(QFrame):
    """Картка статистики з іконкою, числом і підписом."""
    def __init__(self, icon: str, label: str, value: int, accent: str, parent=None):
        super().__init__(parent)
        self.setFixedHeight(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border-radius: 12px;
                border-left: 5px solid {accent};
                border-top: 1px solid {BORDER};
                border-right: 1px solid {BORDER};
                border-bottom: 1px solid {BORDER};
            }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 12)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 32px; min-width: 42px;")
        icon_lbl.setAlignment(Qt.AlignCenter)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        self._val_lbl = QLabel(str(value))
        self._val_lbl.setStyleSheet(
            f"font-size: 28px; font-weight: 700; color: {accent}; background: transparent;"
        )
        name_lbl = QLabel(label)
        name_lbl.setStyleSheet(
            f"font-size: 11px; color: {TEXT_LIGHT}; font-weight: 500; background: transparent;"
        )
        text_col.addWidget(self._val_lbl)
        text_col.addWidget(name_lbl)

        layout.addWidget(icon_lbl)
        layout.addLayout(text_col)
        layout.addStretch()

    def set_value(self, val: int):
        self._val_lbl.setText(str(val))


# ── Панель пошуку + сортування ────────────────────────────────────────────────

class SearchBar(QWidget):
    """Рядок пошуку з іконкою."""
    def __init__(self, placeholder="Пошук...", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.inp = QLineEdit()
        self.inp.setPlaceholderText(f"🔍  {placeholder}")
        self.inp.setFixedHeight(38)
        self.inp.setStyleSheet(f"""
            QLineEdit {{
                border: 1.5px solid {BORDER};
                border-radius: 19px;
                padding: 0 16px;
                font-size: 13px;
                background: {WHITE};
            }}
            QLineEdit:focus {{
                border-color: {PRIMARY_LIGHT};
                background: #F0F7FF;
            }}
        """)
        layout.addWidget(self.inp)

    def text(self): return self.inp.text()
    def connect(self, slot): self.inp.textChanged.connect(slot)
    def clear(self): self.inp.clear()


# ── Заголовок секції ──────────────────────────────────────────────────────────

class SectionHeader(QWidget):
    """Заголовок з лінією під ним."""
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        lbl = QLabel(title)
        lbl.setStyleSheet(f"""
            font-size: 18px; font-weight: 700;
            color: {PRIMARY}; padding: 4px 0;
        """)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFixedHeight(2)
        line.setStyleSheet(f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {PRIMARY_LIGHT},stop:1 transparent);")

        layout.addWidget(lbl)
        layout.addWidget(line)


# ── Порожній стан таблиці ─────────────────────────────────────────────────────

class EmptyState(QWidget):
    """Показується коли таблиця порожня."""
    def __init__(self, icon="📭", message="Немає даних", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 48px;")
        icon_lbl.setAlignment(Qt.AlignCenter)

        msg_lbl = QLabel(message)
        msg_lbl.setStyleSheet(f"font-size: 15px; color: {TEXT_LIGHT};")
        msg_lbl.setAlignment(Qt.AlignCenter)

        layout.addWidget(icon_lbl)
        layout.addWidget(msg_lbl)
