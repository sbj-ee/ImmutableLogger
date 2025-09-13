import datetime
from typing import List, Tuple
from dataclasses import dataclass, field
from threading import Lock

@dataclass(frozen=True)
class LogEntry:
    timestamp: datetime.datetime
    level: str
    message: str

class ImmutableLogger:
    def __init__(self, log_file: str = "app.log"):
        self._logs: List[LogEntry] = []
        self._lock = Lock()
        self._log_file = log_file

    def log(self, level: str, message: str) -> None:
        """Add a new log entry with the specified level and message, and write to file."""
        with self._lock:
            entry = LogEntry(
                timestamp=datetime.datetime.now(),
                level=level.upper(),
                message=message
            )
            self._logs.append(entry)
            self._write_to_file(entry)

    def _write_to_file(self, entry: LogEntry) -> None:
        """Write a single log entry to the file in a thread-safe manner."""
        with self._lock:
            with open(self._log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{entry.timestamp}] {entry.level}: {entry.message}\n")

    def get_logs(self) -> Tuple[LogEntry, ...]:
        """Return a tuple of all log entries to ensure immutability."""
        with self._lock:
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
