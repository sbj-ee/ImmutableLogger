# ImmutableLogger

`ImmutableLogger` is a thread-safe, immutable logging utility for Python that writes logs to a file. Its immutable nature ensures that each log action creates a new logger instance, preserving the history of logs in an immutable state. This makes it particularly useful in multi-threaded applications where a shared mutable state can lead to complex synchronization issues.

## Features

- **Immutability**: Each logging action (e.g., `info`, `warning`, `error`) returns a new `ImmutableLogger` instance, leaving the original instance unchanged.
- **File-based Logging**: All log entries are written to a specified log file.
- **Log Rotation**: Automatically rotates log files when they exceed a specified size, preventing them from growing indefinitely.
- **Log Filtering**: Allows retrieving logs filtered by their level (e.g., `INFO`, `WARNING`, `ERROR`).
- **Easy to Use**: Provides a simple and intuitive API for logging.

## Installation

No external dependencies are required. Simply place the `ImmutableLogger.py` file in your project.

## Usage

### Basic Logging

Here's a simple example of how to use `ImmutableLogger`:

```python
from ImmutableLogger import ImmutableLogger

# Initialize the logger
logger = ImmutableLogger(log_file="./logs/app.log", max_file_size=1024 * 1024)

# Log messages
logger = logger.info("Application started")
logger = logger.warning("Low disk space")
logger = logger.error("Failed to connect to database")

# Print all logs to the console
print(logger)

# Retrieve and print only ERROR logs
error_logs = logger.get_logs("ERROR")
for log in error_logs:
    print(log)
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

### Configuration

You can configure the logger by passing arguments to its constructor:

- `log_file` (str): The path to the log file. Defaults to `./app.log`.
- `max_file_size` (int): The maximum size of the log file in bytes before rotation. Defaults to `1048576` (1MB).

```python
# Custom configuration
custom_logger = ImmutableLogger(
    log_file="/var/log/my_app.log",
    max_file_size=5 * 1024 * 1024  # 5MB
)
```

## Running Tests

To run the tests, you'll need to install `pytest`:

```bash
pip install pytest
```

Then, you can run the tests from the root of the project:

```bash
pytest
```
