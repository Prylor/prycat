"""LogTableView: virtual-scrolling QTableView for logcat entries."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QAbstractItemView, QApplication, QHeaderView, QMenu, QTableView


class LogTableView(QTableView):
    open_detail_requested = Signal(int)    # proxy row index
    filter_by_tag_requested = Signal(str)  # tag value

    def __init__(self, parent=None):
        super().__init__(parent)
        self._auto_scroll = True

        # Performance: uniform row heights avoids per-row height queries
        self.verticalHeader().setDefaultSectionSize(22)
        self.verticalHeader().setMinimumSectionSize(22)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().hide()

        # Selection
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Appearance
        self.setShowGrid(False)
        self.setWordWrap(False)
        self.setSortingEnabled(False)
        self.setAlternatingRowColors(True)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        # Context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        # Column widths
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    def apply_column_widths(self) -> None:
        """Call after setting a model to fix column widths."""
        widths = [160, 60, 60, 50, 150]
        for i, w in enumerate(widths):
            self.setColumnWidth(i, w)

    @property
    def auto_scroll(self) -> bool:
        return self._auto_scroll

    def scrollContentsBy(self, dx: int, dy: int) -> None:
        super().scrollContentsBy(dx, dy)
        sb = self.verticalScrollBar()
        # Auto-scroll is on when scrollbar is near the bottom
        self._auto_scroll = sb.value() >= sb.maximum() - 5

    def scroll_to_bottom(self) -> None:
        if self._auto_scroll:
            self.scrollToBottom()

    def keyPressEvent(self, event) -> None:
        if event.matches(QKeySequence.Copy):
            self._copy_selection()
            return
        super().keyPressEvent(event)

    def _copy_selection(self) -> None:
        indexes = self.selectionModel().selectedIndexes()
        if not indexes:
            return

        # Group by row
        rows: dict[int, list] = {}
        for idx in indexes:
            rows.setdefault(idx.row(), []).append(idx)

        lines = []
        for row in sorted(rows):
            cells = sorted(rows[row], key=lambda i: i.column())
            line = "\t".join(idx.data(Qt.DisplayRole) or "" for idx in cells)
            lines.append(line)

        QApplication.clipboard().setText("\n".join(lines))

    # ── Context menu ────────────────────────────────────
    def _show_context_menu(self, pos) -> None:
        index = self.indexAt(pos)
        if not index.isValid():
            return

        row = index.row()
        model = self.model()

        # Read tag from column 4
        tag = model.index(row, 4).data(Qt.DisplayRole) or ""

        menu = QMenu(self)

        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self._copy_selection)
        menu.addAction(copy_action)

        menu.addSeparator()

        detail_action = QAction("Open in Window", self)
        detail_action.triggered.connect(lambda: self.open_detail_requested.emit(row))
        menu.addAction(detail_action)

        menu.addSeparator()

        tag_action = QAction(f"Filter by Tag '{tag}'", self)
        tag_action.triggered.connect(lambda: self.filter_by_tag_requested.emit(tag))
        menu.addAction(tag_action)

        menu.exec(self.viewport().mapToGlobal(pos))
