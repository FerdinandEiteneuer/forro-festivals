import os
import subprocess
import logging

import forro_festivals.config as config

# TODO(fe): Check again if a pure python implementation would not also work...
def reload_app_by_touch():
    os.chdir(config.root_path_repository)
    cmd = ['bash', 'src/forro_festivals/scripts/reload-app.sh']
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    stdout, stderr = result.stdout, result.stderr
    if result.returncode != 0:
        logging.error(f'Reloading failed: {stdout=}, {stderr=}')
    return result.returncode

