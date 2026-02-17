"""Toolbar: device selector, connect/disconnect, pause, clear, export."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)


class Toolbar(QWidget):
    connect_requested = Signal()
    disconnect_requested = Signal()
    pause_toggled = Signal(bool)
    clear_requested = Signal()
    export_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("toolbar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        # Device selector
        layout.addWidget(QLabel("Device:"))
        self._device_combo = QComboBox()
        self._device_combo.setEditable(True)
        self._device_combo.setMinimumWidth(180)
        layout.addWidget(self._device_combo)

        # Refresh devices
        self._refresh_btn = QPushButton("Refresh")
        layout.addWidget(self._refresh_btn)

        # Package filter
        layout.addWidget(QLabel("Package:"))
        self._package_edit = QLineEdit()
        self._package_edit.setPlaceholderText("com.example.app")
        self._package_edit.setMinimumWidth(180)
        layout.addWidget(self._package_edit)

        # Spacer
        layout.addStretch()

        # Connect / Disconnect
        self._connect_btn = QPushButton("Connect")
        self._connect_btn.setObjectName("connect_btn")
        layout.addWidget(self._connect_btn)

        self._disconnect_btn = QPushButton("Disconnect")
        self._disconnect_btn.setObjectName("disconnect_btn")
        self._disconnect_btn.setEnabled(False)
        layout.addWidget(self._disconnect_btn)

        # Pause
        self._pause_btn = QPushButton("Pause")
        self._pause_btn.setCheckable(True)
        layout.addWidget(self._pause_btn)

        # Clear
        self._clear_btn = QPushButton("Clear")
        layout.addWidget(self._clear_btn)

        # Export
        self._export_btn = QPushButton("Export")
        layout.addWidget(self._export_btn)

        # Signals
        self._connect_btn.clicked.connect(self.connect_requested.emit)
        self._disconnect_btn.clicked.connect(self.disconnect_requested.emit)
        self._pause_btn.toggled.connect(self.pause_toggled.emit)
        self._clear_btn.clicked.connect(self.clear_requested.emit)
        self._export_btn.clicked.connect(self.export_requested.emit)

    # ── Public API ──────────────────────────────────────
    @property
    def refresh_button(self) -> QPushButton:
        return self._refresh_btn

    def current_device(self) -> str:
        return self._device_combo.currentText().strip()

    def current_package(self) -> str:
        return self._package_edit.text().strip()

    def set_device(self, device: str) -> None:
        self._device_combo.setCurrentText(device)

    def set_package(self, package: str) -> None:
        self._package_edit.setText(package)

    def set_devices(self, devices: list[str]) -> None:
        current = self._device_combo.currentText()
        self._device_combo.clear()
        self._device_combo.addItems(devices)
        if current in devices:
            self._device_combo.setCurrentText(current)

    def set_connected(self, connected: bool) -> None:
        self._connect_btn.setEnabled(not connected)
        self._disconnect_btn.setEnabled(connected)
        self._device_combo.setEnabled(not connected)
        self._package_edit.setEnabled(not connected)
        self._refresh_btn.setEnabled(not connected)
