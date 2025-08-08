import logging
# Configure the root logger minimally or not at all
#logging.basicConfig(level=logging.WARNING)  # Optional: Minimal configuration for the root logger

# Create and configure a named logger
def setup_logger(name : str, level : str=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create handlers
    console_handler = logging.StreamHandler()

    # Create formatters and add them to handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s : %(message)s')
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)

    return logger


app_logger = setup_logger("genaSQL-Shopify", level=logging.DEBUG)