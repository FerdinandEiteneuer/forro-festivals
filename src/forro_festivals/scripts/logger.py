import logging
from logging.handlers import RotatingFileHandler

from forro_festivals.scripts.notification import post_error_to_ntfy_channel
from forro_festivals.config import LOG_CONSOLE, LOG_FOLDER, NTFY_TOPIC

def get_logger():
    logger = logging.getLogger('app')
    logger.setLevel(logging.DEBUG)  # Set the default level to DEBUG

    # Create a formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)8s - %(module)s:%(funcName)s:%(lineno)d - %(message)s',
        datefmt='%d/%b/%Y %H:%M:%S'  # Custom date format: [18/Jan/2025 13:00:49]
    )

    if LOG_CONSOLE:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(filename=LOG_FOLDER / 'app.log', maxBytes=1e6, backupCount=5)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    class NtfyHandler(logging.Handler):
        """Sends error messages to ntfy."""
        def emit(self, record):
            if record.levelno >= 40 and NTFY_TOPIC is not None:
                ntfy_msg = formatter.format(record)
                post_error_to_ntfy_channel(message=ntfy_msg, topic=NTFY_TOPIC)

    logger.addHandler(NtfyHandler())

    return logger

logger = get_logger()
