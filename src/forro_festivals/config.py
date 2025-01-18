from pathlib import Path
import os
import logging


# Env vars
API_TOKEN = os.environ.get('API_TOKEN')
USERNAME = os.environ.get('USERNAME')
APP_SECRET_KEY = os.environ.get('APP_SECRET_KEY')
NTFY_TOPIC = os.environ.get('NTFY_TOPIC')
LOG_FOLDER = Path(os.environ.get('LOG_FOLDER', 'data/logs'))
LOG_CONSOLE = os.environ.get('LOG_CONSOLE') == 'True'

# Paths - basic
root_path_repository = Path(__file__).parent.parent.parent
src = root_path_repository / 'src'
root_path_flask = src / 'forro_festivals'

# html dirs
static_folder = root_path_flask / 'static'
template_folder = root_path_flask / 'template'

# data paths
private_json = root_path_repository / 'data/private.json'
users_path = root_path_repository / 'data/users.json'
db_path = root_path_repository / 'data/festivals.db'
db_backup_folder = root_path_repository / 'data/backups_db'

class DateFormats:
    dm = '%d.%m'  # dd.mm
    ymd = '%Y-%m-%d'  # yyyy-mm-dd
    ymd_hms = '%Y-%m-%d-%H-%M-%S'  # yyyy-mm-dd-hh-mm-ss'
    bdy = '%B %d, %Y'  # August 12, 2025


import logging
from logging.handlers import RotatingFileHandler


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

    return logger
