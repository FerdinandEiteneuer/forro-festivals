#!/bin/bash

cd /home/feiteneuer/forro-festivals

git pull

# This is supposed to reload the app since pythonanywhere is checking for file changes
touch /var/www/www_forro-festivals_com_wsgi.py



# Make the API call to reload the web app
#curl -X POST \
#    -H "Authorization: Token $API_TOKEN" \
#    https://www.pythonanywhere.com/api/v0/user/$USERNAME/webapps/www.forro-festivals.com/reload/