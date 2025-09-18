<code>
    logger = ImmutableLogger(log_file="./logs/app.log", max_file_size=1024 * 1024)
    logger = logger.info("Application started")
    logger = logger.warning("Low disk space")
    logger = logger.error("Failed to connect to database")
    print(logger)  # Prints all logs
    print(logger.get_logs("ERROR"))  # Prints only ERROR logs
</code>
