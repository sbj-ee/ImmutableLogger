import datetime
import os
from typing import List, Tuple
from dataclasses import dataclass
import logging

@dataclass(frozen=True)
class LogEntry:
    timestamp: datetime.datetime
    level: str
    message: str

class ImmutableLogger:
    def __init__(self, log_file: str = "./app.log", max_file_size: int = 1024 * 1024):
        """Initialize logger with log file path and max file size (in bytes)."""
        self._logs: List[LogEntry] = []
        self._log_file = log_file
        self._max_file_size = max_file_size  # Default: 1MB
        self._ensure_directory_exists()

    def _ensure_directory_exists(self) -> None:
        """Ensure the directory for the log file exists."""
        directory = os.path.dirname(self._log_file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    def log(self, level: str, message: str) -> None:
        """Add a new log entry with the specified level and message, and write to file."""
        entry = LogEntry(
            timestamp=datetime.datetime.now(),
            level=level.upper(),
            message=message
        )
        self._logs.append(entry)
        try:
            self._write_to_file(entry)
        except (IOError, OSError) as e:
            print(f"Failed to write to log file: {e}")

    def _write_to_file(self, entry: LogEntry) -> None:
        """Write a single log entry to the file and handle log rotation."""
        if os.path.exists(self._log_file) and os.path.getsize(self._log_file) > self._max_file_size:
            self._rotate_log_file()
        with open(self._log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{entry.timestamp}] {entry.level}: {entry.message}\n")

    def _rotate_log_file(self) -> None:
        """Rotate the log file if it exceeds the maximum size."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            rotated_file = f"{self._log_file}.{timestamp}"
            if os.path.exists(self._log_file):
                os.rename(self._log_file, rotated_file)
        except (IOError, OSError) as e:
            print(f"Failed to rotate log file: {e}")

    def get_logs(self, level: str = None) -> Tuple[LogEntry, ...]:
        """Return a tuple of all log entries, optionally filtered by level."""
        if level:
            return tuple(entry for entry in self._logs if entry.level == level.upper())
        return tuple(self._logs)

    def info(self, message: str) -> None:
        """Log an INFO level message."""
        self.log("INFO", message)

    def warning(self, message: str) -> None:
        """Log a WARNING level message."""
        self.log("WARNING", message)

    def error(self, message: str) -> None:
        """Log an ERROR level message."""
        self.log("ERROR", message)

    def __str__(self) -> str:
        """Return a string representation of all log entries."""
        return "\n".join(
            f"[{entry.timestamp}] {entry.level}: {entry.message}"
            for entry in self.get_logs()
        )
