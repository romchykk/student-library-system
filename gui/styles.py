"""Централізовані стилі."""

PRIMARY       = "#1A3C5E"
PRIMARY_DARK  = "#0F2A45"
PRIMARY_LIGHT = "#2E6DA4"
SUCCESS       = "#1E7E34"
SUCCESS_LIGHT = "#28A745"
DANGER        = "#B71C1C"
DANGER_LIGHT  = "#DC3545"
WARNING       = "#E65100"
WARNING_LIGHT = "#F57C00"
PURPLE        = "#4A148C"
PURPLE_LIGHT  = "#6A1B9A"
GRAY_DARK     = "#37474F"
GRAY          = "#546E7A"
GRAY_LIGHT    = "#ECEFF1"
BG            = "#F5F7FA"
WHITE         = "#FFFFFF"
TEXT          = "#1A1A2E"
TEXT_LIGHT    = "#546E7A"
BORDER        = "#CFD8DC"
ALT_ROW       = "#F0F7FF"

APP_STYLE = f"""
* {{ font-family: 'Segoe UI', Arial, sans-serif; }}

QMainWindow, QDialog {{ background: {BG}; }}

/* ── Tabs ── */
QTabWidget::pane {{
    border: none; background: {BG}; padding-top: 4px;
}}
QTabBar::tab {{
    background: {GRAY_LIGHT}; color: {GRAY};
    padding: 11px 26px; font-size: 13px; font-weight: 600;
    border-top-left-radius: 8px; border-top-right-radius: 8px;
    margin-right: 4px; border-bottom: 3px solid transparent;
}}
QTabBar::tab:selected {{
    background: {WHITE}; color: {PRIMARY};
    border-bottom: 3px solid {PRIMARY_LIGHT};
}}
QTabBar::tab:hover:!selected {{
    background: #D6E4F7; color: {PRIMARY};
}}

/* ── Tables ──
   ВАЖЛИВО: item:selected має color:white щоб текст був видимий
*/
QTableWidget {{
    background: {WHITE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    gridline-color: #E3EAF2;
    font-size: 13px;
    outline: none;
}}
QTableWidget::item {{
    padding: 8px 10px;
    border: none;
    color: {TEXT};
}}
QTableWidget::item:selected {{
    background-color: {PRIMARY_LIGHT};
    color: {WHITE};
}}
QTableWidget::item:alternate {{
    background-color: {ALT_ROW};
    color: {TEXT};
}}
QTableWidget::item:alternate:selected {{
    background-color: {PRIMARY_LIGHT};
    color: {WHITE};
}}
QHeaderView::section {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #2060A0, stop:1 {PRIMARY});
    color: white;
    padding: 10px;
    font-weight: bold;
    font-size: 12px;
    border: none;
    border-right: 1px solid #1A4A80;
}}
QHeaderView::section:first {{ border-top-left-radius: 9px; }}
QHeaderView::section:last  {{ border-top-right-radius: 9px; border-right: none; }}

/* ── Inputs ── */
QLineEdit, QSpinBox, QComboBox, QTextEdit {{
    border: 1.5px solid {BORDER};
    border-radius: 7px;
    padding: 8px 12px;
    font-size: 13px;
    background: {WHITE};
    color: {TEXT};
}}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus {{
    border-color: {PRIMARY_LIGHT}; background: #F0F7FF;
}}
QLineEdit:hover, QComboBox:hover {{ border-color: {GRAY}; }}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    border: 1px solid {BORDER}; border-radius: 6px;
    background: white;
    selection-background-color: {PRIMARY_LIGHT};
    selection-color: white;
}}

/* ── Status bar ── */
QStatusBar {{
    background: {PRIMARY}; color: white;
    font-size: 12px; font-weight: 500;
    padding: 4px 12px;
    border-top: 1px solid {PRIMARY_DARK};
}}
QStatusBar::item {{ border: none; }}

/* ── Menu ── */
QMenuBar {{
    background: {PRIMARY}; color: white;
    font-size: 13px; padding: 2px 0;
    border-bottom: 1px solid {PRIMARY_DARK};
}}
QMenuBar::item {{ padding: 6px 14px; border-radius: 4px; }}
QMenuBar::item:selected {{ background: {PRIMARY_LIGHT}; }}
QMenu {{
    background: white; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 8px; padding: 4px;
}}
QMenu::item {{ padding: 8px 24px; border-radius: 5px; }}
QMenu::item:selected {{ background: {PRIMARY_LIGHT}; color: white; }}
QMenu::separator {{ height: 1px; background: {BORDER}; margin: 4px 8px; }}

/* ── ScrollBar ── */
QScrollBar:vertical {{
    border: none; background: {GRAY_LIGHT};
    width: 8px; border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: #B0BEC5; border-radius: 4px; min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: {GRAY}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

/* ── ToolTip ── */
QToolTip {{
    background: {PRIMARY_DARK}; color: white;
    border: none; border-radius: 5px;
    padding: 6px 10px; font-size: 12px;
}}

/* ── GroupBox ── */
QGroupBox {{
    border: 1.5px solid {BORDER}; border-radius: 8px;
    margin-top: 14px; padding: 10px;
    font-weight: bold; color: {PRIMARY};
}}
QGroupBox::title {{
    subcontrol-origin: margin; left: 12px;
    padding: 0 6px; color: {PRIMARY}; font-size: 13px;
}}

/* ── Checkbox ── */
QCheckBox {{ color: {TEXT}; font-size: 13px; spacing: 6px; }}
QCheckBox::indicator {{
    width: 16px; height: 16px; border-radius: 4px;
    border: 1.5px solid {BORDER}; background: white;
}}
QCheckBox::indicator:checked {{
    background: {PRIMARY_LIGHT}; border-color: {PRIMARY_LIGHT};
}}

/* ── MessageBox ── */
QMessageBox {{ background: white; }}
QMessageBox QPushButton {{
    background: {PRIMARY_LIGHT}; color: white;
    border-radius: 6px; padding: 6px 20px; min-width: 80px;
}}
QMessageBox QPushButton:hover {{ background: {PRIMARY}; }}
"""


def btn_style(bg, hover, text_color="white"):
    return f"""
        QPushButton {{
            background-color: {bg}; color: {text_color};
            border: none; border-radius: 7px;
            font-size: 13px; font-weight: 600; padding: 0 16px;
        }}
        QPushButton:hover {{ background-color: {hover}; }}
        QPushButton:pressed {{ opacity: 0.85; }}
        QPushButton:disabled {{ background-color: #CFD8DC; color: #90A4AE; }}
    """


CARD_STYLE = f"""
    QFrame {{
        background: {WHITE}; border-radius: 12px; border: 1px solid {BORDER};
    }}
"""
