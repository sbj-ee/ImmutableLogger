import pytest
import os
import datetime
from unittest.mock import mock_open, patch
from ImmutableLogger import ImmutableLogger, LogEntry

@pytest.fixture
def logger():
    """Fixture to provide a logger instance with a temporary log file."""
    return ImmutableLogger(log_file="test.log")

def test_log_creation_and_immutability(logger):
    """Test that a log entry is created and the logger remains immutable."""
    original_logs = logger.get_logs()

    new_logger = logger.info("Test message")

    # Check that the original logger is unchanged
    assert len(logger.get_logs()) == 0
    assert logger.get_logs() is original_logs

    # Check that the new logger has the new log
    new_logs = new_logger.get_logs()
    assert len(new_logs) == 1
    assert new_logs[0].level == "INFO"
    assert new_logs[0].message == "Test message"

    # Check that the new logger is a different instance
    assert new_logger is not logger

def test_log_filtering(logger):
    """Test that log entries can be filtered by level."""
    logger1 = logger.info("Info message")
    logger2 = logger1.warning("Warning message")
    logger3 = logger2.error("Error message")

    info_logs = logger3.get_logs("INFO")
    assert len(info_logs) == 1
    assert info_logs[0].level == "INFO"

    warning_logs = logger3.get_logs("WARNING")
    assert len(warning_logs) == 1
    assert warning_logs[0].level == "WARNING"

    error_logs = logger3.get_logs("ERROR")
    assert len(error_logs) == 1
    assert error_logs[0].level == "ERROR"

    all_logs = logger3.get_logs()
    assert len(all_logs) == 3

@patch("os.path.exists", return_value=True)
@patch("os.path.getsize", return_value=2000)
@patch("os.rename")
@patch("builtins.open", new_callable=mock_open)
def test_log_rotation(mock_open_file, mock_rename, mock_getsize, mock_exists, logger):
    """Test that the log file is rotated when it exceeds the max size."""
    logger._max_file_size = 1024  # 1KB

    new_logger = logger.info("This should trigger rotation")

    mock_getsize.assert_called_with(logger._log_file)
    assert mock_rename.call_count == 1

    # Check that the old log file was renamed with a timestamp
    original_file, rotated_file = mock_rename.call_args[0]
    assert original_file == logger._log_file
    assert logger._log_file in rotated_file
    assert datetime.datetime.now().strftime("%Y-%m-%d") in rotated_file

@patch("os.makedirs")
def test_directory_creation(mock_makedirs):
    """Test that the log directory is created if it doesn't exist."""
    log_file = "./logs/app.log"
    logger = ImmutableLogger(log_file=log_file)

    directory = os.path.dirname(log_file)
    mock_makedirs.assert_called_once_with(directory)

def test_get_logs_returns_tuple(logger):
    """Test that get_logs returns a tuple, which is immutable."""
    new_logger = logger.info("A message")
    logs = new_logger.get_logs()
    assert isinstance(logs, tuple)

def test_str_representation(logger):
    """Test the string representation of the logger."""
    logger1 = logger.info("First message")
    logger2 = logger1.warning("Second message")

    log_str = str(logger2)
    logs = logger2.get_logs()

    expected_str = "\n".join(
        f"[{entry.timestamp}] {entry.level}: {entry.message}"
        for entry in logs
    )

    assert log_str == expected_str

if __name__ == "__main__":
    pytest.main()
