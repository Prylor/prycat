"""FilterBar: text search, tag filter, priority dropdown, PID filter."""

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QWidget,
)


class FilterBar(QWidget):
    text_filter_changed = Signal(str, bool)  # (text, is_regex)
    tag_filter_changed = Signal(set)
    priority_changed = Signal(str)
    pid_filter_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("filter_bar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        # Search
        layout.addWidget(QLabel("Search:"))
        self._search = QLineEdit()
        self._search.setPlaceholderText("Filter logs...")
        self._search.setClearButtonEnabled(True)
        self._search.setMinimumWidth(200)
        layout.addWidget(self._search, 1)

        # Regex toggle
        self._regex_cb = QCheckBox("Regex")
        layout.addWidget(self._regex_cb)

        # Tag filter
        layout.addWidget(QLabel("Tags:"))
        self._tags = QLineEdit()
        self._tags.setPlaceholderText("tag1,tag2,...")
        self._tags.setMaximumWidth(180)
        layout.addWidget(self._tags)

        # Priority dropdown
        layout.addWidget(QLabel("Level:"))
        self._priority = QComboBox()
        self._priority.addItems(["V", "D", "I", "W", "E", "F"])
        self._priority.setCurrentIndex(0)
        self._priority.setMaximumWidth(70)
        layout.addWidget(self._priority)

        # PID filter
        layout.addWidget(QLabel("PID:"))
        self._pid = QLineEdit()
        self._pid.setPlaceholderText("PID")
        self._pid.setMaximumWidth(80)
        layout.addWidget(self._pid)

        # Debounce timer for text search (300ms)
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(300)
        self._debounce.timeout.connect(self._emit_text_filter)

        # Connections
        self._search.textChanged.connect(lambda: self._debounce.start())
        self._regex_cb.toggled.connect(lambda: self._debounce.start())
        self._tags.editingFinished.connect(self._emit_tag_filter)
        self._priority.currentTextChanged.connect(self.priority_changed.emit)
        self._pid.editingFinished.connect(lambda: self.pid_filter_changed.emit(self._pid.text()))

    def _emit_text_filter(self) -> None:
        self.text_filter_changed.emit(self._search.text(), self._regex_cb.isChecked())

    def _emit_tag_filter(self) -> None:
        raw = self._tags.text().strip()
        tags = {t.strip() for t in raw.split(",") if t.strip()} if raw else set()
        self.tag_filter_changed.emit(tags)
