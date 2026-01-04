"""Tests for ImmutableLogger."""

import datetime
import os
import tempfile
from unittest.mock import MagicMock, mock_open, patch

import pytest

from ImmutableLogger import ImmutableLogger, LogEntry


@pytest.fixture
def temp_log_file():
    """Fixture to provide a temporary log file path that's cleaned up after tests."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        log_path = f.name
    yield log_path
    # Cleanup
    if os.path.exists(log_path):
        os.remove(log_path)
    # Also clean up any rotated files
    for f in os.listdir(os.path.dirname(log_path)):
        if f.startswith(os.path.basename(log_path)):
            try:
                os.remove(os.path.join(os.path.dirname(log_path), f))
            except OSError:
                pass


@pytest.fixture
def logger(temp_log_file):
    """Fixture to provide a logger instance with a temporary log file."""
    return ImmutableLogger(log_file=temp_log_file)


class TestLogEntry:
    """Tests for the LogEntry dataclass."""

    def test_log_entry_is_frozen(self):
        """LogEntry should be immutable (frozen)."""
        entry = LogEntry(
            timestamp=datetime.datetime.now(),
            level="INFO",
            message="Test",
        )
        with pytest.raises(AttributeError):
            entry.message = "Changed"

    def test_log_entry_attributes(self):
        """LogEntry should store all attributes correctly."""
        now = datetime.datetime.now()
        entry = LogEntry(timestamp=now, level="ERROR", message="Test message")
        assert entry.timestamp == now
        assert entry.level == "ERROR"
        assert entry.message == "Test message"


class TestImmutableLoggerBasic:
    """Basic tests for ImmutableLogger."""

    def test_log_creation_and_immutability(self, logger):
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

    def test_info_method(self, logger):
        """Test the info convenience method."""
        new_logger = logger.info("Info message")
        logs = new_logger.get_logs()
        assert len(logs) == 1
        assert logs[0].level == "INFO"
        assert logs[0].message == "Info message"

    def test_warning_method(self, logger):
        """Test the warning convenience method."""
        new_logger = logger.warning("Warning message")
        logs = new_logger.get_logs()
        assert len(logs) == 1
        assert logs[0].level == "WARNING"
        assert logs[0].message == "Warning message"

    def test_error_method(self, logger):
        """Test the error convenience method."""
        new_logger = logger.error("Error message")
        logs = new_logger.get_logs()
        assert len(logs) == 1
        assert logs[0].level == "ERROR"
        assert logs[0].message == "Error message"

    def test_log_method_with_custom_level(self, logger):
        """Test the log method with a custom level."""
        new_logger = logger.log("DEBUG", "Debug message")
        logs = new_logger.get_logs()
        assert len(logs) == 1
        assert logs[0].level == "DEBUG"
        assert logs[0].message == "Debug message"

    def test_log_level_is_uppercased(self, logger):
        """Test that log levels are converted to uppercase."""
        new_logger = logger.log("debug", "Debug message")
        logs = new_logger.get_logs()
        assert logs[0].level == "DEBUG"

    def test_chaining_logs(self, logger):
        """Test chaining multiple log calls."""
        final_logger = (
            logger.info("First")
            .warning("Second")
            .error("Third")
        )
        logs = final_logger.get_logs()
        assert len(logs) == 3
        assert logs[0].message == "First"
        assert logs[1].message == "Second"
        assert logs[2].message == "Third"

    def test_get_logs_returns_tuple(self, logger):
        """Test that get_logs returns a tuple, which is immutable."""
        new_logger = logger.info("A message")
        logs = new_logger.get_logs()
        assert isinstance(logs, tuple)

    def test_empty_message(self, logger):
        """Test logging an empty message."""
        new_logger = logger.info("")
        logs = new_logger.get_logs()
        assert len(logs) == 1
        assert logs[0].message == ""


class TestLogFiltering:
    """Tests for log filtering functionality."""

    def test_filter_by_level(self, logger):
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

    def test_filter_case_insensitive(self, logger):
        """Test that filtering is case-insensitive."""
        new_logger = logger.info("Test")
        logs = new_logger.get_logs("info")
        assert len(logs) == 1

    def test_filter_returns_empty_for_no_matches(self, logger):
        """Test that filtering returns empty tuple when no matches."""
        new_logger = logger.info("Test")
        logs = new_logger.get_logs("ERROR")
        assert len(logs) == 0
        assert isinstance(logs, tuple)

    def test_get_all_logs(self, logger):
        """Test getting all logs without filter."""
        logger3 = logger.info("1").warning("2").error("3")
        all_logs = logger3.get_logs()
        assert len(all_logs) == 3


class TestLogRotation:
    """Tests for log rotation functionality."""

    @patch("os.path.exists", return_value=True)
    @patch("os.path.getsize", return_value=2000)
    @patch("os.rename")
    @patch("builtins.open", new_callable=mock_open)
    def test_log_rotation_triggered(
        self, mock_open_file, mock_rename, mock_getsize, mock_exists
    ):
        """Test that the log file is rotated when it exceeds the max size."""
        logger = ImmutableLogger(log_file="test.log", max_file_size=1024)

        logger.info("This should trigger rotation")

        mock_getsize.assert_called_with("test.log")
        assert mock_rename.call_count == 1

        # Check that the old log file was renamed with a timestamp
        original_file, rotated_file = mock_rename.call_args[0]
        assert original_file == "test.log"
        assert "test.log" in rotated_file
        assert datetime.datetime.now().strftime("%Y-%m-%d") in rotated_file

    @patch("os.path.exists", return_value=True)
    @patch("os.path.getsize", return_value=500)
    @patch("os.rename")
    @patch("builtins.open", new_callable=mock_open)
    def test_no_rotation_when_under_size(
        self, mock_open_file, mock_rename, mock_getsize, mock_exists
    ):
        """Test that no rotation occurs when file is under max size."""
        logger = ImmutableLogger(log_file="test.log", max_file_size=1024)

        logger.info("This should not trigger rotation")

        assert mock_rename.call_count == 0


class TestDirectoryCreation:
    """Tests for automatic directory creation."""

    @patch("os.path.exists", return_value=False)
    @patch("os.makedirs")
    def test_directory_creation(self, mock_makedirs, mock_exists):
        """Test that the log directory is created if it doesn't exist."""
        log_file = "./logs/app.log"
        ImmutableLogger(log_file=log_file)

        directory = os.path.dirname(log_file)
        mock_makedirs.assert_called_once_with(directory)

    @patch("os.makedirs")
    def test_no_directory_creation_for_current_dir(self, mock_makedirs):
        """Test that no directory is created for files in current directory."""
        ImmutableLogger(log_file="app.log")
        mock_makedirs.assert_not_called()


