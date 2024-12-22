from pathlib import Path
import os

# Auth Token
AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
USERNAME = os.environ.get('USERNAME')

# Paths
root_path_repository = Path(__file__).parent.parent.parent
src = root_path_repository / 'src'
root_path_flask = src / 'forro_festivals'

static_folder = root_path_flask / 'static'
template_folder = root_path_flask / 'template'
private_json = root_path_repository / 'data/private.json'
