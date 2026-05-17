# LogWatcher

**LogWatcher** is a tiny Python utility for watching log files in real time.

## Features
- Real‑time tail of any text log file.
- Optional keyword filtering (multiple keywords, case‑insensitive).
- Structured JSON output to stdout or a separate file.
- Configurable log level for the tool itself.
- Cross‑platform (Windows, macOS, Linux).

## Installation
```bash
# Clone the repo
git clone https://github.com/yourname/logwatcher.git
cd logwatcher
# Install dependencies (only the standard library is required, but you may want to use a virtualenv)
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt  # file is empty for now
```

## Usage
```bash
python logwatcher.py -f /var/log/syslog -k error warning -o output.json
```

- `-f/--file` – Path to the log file to watch (required).
- `-k/--keyword` – One or more keywords to filter lines. If omitted, all lines are shown.
- `-o/--output` – Optional file to write JSON‑encoded log entries.
- `-l/--log-level` – Set the internal logger level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). Default is `INFO`.

Press **Ctrl‑C** to stop.

## Contributing
Feel free to open issues or submit pull requests. Please keep the code style consistent with the existing code (PEP 8, type hints, docstrings).

## License
MIT – see the [LICENSE](LICENSE) file.
