import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from forro_festivals.misc.notification import post_error_to_ntfy_channel
from forro_festivals.config import LOG_CONSOLE, LOG_FOLDER, NTFY_TOPIC


class NtfyHandler(logging.Handler):
    """Sends error messages to ntfy."""
    def __init__(self, formatter, *args, **kwargs):
        self.formatter = formatter
        super().__init__(*args, **kwargs)

    def emit(self, record):
        if record.levelno >= 40 and NTFY_TOPIC is not None:
            ntfy_msg = self.formatter.format(record)
            post_error_to_ntfy_channel(message=ntfy_msg, topic=NTFY_TOPIC)

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

    if LOG_FOLDER:
        Path(LOG_FOLDER).mkdir(exist_ok=True, parents=True)
        filename = Path(LOG_FOLDER) / 'app.log'
        file_handler = RotatingFileHandler(filename=filename, maxBytes=1e6, backupCount=5)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if NTFY_TOPIC:
        logger.addHandler(NtfyHandler(formatter=formatter))

    return logger

logger = get_logger()
