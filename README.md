logger = ImmutableLogger()
logger.info("Application started")
logger.warning("Low disk space")
logger.error("Failed to connect to database")
print(logger)  # Prints all logs
logs = logger.get_logs()  # Returns immutable tuple of logs
