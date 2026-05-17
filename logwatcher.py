#!/usr/bin/env python3
"""logwatcher.py – Real‑time log file tailer with optional keyword filtering.

Features
--------
- Tail a file safely on any OS.
- Filter lines by one or more keywords (case‑insensitive).
- Emit JSON objects to stdout or a user‑specified output file.
- Internal logging with configurable verbosity.

Author: TopherBot <topherbot@proton.me>
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Iterable, List, Optional

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

def configure_logger(level: str) -> logging.Logger:
    """Create and configure a module‑level logger.

    Parameters
    ----------
    level: str
        One of ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``.
    """
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")
    logger = logging.getLogger("logwatcher")
    logger.setLevel(numeric_level)
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.handlers = []  # Remove any duplicated handlers
    logger.addHandler(handler)
    return logger

# ---------------------------------------------------------------------------
# Core functionality
# ---------------------------------------------------------------------------

def follow(file_path: Path, logger: logging.Logger) -> Iterable[str]:
    """Yield new lines as they are appended to *file_path*.

    This implements a simple ``tail -f`` behaviour using a polling loop.
    The function is a generator that never returns unless the file is deleted
    or an unrecoverable error occurs.
    """
    logger.debug("Opening file %s for tailing", file_path)
    with file_path.open("r", encoding="utf-8", errors="replace") as f:
        # Move to the end of file initially – we only want *new* lines.
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if line:
                yield line.rstrip("\n")
            else:
                # No new data, wait a bit before retrying.
                time.sleep(0.2)
                # If the file was rotated/truncated, reposition.
                if f.tell() > file_path.stat().st_size:
                    logger.info("File was truncated, seeking to start")
                    f.seek(0, os.SEEK_SET)

def line_matches(line: str, keywords: Optional[List[str]]) -> bool:
    """Return ``True`` if *line* contains any of *keywords*.

    If *keywords* is ``None`` or empty, the function returns ``True`` for every
    line.
    """
    if not keywords:
        return True
    lowered = line.lower()
    return any(kw.lower() in lowered for kw in keywords)

def process_line(line: str) -> dict:
    """Convert a raw log line into a simple JSON‑serialisable dict.

    The dict contains the original text and a timestamp of when the line was
    observed (in ISO‑8601 format, UTC).
    """
    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "message": line,
    }

# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Tail a log file with optional keyword filtering"
    )
    parser.add_argument(
        "-f",
        "--file",
        required=True,
        help="Path to the log file to monitor",
    )
    parser.add_argument(
        "-k",
        "--keyword",
        action="append",
        help="Keyword to filter lines (case‑insensitive). Can be used multiple times.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="File to write JSON output. If omitted, prints to stdout.",
    )
    parser.add_argument(
        "-l",
        "--log-level",
        default="INFO",
        help="Logging level for the tool itself (DEBUG, INFO, WARNING, ERROR).",
    )
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    logger = configure_logger(args.log_level)
    log_path = Path(args.file).expanduser().resolve()
    if not log_path.is_file():
        logger.error("File not found: %s", log_path)
        sys.exit(1)

    output_handle = None
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        try:
            output_handle = output_path.open("w", encoding="utf-8")
        except OSError as exc:
            logger.error("Cannot open output file %s: %s", output_path, exc)
            sys.exit(1)

    logger.info("Starting to follow %s", log_path)
    try:
        for raw_line in follow(log_path, logger):
            if line_matches(raw_line, args.keyword):
                entry = process_line(raw_line)
                json_line = json.dumps(entry, ensure_ascii=False)
                if output_handle:
                    output_handle.write(json_line + "\n")
                    output_handle.flush()
                else:
                    print(json_line)
    except KeyboardInterrupt:
        logger.info("Interrupted by user – exiting.")
    finally:
        if output_handle:
            output_handle.close()

if __name__ == "__main__":
    main()
