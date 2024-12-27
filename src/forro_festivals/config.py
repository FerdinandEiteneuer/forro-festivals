from pathlib import Path
import os

# Env vars
API_TOKEN = os.environ.get('API_TOKEN')
USERNAME = os.environ.get('USERNAME')
RELOAD_URL_PART = os.environ.get('RELOAD_URL_PART')

# Paths - basic
root_path_repository = Path(__file__).parent.parent.parent
src = root_path_repository / 'src'
root_path_flask = src / 'forro_festivals'

# html dirs
static_folder = root_path_flask / 'static'
template_folder = root_path_flask / 'template'

# data paths
private_json = root_path_repository / 'data/private.json'
db_path = root_path_repository / 'data/festivals.db'
db_backup_folder = Path(os.environ.get('HOME')) / 'backups_db'

# date formats
date_fmt_ymd = '%Y-%m-%d'  # yyyy-mm-dd
date_fmt_ymd_hms = '%Y-%m-%d-%H-%M-%S'  # yyyy-mm-dd-hh-mm-ss'
