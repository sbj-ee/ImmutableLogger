
<code>
logger = ImmutableLogger(log_file="my_app.log")
logger.info("Application started")
logger.warning("Low disk space")
logger.error("Failed to connect to database")
print(logger)  # Prints all logs
# Logs are also written to my_app.log
</code>
