#!/bin/bash
set -e  # exit with non-zero exist state if one command fails

cd /home/feiteneuer/forro-festivals

git fetch --all
git reset --hard origin/master

python src/forro_festivals/scripts/render_html_pages.py

# This is reloads the app since pythonanywhere is checking for file changes
# to the wsgi file and reloads the app upon last changed
touch /var/www/www_forro-festivals_com_wsgi.py
