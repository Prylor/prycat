"""CLI entry point for prycat: ADB Logcat GUI Viewer."""

import argparse
import sys

from PySide6.QtWidgets import QApplication

from prycat.app import create_app


def parse_tags(tags_str: str) -> list[str]:
    """Parse comma-separated tag:priority pairs into ADB filter specs."""
    if not tags_str:
        return []
    filters = []
    for pair in tags_str.split(","):
        pair = pair.strip()
        if pair:
            filters.append(pair)
    return filters


def main():
    parser = argparse.ArgumentParser(
        prog="prycat",
        description="ADB Logcat GUI Viewer — Catppuccin-themed, high-performance log viewer",
    )
    parser.add_argument(
        "--adb-path", default="adb", help="Path to adb executable (default: adb)"
    )
    parser.add_argument(
        "-s", "--device", default=None, help="Target device serial number"
    )
    parser.add_argument(
        "-p", "--package", default=None, help="Package name to filter by PID"
    )
    parser.add_argument(
        "--tags", default="", help="Comma-separated tag:priority pairs (e.g. MyTag:D,System:W)"
    )
    parser.add_argument(
        "--min-level",
        default="V",
        choices=["V", "D", "I", "W", "E", "F"],
        help="Minimum log priority level (default: V)",
    )
    parser.add_argument(
        "--buffer",
        default=None,
        choices=["main", "system", "crash", "all"],
        help="Logcat buffer to read (default: main)",
    )
    parser.add_argument(
        "--buffer-size",
        type=int,
        default=500_000,
        help="Max log entries to keep in memory (default: 500000)",
    )

    args = parser.parse_args()
    args.tag_filters = parse_tags(args.tags)

    app = QApplication(sys.argv)
    window = create_app(app, args)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
