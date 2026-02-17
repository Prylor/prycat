"""Log detail window: shows a single log entry in a readable, styled view."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QTextEdit, QVBoxLayout, QWidget

from ..theme import BASE, BLUE, MANTLE, OVERLAY0, SURFACE0, SURFACE1, SUBTEXT0, TEXT, priority_color


class LogDetailWindow(QWidget):
    """Standalone window displaying a single log entry."""

    def __init__(self, timestamp: str, pid: str, tid: str, priority: str, tag: str, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Log — {tag}")
        self.setWindowFlags(Qt.Window)
        self.resize(720, 400)

        color = priority_color(priority).name()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header row
        header = QHBoxLayout()
        header.setSpacing(16)
        for label_text, value in [("Time", timestamp), ("PID", pid), ("TID", tid), ("Level", priority), ("Tag", tag)]:
            col = QVBoxLayout()
            col.setSpacing(2)
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"color: {SUBTEXT0}; font-size: 11px;")
            val = QLabel(value)
            val_style = f"color: {color}; font-size: 13px; font-weight: bold;" if label_text in ("Level", "Tag") else f"color: {TEXT}; font-size: 13px;"
            val.setStyleSheet(val_style)
            val.setTextInteractionFlags(Qt.TextSelectableByMouse)
            col.addWidget(lbl)
            col.addWidget(val)
            header.addLayout(col)
        header.addStretch()
        layout.addLayout(header)

        # Separator
        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {SURFACE1};")
        layout.addWidget(sep)

        # Message body
        body = QTextEdit()
        body.setReadOnly(True)
        body.setPlainText(message)
        body.setStyleSheet(
            f"QTextEdit {{"
            f"  background-color: {SURFACE0};"
            f"  color: {color};"
            f"  border: 1px solid {SURFACE1};"
            f"  border-radius: 6px;"
            f"  padding: 10px;"
            f"  font-size: 13px;"
            f"}}"
        )
        layout.addWidget(body, 1)

        # Window styling
        self.setStyleSheet(f"QWidget {{ background-color: {BASE}; }}")
