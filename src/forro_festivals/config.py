from pathlib import Path
import os

# Env vars
API_TOKEN = os.environ.get('API_TOKEN')
USERNAME = os.environ.get('USERNAME')
APP_SECRET_KEY = os.environ.get('APP_SECRET_KEY')
NTFY_TOPIC = os.environ.get('NTFY_TOPIC')

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
