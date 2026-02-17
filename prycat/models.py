"""LogEntry data class, LogcatModel (QAbstractTableModel), LogcatFilterProxy."""

from __future__ import annotations

import re
from collections import deque
from typing import Any, NamedTuple

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt

from .theme import TEXT, priority_color

COLUMNS = ("Time", "PID", "TID", "Level", "Tag", "Message")
PRIORITY_ORDER = {"V": 0, "D": 1, "I": 2, "W": 3, "E": 4, "F": 5, "S": 6}


class LogEntry(NamedTuple):
    timestamp: str
    pid: str
    tid: str
    priority: str
    tag: str
    message: str


class LogcatModel(QAbstractTableModel):
    def __init__(self, maxlen: int = 500_000, parent=None):
        super().__init__(parent)
        self._data: deque[LogEntry] = deque(maxlen=maxlen)
        self._maxlen = maxlen

    # ── Qt interface ────────────────────────────────────
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(COLUMNS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None
        entry = self._data[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            return entry[col]
        if role == Qt.ForegroundRole:
            return priority_color(entry.priority)
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return COLUMNS[section]
        return None

    # ── Mutation ────────────────────────────────────────
    def append_batch(self, entries: list[LogEntry]) -> None:
        if not entries:
            return

        # If batch alone exceeds maxlen, only keep the tail
        if len(entries) > self._maxlen:
            entries = entries[-self._maxlen:]

        count = len(entries)
        current = len(self._data)
        overflow = max(0, current + count - self._maxlen)

        # Only evict up to what we actually have
        evict = min(overflow, current)
        if evict > 0:
            self.beginRemoveRows(QModelIndex(), 0, evict - 1)
            for _ in range(evict):
                self._data.popleft()
            self.endRemoveRows()

        # Insert new rows (deque maxlen handles any remaining overflow)
        new_start = len(self._data)
        self.beginInsertRows(QModelIndex(), new_start, new_start + count - 1)
        self._data.extend(entries)
        self.endInsertRows()

    def clear_all(self) -> None:
        self.beginResetModel()
        self._data.clear()
        self.endResetModel()

    @property
    def total_count(self) -> int:
        return len(self._data)

    @property
    def buffer_percent(self) -> float:
        if self._maxlen == 0:
            return 0.0
        return len(self._data) / self._maxlen * 100


class LogcatFilterProxy(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDynamicSortFilter(False)

        self._text: str = ""
        self._text_re: re.Pattern | None = None
        self._use_regex: bool = False
        self._tags: set[str] = set()
        self._min_priority: int = 0  # V=0 means accept all
        self._pid: str = ""

    # ── Filter setters ──────────────────────────────────
    def _refilter(self) -> None:
        self.beginFilterChange()
        self.endFilterChange()

    def set_text_filter(self, text: str, use_regex: bool = False) -> None:
        self._use_regex = use_regex
        if use_regex:
            try:
                self._text_re = re.compile(text, re.IGNORECASE)
            except re.error:
                self._text_re = None
            self._text = ""
        else:
            self._text = text.lower()
            self._text_re = None
        self._refilter()

    def set_tag_filter(self, tags: set[str]) -> None:
        self._tags = tags
        self._refilter()

    def set_min_priority(self, level: str) -> None:
        self._min_priority = PRIORITY_ORDER.get(level, 0)
        self._refilter()

    def set_pid_filter(self, pid: str) -> None:
        self._pid = pid.strip()
        self._refilter()

    # ── Core filter ─────────────────────────────────────
    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        model: LogcatModel = self.sourceModel()
        if source_row >= len(model._data):
            return False
        entry = model._data[source_row]

        # Priority check (cheapest)
        if PRIORITY_ORDER.get(entry.priority, 0) < self._min_priority:
            return False

        # PID check
        if self._pid and entry.pid != self._pid:
            return False

        # Tag check
        if self._tags and entry.tag not in self._tags:
            return False

        # Text search (most expensive — last)
        if self._text_re is not None:
            haystack = f"{entry.tag} {entry.message}"
            if not self._text_re.search(haystack):
                return False
        elif self._text:
            haystack = f"{entry.tag} {entry.message}".lower()
            if self._text not in haystack:
                return False

        return True
