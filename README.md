
<code>
    logger = ImmutableLogger(log_file="./logs/app.log", max_file_size=1024 * 1024)
    logger.info("Application started")
    logger.warning("Low disk space")
    logger.error("Failed to connect to database")
    print(logger)  # Prints all logs
    print(logger.get_logs("ERROR"))  # Prints only ERROR logs
</code>
