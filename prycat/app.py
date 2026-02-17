"""Application bootstrap: theme application and window creation."""

from PySide6.QtWidgets import QApplication

from .theme import get_stylesheet
from .widgets.main_window import MainWindow


def create_app(app: QApplication, args) -> MainWindow:
    app.setStyle("Fusion")
    app.setStyleSheet(get_stylesheet())

    window = MainWindow(
        adb_path=args.adb_path,
        device=args.device,
        package=args.package,
        tag_filters=args.tag_filters,
        min_level=args.min_level,
        buffer=args.buffer,
        buffer_size=args.buffer_size,
    )
    return window
