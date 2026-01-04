# ImmutableLogger

A thread-safe, immutable logging utility for Python that writes logs to a file. Each log action creates a new logger instance, preserving the history of logs in an immutable state. This makes it particularly useful in multi-threaded applications where shared mutable state can lead to complex synchronization issues.

## Features

- **Immutability**: Each logging action returns a new `ImmutableLogger` instance, leaving the original unchanged
- **File-based Logging**: All log entries are written to a specified log file
- **Log Rotation**: Automatically rotates log files when they exceed a specified size
- **Log Filtering**: Retrieve logs filtered by level (INFO, WARNING, ERROR, or custom)
- **Zero Dependencies**: Uses only Python standard library

## Installation

No external dependencies required. Simply copy `ImmutableLogger.py` into your project.

```bash
git clone https://github.com/sbj-ee/ImmutableLogger.git
```

## Usage

### Basic Logging

```python
from ImmutableLogger import ImmutableLogger

# Initialize the logger
logger = ImmutableLogger(log_file="./logs/app.log", max_file_size=1024 * 1024)

# Log messages (each call returns a new logger instance)
logger = logger.info("Application started")
logger = logger.warning("Low disk space")
logger = logger.error("Failed to connect to database")

# Print all logs to the console
print(logger)

# Retrieve and print only ERROR logs
error_logs = logger.get_logs("ERROR")
for log in error_logs:
    print(f"{log.timestamp}: {log.message}")
```

### Immutability in Action

Each call to a logging method returns a new instance of the logger:

```python
logger1 = ImmutableLogger()
logger2 = logger1.info("First message")
logger3 = logger2.warning("Second message")

# logger1 has 0 logs
# logger2 has 1 log ("First message")
# logger3 has 2 logs ("First message", "Second message")

print(f"logger1 has {len(logger1.get_logs())} logs")
print(f"logger2 has {len(logger2.get_logs())} logs")
print(f"logger3 has {len(logger3.get_logs())} logs")
```

### Method Chaining

```python
logger = ImmutableLogger()
logger = (
    logger.info("Starting process")
    .warning("Resource usage high")
    .error("Process failed")
)
```

### Custom Log Levels

```python
logger = ImmutableLogger()
logger = logger.log("DEBUG", "Debugging information")
logger = logger.log("CRITICAL", "System failure")
```

### Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `log_file` | str | `"./app.log"` | Path to the log file |
| `max_file_size` | int | `1048576` (1MB) | Maximum file size before rotation |

```python
# Custom configuration
logger = ImmutableLogger(
    log_file="/var/log/my_app.log",
    max_file_size=5 * 1024 * 1024  # 5MB
)
```

## API Reference

### ImmutableLogger

| Method | Returns | Description |
|--------|---------|-------------|
| `info(message)` | `ImmutableLogger` | Log an INFO level message |
| `warning(message)` | `ImmutableLogger` | Log a WARNING level message |
| `error(message)` | `ImmutableLogger` | Log an ERROR level message |
| `log(level, message)` | `ImmutableLogger` | Log a message with custom level |
| `get_logs(level=None)` | `Tuple[LogEntry, ...]` | Get all logs, optionally filtered by level |

### LogEntry

Immutable dataclass with the following attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `timestamp` | `datetime` | When the log was created |
| `level` | `str` | Log level (INFO, WARNING, ERROR, etc.) |
| `message` | `str` | Log message content |

## Running Tests

```bash
pip install pytest
pytest test_logging.py -v
```

## Requirements

- Python 3.10+
- pytest (for running tests only)

## License

MIT
