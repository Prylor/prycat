# prycat

A fast, dark-themed GUI for viewing ADB logcat output in real time.

## About

prycat renders Android device logs in a responsive table that handles hundreds of thousands of lines without lag. It streams logcat output in a background thread, batches updates to the UI, and caps memory with a ring buffer — so it stays fast even during extended debug sessions.

## Features

- **Real-time streaming** — logs appear as they happen, no manual refresh
- **Package filtering** — filter by app package name (resolved to PID automatically)
- **Live filters** — search text, regex, tag, priority level, PID — all applied instantly
- **Virtual scrolling** — only visible rows are rendered, smooth at 500k+ lines
- **Memory-bounded** — configurable ring buffer evicts oldest entries automatically
- **Copy & export** — Ctrl+C selected rows, or export filtered results to .txt/.csv
- **Dark theme** — easy on the eyes for long sessions
- **Cross-platform** — runs anywhere Python and ADB are available

## Installation

Requires Python 3.10+ and ADB on your PATH.

```bash
pip install git+https://github.com/Prylor/prycat.git
```

Or from a local clone:

```bash
git clone https://github.com/Prylor/prycat.git
cd prycat
pip install .
```

## Usage

```bash
# Launch the GUI
prycat

# Connect to a specific device and filter by package
prycat -s emulator-5554 -p com.example.app

# Set minimum log level and read from all buffers
prycat --min-level W --buffer all

# Pre-filter by tags
prycat --tags "MyTag:D,NetworkLib:W"
```

### CLI Options

| Flag | Description | Default |
|------|-------------|---------|
| `--adb-path` | Path to adb executable | `adb` |
| `-s`, `--device` | Target device serial | auto-detect |
| `-p`, `--package` | Package name (resolves to PID) | none |
| `--tags` | Comma-separated `tag:priority` pairs | none |
| `--min-level` | Minimum priority: V, D, I, W, E, F | V |
| `--buffer` | Logcat buffer: main, system, crash, all | main |
| `--buffer-size` | Max entries kept in memory | 500000 |

### In the GUI

- **Connect/Disconnect** — start or stop log streaming
- **Pause** — freeze the display; logs keep buffering in the background
- **Filters** — type in the search box, pick a priority level, or enter comma-separated tags
- **Regex** — check the Regex box to use regular expressions in search
- **Auto-scroll** — follows new logs; scroll up to pause, scroll back to bottom to resume
- **Ctrl+C** — copies selected rows as tab-separated text
- **Export** — save filtered logs as .txt or .csv

## Development

```bash
git clone https://github.com/Prylor/prycat.git
cd prycat
pip install -e .
python main.py
```

## License

MIT
