"""Catppuccin Mocha theme: QSS stylesheet and priority colors."""

from PySide6.QtGui import QColor

# Palette built on #121212 / #1e1e1e
MAUVE = "#cba6f7"
RED = "#f38ba8"
YELLOW = "#f9e2af"
GREEN = "#a6e3a1"
BLUE = "#89b4fa"
TEXT = "#e0e0e0"
SUBTEXT1 = "#b0b0b0"
SUBTEXT0 = "#909090"
OVERLAY1 = "#707070"
OVERLAY0 = "#585858"
SURFACE2 = "#424242"
SURFACE1 = "#333333"
SURFACE0 = "#282828"
BASE = "#1e1e1e"
MANTLE = "#181818"
CRUST = "#121212"

PRIORITY_COLORS = {
    "V": QColor(OVERLAY1),   # Verbose — gray
    "D": QColor(BLUE),       # Debug — blue
    "I": QColor(GREEN),      # Info — green
    "W": QColor(YELLOW),     # Warning — yellow
    "E": QColor(RED),        # Error — red
    "F": QColor(MAUVE),      # Fatal — mauve
    "S": QColor(OVERLAY0),   # Silent — dim
}

_DEFAULT_COLOR = QColor(TEXT)


def priority_color(level: str) -> QColor:
    return PRIORITY_COLORS.get(level, _DEFAULT_COLOR)


def get_stylesheet() -> str:
    return f"""
/* ── Global ─────────────────────────────────────────── */
* {{
    font-family: "Cascadia Code", "Consolas", "JetBrains Mono", monospace;
    font-size: 13px;
}}

QMainWindow {{
    background-color: {BASE};
    color: {TEXT};
}}

/* ── Table ──────────────────────────────────────────── */
QTableView {{
    background-color: {BASE};
    alternate-background-color: {MANTLE};
    color: {TEXT};
    gridline-color: transparent;
    border: none;
    selection-background-color: {SURFACE1};
    selection-color: {TEXT};
    outline: none;
}}

QHeaderView::section {{
    background-color: {MANTLE};
    color: {SUBTEXT1};
    border: none;
    border-bottom: 1px solid {SURFACE1};
    padding: 4px 8px;
    font-weight: bold;
}}

/* ── Toolbar / Filter area ──────────────────────────── */
QToolBar {{
    background-color: {MANTLE};
    border: none;
    spacing: 6px;
    padding: 4px;
}}

QWidget#toolbar, QWidget#filter_bar {{
    background-color: {MANTLE};
    border-bottom: 1px solid {SURFACE0};
}}

/* ── Buttons ────────────────────────────────────────── */
QPushButton {{
    background-color: {SURFACE0};
    color: {TEXT};
    border: 1px solid {SURFACE1};
    border-radius: 4px;
    padding: 4px 14px;
    min-height: 22px;
}}
QPushButton:hover {{
    background-color: {SURFACE1};
    border-color: {OVERLAY0};
}}
QPushButton:pressed {{
    background-color: {SURFACE2};
}}
QPushButton:disabled {{
    color: {OVERLAY0};
    background-color: {SURFACE0};
    border-color: {SURFACE0};
}}
QPushButton:checked {{
    background-color: {SURFACE1};
    border-color: {BLUE};
    color: {BLUE};
}}

QPushButton#connect_btn {{
    border-color: {GREEN};
    color: {GREEN};
}}
QPushButton#connect_btn:hover {{
    background-color: {SURFACE1};
}}
QPushButton#disconnect_btn {{
    border-color: {RED};
    color: {RED};
}}
QPushButton#disconnect_btn:hover {{
    background-color: {SURFACE1};
}}

/* ── Inputs ─────────────────────────────────────────── */
QLineEdit {{
    background-color: {SURFACE0};
    color: {TEXT};
    border: 1px solid {SURFACE1};
    border-radius: 4px;
    padding: 4px 8px;
    selection-background-color: {SURFACE2};
    min-height: 22px;
}}
QLineEdit:focus {{
    border-color: {BLUE};
}}

QComboBox {{
    background-color: {SURFACE0};
    color: {TEXT};
    border: 1px solid {SURFACE1};
    border-radius: 4px;
    padding: 4px 8px;
    min-height: 22px;
}}
QComboBox:hover {{
    border-color: {OVERLAY0};
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {SUBTEXT0};
    margin-right: 6px;
}}
QComboBox QAbstractItemView {{
    background-color: {SURFACE0};
    color: {TEXT};
    selection-background-color: {SURFACE1};
    selection-color: {TEXT};
    border: 1px solid {SURFACE1};
    outline: none;
}}

/* ── Checkbox ───────────────────────────────────────── */
QCheckBox {{
    color: {TEXT};
    spacing: 6px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {SURFACE2};
    border-radius: 3px;
    background-color: {SURFACE0};
}}
QCheckBox::indicator:checked {{
    background-color: {BLUE};
    border-color: {BLUE};
}}

/* ── Status bar ─────────────────────────────────────── */
QStatusBar {{
    background-color: {CRUST};
    color: {SUBTEXT0};
    border-top: 1px solid {SURFACE0};
    font-size: 12px;
}}
QStatusBar::item {{
    border: none;
}}

/* ── Scrollbars ─────────────────────────────────────── */
QScrollBar:vertical {{
    background-color: {MANTLE};
    width: 10px;
    margin: 0;
    border: none;
}}
QScrollBar::handle:vertical {{
    background-color: {SURFACE1};
    min-height: 30px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {SURFACE2};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}

QScrollBar:horizontal {{
    background-color: {MANTLE};
    height: 10px;
    margin: 0;
    border: none;
}}
QScrollBar::handle:horizontal {{
    background-color: {SURFACE1};
    min-width: 30px;
    border-radius: 5px;
}}
QScrollBar::handle:horizontal:hover {{
    background-color: {SURFACE2};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: none;
}}

/* ── Labels ─────────────────────────────────────────── */
QLabel {{
    color: {SUBTEXT1};
}}
"""
