from pathlib import Path
import os


# Env vars
API_TOKEN = os.environ.get('API_TOKEN')
USERNAME = os.environ.get('USERNAME')
LOG_FOLDER = os.environ.get('LOG_FOLDER')

ENV = os.environ.get('ENV', default='prod')

if ENV == 'prod':
    APP_SECRET_KEY = os.environ.get('APP_SECRET_KEY')
    NTFY_TOPIC = os.environ.get('NTFY_TOPIC')
    LOG_CONSOLE = os.environ.get('LOG_CONSOLE') == 'True'
elif ENV == 'dev':
    APP_SECRET_KEY = 'unsecure'
    NTFY_TOPIC = None
    LOG_CONSOLE = True
else:
    raise ValueError(f'{ENV=} must be one of "prod" or "dev".')


# Paths - basic
root_path_repository = Path(__file__).parent.parent.parent
src = root_path_repository / 'src'
root_path_flask = src / 'forro_festivals'

# html dirs
static_folder = root_path_flask / 'static'
template_folder = root_path_flask / 'template'

# data paths
data_folder = root_path_repository / 'data'
private_json = data_folder / 'private.json'
users_path = data_folder / 'users.json'
db_path = data_folder / 'festivals.db'
db_backup_folder = data_folder / 'backups_db'

class DateFormats:
    dm = '%d.%m'  # dd.mm
    ymd = '%Y-%m-%d'  # yyyy-mm-dd
    ymd_hms = '%Y-%m-%d-%H-%M-%S'  # yyyy-mm-dd-hh-mm-ss'
    ymd_hm = '%Y-%m-%d-%H-%M'
    bdy = '%B %d, %Y'  # August 12, 2025

