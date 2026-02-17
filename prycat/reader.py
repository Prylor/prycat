"""ADB logcat reader: subprocess management, line parsing, device listing."""

from __future__ import annotations

import queue
import re
import subprocess
import threading
from typing import Optional

from .models import LogEntry

# threadtime format: "MM-DD HH:MM:SS.mmm  PID  TID LEVEL TAG     : message"
_LOGCAT_RE = re.compile(
    r"^(\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3})\s+"
    r"(\d+)\s+(\d+)\s+"
    r"([VDIWEFS])\s+"
    r"(.+?)\s*:\s(.*)$"
)


class AdbReader:
    """Reads ADB logcat in a background thread, pushes LogEntry to a queue."""

    def __init__(
        self,
        out_queue: queue.Queue,
        adb_path: str = "adb",
        device: str | None = None,
        buffer: str | None = None,
        tag_filters: list[str] | None = None,
        pid: str | None = None,
    ):
        self._queue = out_queue
        self._adb_path = adb_path
        self._device = device
        self._buffer = buffer
        self._tag_filters = tag_filters or []
        self._pid = pid
        self._stop_event = threading.Event()
        self._process: Optional[subprocess.Popen] = None
        self._thread: Optional[threading.Thread] = None

    def build_command(self) -> list[str]:
        cmd = [self._adb_path]
        if self._device:
            cmd.extend(["-s", self._device])
        cmd.extend(["logcat", "-v", "threadtime"])
        if self._buffer:
            if self._buffer == "all":
                cmd.extend(["-b", "main,system,crash"])
            else:
                cmd.extend(["-b", self._buffer])
        if self._pid:
            cmd.extend(["--pid", self._pid])
        if self._tag_filters:
            cmd.extend(self._tag_filters)
            cmd.append("*:S")
        return cmd

    def start(self) -> None:
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        cmd = self.build_command()
        try:
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW
                if hasattr(subprocess, "CREATE_NO_WINDOW")
                else 0,
            )
        except FileNotFoundError:
            self._queue.put(None)
            return

        for line in self._process.stdout:
            if self._stop_event.is_set():
                break
            line = line.rstrip("\n\r")
            entry = self._parse_line(line)
            if entry is None:
                continue
            try:
                self._queue.put_nowait(entry)
            except queue.Full:
                pass  # drop under backpressure

        # Signal that the reader has stopped
        self._queue.put(None)

    @staticmethod
    def _parse_line(line: str) -> LogEntry | None:
        m = _LOGCAT_RE.match(line)
        if not m:
            return None
        return LogEntry(
            timestamp=m.group(1),
            pid=m.group(2),
            tid=m.group(3),
            priority=m.group(4),
            tag=m.group(5).strip(),
            message=m.group(6),
        )

    def stop(self) -> None:
        self._stop_event.set()
        if self._process:
            try:
                self._process.terminate()
            except OSError:
                pass
            self._process = None
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None

    @staticmethod
    def list_devices(adb_path: str = "adb") -> list[str]:
        try:
            result = subprocess.run(
                [adb_path, "devices"],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW
                if hasattr(subprocess, "CREATE_NO_WINDOW")
                else 0,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []
        devices = []
        for line in result.stdout.splitlines()[1:]:
            parts = line.strip().split("\t")
            if len(parts) == 2 and parts[1] == "device":
                devices.append(parts[0])
        return devices

    @staticmethod
    def get_pid_for_package(adb_path: str, device: str | None, package: str) -> str | None:
        cmd = [adb_path]
        if device:
            cmd.extend(["-s", device])
        cmd.extend(["shell", "pidof", package])
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW
                if hasattr(subprocess, "CREATE_NO_WINDOW")
                else 0,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return None
        pid = result.stdout.strip().split()[0] if result.stdout.strip() else None
        return pid
