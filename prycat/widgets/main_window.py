"""MainWindow: integration hub — drain loop, signal wiring, state management."""

from __future__ import annotations

import csv
import queue
import time

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFileDialog, QLabel, QMainWindow, QMessageBox, QVBoxLayout, QWidget

from ..models import LogcatFilterProxy, LogcatModel, LogEntry
from ..reader import AdbReader
from .filter_bar import FilterBar
from .log_detail import LogDetailWindow
from .log_table import LogTableView
from .toolbar import Toolbar


class MainWindow(QMainWindow):
    def __init__(
        self,
        adb_path: str = "adb",
        device: str | None = None,
        package: str | None = None,
        tag_filters: list[str] | None = None,
        min_level: str = "V",
        buffer: str | None = None,
        buffer_size: int = 500_000,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("prycat")
        self.resize(1200, 700)

        # Config
        self._adb_path = adb_path
        self._initial_device = device
        self._initial_package = package
        self._tag_filters = tag_filters or []
        self._initial_min_level = min_level
        self._buffer_name = buffer
        self._buffer_size = buffer_size

        # Core objects
        self._queue: queue.Queue[LogEntry | None] = queue.Queue(maxsize=10_000)
        self._model = LogcatModel(maxlen=buffer_size)
        self._proxy = LogcatFilterProxy()
        self._proxy.setSourceModel(self._model)
        self._reader: AdbReader | None = None
        self._paused = False
        self._detail_windows: list[LogDetailWindow] = []

        # Build UI
        self._build_ui()
        self._wire_signals()

        # Drain timer (50ms)
        self._drain_timer = QTimer(self)
        self._drain_timer.setInterval(50)
        self._drain_timer.timeout.connect(self._drain_queue)

        # Status bar
        self._status_conn = QLabel("Disconnected")
        self._status_lines = QLabel("0 / 0 lines")
        self._status_buf = QLabel("Buffer: 0%")
        self.statusBar().addWidget(self._status_conn, 1)
        self.statusBar().addPermanentWidget(self._status_lines)
        self.statusBar().addPermanentWidget(self._status_buf)

        # Apply initial CLI values
        if self._initial_device:
            self._toolbar.set_device(self._initial_device)
        if self._initial_package:
            self._toolbar.set_package(self._initial_package)
        if self._initial_min_level != "V":
            # Set the filter bar priority combo to match
            idx = self._filter_bar._priority.findText(self._initial_min_level)
            if idx >= 0:
                self._filter_bar._priority.setCurrentIndex(idx)

        # Refresh device list on startup
        self._refresh_devices()

        # Auto-connect if device provided
        if self._initial_device:
            QTimer.singleShot(200, self._on_connect)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._toolbar = Toolbar()
        layout.addWidget(self._toolbar)

        self._filter_bar = FilterBar()
        layout.addWidget(self._filter_bar)

        self._table = LogTableView()
        self._table.setModel(self._proxy)
        self._table.apply_column_widths()
        layout.addWidget(self._table, 1)

    def _wire_signals(self) -> None:
        # Toolbar
        self._toolbar.connect_requested.connect(self._on_connect)
        self._toolbar.disconnect_requested.connect(self._on_disconnect)
        self._toolbar.pause_toggled.connect(self._on_pause)
        self._toolbar.clear_requested.connect(self._on_clear)
        self._toolbar.export_requested.connect(self._on_export)
        self._toolbar.refresh_button.clicked.connect(self._refresh_devices)

        # Filter bar
        self._filter_bar.text_filter_changed.connect(self._proxy.set_text_filter)
        self._filter_bar.tag_filter_changed.connect(self._proxy.set_tag_filter)
        self._filter_bar.priority_changed.connect(self._proxy.set_min_priority)
        self._filter_bar.pid_filter_changed.connect(self._proxy.set_pid_filter)

        # Table context menu
        self._table.open_detail_requested.connect(self._open_log_detail)
        self._table.filter_by_tag_requested.connect(self._filter_bar.append_tag)

    # ── Actions ─────────────────────────────────────────
    def _refresh_devices(self) -> None:
        devices = AdbReader.list_devices(self._adb_path)
        self._toolbar.set_devices(devices)

    def _on_connect(self) -> None:
        device = self._toolbar.current_device() or None
        package = self._toolbar.current_package() or None

        pid = None
        if package:
            # Retry pidof a few times — ADB or the app may need a moment
            for attempt in range(3):
                pid = AdbReader.get_pid_for_package(self._adb_path, device, package)
                if pid:
                    break
                if attempt < 2:
                    time.sleep(0.5)

            if not pid:
                reply = QMessageBox.warning(
                    self,
                    "PID not found",
                    f"Could not resolve PID for '{package}'.\n"
                    "The app may not be running on the device.\n\n"
                    "Connect without package filter?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if reply == QMessageBox.No:
                    return

        # Clear the queue
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break

        self._reader = AdbReader(
            out_queue=self._queue,
            adb_path=self._adb_path,
            device=device,
            buffer=self._buffer_name,
            tag_filters=self._tag_filters,
            pid=pid,
        )
        self._reader.start()
        self._drain_timer.start()
        self._toolbar.set_connected(True)
        status = f"Connected: {device or 'default'}"
        if pid:
            status += f" (PID {pid})"
        elif package:
            status += " (no PID filter)"
        self._status_conn.setText(status)

    def _on_disconnect(self) -> None:
        if self._reader:
            self._reader.stop()
            self._reader = None
        self._drain_timer.stop()
        self._toolbar.set_connected(False)
        self._status_conn.setText("Disconnected")

    def _on_pause(self, paused: bool) -> None:
        self._paused = paused

    def _open_log_detail(self, proxy_row: int) -> None:
        model = self._proxy
        timestamp = model.index(proxy_row, 0).data() or ""
        pid = model.index(proxy_row, 1).data() or ""
        tid = model.index(proxy_row, 2).data() or ""
        priority = model.index(proxy_row, 3).data() or ""
        tag = model.index(proxy_row, 4).data() or ""
        message = model.index(proxy_row, 5).data() or ""

        win = LogDetailWindow(timestamp, pid, tid, priority, tag, message)
        self._detail_windows.append(win)
        win.destroyed.connect(lambda: self._detail_windows.remove(win) if win in self._detail_windows else None)
        win.show()

    def _on_clear(self) -> None:
        self._model.clear_all()
        self._update_status()

    def _on_export(self) -> None:
        path, selected_filter = QFileDialog.getSaveFileName(
            self, "Export Logs", "", "Text Files (*.txt);;CSV Files (*.csv)"
        )
        if not path:
            return

        rows = []
        for row in range(self._proxy.rowCount()):
            cells = []
            for col in range(self._proxy.columnCount()):
                idx = self._proxy.index(row, col)
                cells.append(idx.data() or "")
            rows.append(cells)

        if path.endswith(".csv"):
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Time", "PID", "TID", "Level", "Tag", "Message"])
                writer.writerows(rows)
        else:
            with open(path, "w", encoding="utf-8") as f:
                for cells in rows:
                    f.write("\t".join(cells) + "\n")

    # ── Drain loop ──────────────────────────────────────
    def _drain_queue(self) -> None:
        if self._paused:
            return

        batch: list[LogEntry] = []
        for _ in range(500):
            try:
                item = self._queue.get_nowait()
            except queue.Empty:
                break
            if item is None:
                # Reader stopped unexpectedly
                self._on_disconnect()
                return
            batch.append(item)

        if batch:
            self._model.append_batch(batch)
            self._proxy._refilter()
            self._table.scroll_to_bottom()
            self._update_status()

    def _update_status(self) -> None:
        filtered = self._proxy.rowCount()
        total = self._model.total_count
        self._status_lines.setText(f"{filtered} / {total} lines")
        self._status_buf.setText(f"Buffer: {self._model.buffer_percent:.0f}%")

    # ── Cleanup ─────────────────────────────────────────
    def closeEvent(self, event) -> None:
        if self._reader:
            self._reader.stop()
        self._drain_timer.stop()
        super().closeEvent(event)
