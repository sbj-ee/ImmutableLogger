# import pytest
from ImmutableLogger import ImmutableLogger


def test_logger():
    print("Test started")
    logger = ImmutableLogger(log_file="my_app.log")
    print("logger created")
    #logger.info("Application started")
    #logger.warning("Low disk space")
    #logger.error("Failed to connect to database")
    print(logger)  # Prints all logs
    # Logs are also written to my_app.log
    return logger

if __name__ == "__main__":
    my_log = test_logger()
    my_log.info("Application started")
    my_log.warning("Low disk space")
    my_log.error("Failed to connect to database")
    print(my_log)