class TestFileWriting:
    """Tests for file writing functionality."""

    def test_writes_to_file(self, temp_log_file):
        """Test that logs are written to the file."""
        logger = ImmutableLogger(log_file=temp_log_file)
        logger.info("Test message")

        with open(temp_log_file, "r") as f:
            content = f.read()

        assert "INFO: Test message" in content

    def test_appends_to_file(self, temp_log_file):
        """Test that multiple logs are appended to the file."""
        logger = ImmutableLogger(log_file=temp_log_file)
        logger2 = logger.info("First")
        logger2.warning("Second")

        with open(temp_log_file, "r") as f:
            content = f.read()

        assert "INFO: First" in content
        assert "WARNING: Second" in content

    @patch("builtins.open", side_effect=IOError("Cannot write"))
    @patch("os.path.exists", return_value=False)
    def test_handles_write_error(self, mock_exists, mock_open_file, caplog):
        """Test that write errors are logged but don't raise exceptions."""
        logger = ImmutableLogger(log_file="test.log")

        # Should not raise an exception
        new_logger = logger.info("Test")

        # The log entry should still be added to the in-memory logs
        assert len(new_logger.get_logs()) == 1


class TestStringRepresentation:
    """Tests for string representation."""

    def test_str_representation(self, logger):
        """Test the string representation of the logger."""
        logger1 = logger.info("First message")
        logger2 = logger1.warning("Second message")

        log_str = str(logger2)
        logs = logger2.get_logs()

        expected_str = "\n".join(
            f"[{entry.timestamp}] {entry.level}: {entry.message}" for entry in logs
        )

        assert log_str == expected_str

    def test_str_empty_logger(self, logger):
        """Test string representation of empty logger."""
        assert str(logger) == ""


class TestConfiguration:
    """Tests for logger configuration."""

    def test_default_configuration(self):
        """Test default configuration values."""
        with patch("os.path.exists", return_value=True):
            logger = ImmutableLogger()
        assert logger._log_file == "./app.log"
        assert logger._max_file_size == 1024 * 1024

    def test_custom_configuration(self):
        """Test custom configuration values."""
        with patch("os.path.exists", return_value=True):
            logger = ImmutableLogger(
                log_file="/custom/path.log",
                max_file_size=5 * 1024 * 1024,
            )
        assert logger._log_file == "/custom/path.log"
        assert logger._max_file_size == 5 * 1024 * 1024


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
