#!/bin/bash

cd /home/feiteneuer/forro-festivals

git fetch --all
git reset --hard origin/master

# This is reloads the app since pythonanywhere is checking for file changes
# to the wsgi file and reloads the app upon last changed
touch /var/www/www_forro-festivals_com_wsgi.py
