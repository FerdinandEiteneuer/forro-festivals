#!/bin/bash

# USERNAME and API_TOKEN are automatically set in the pythonanywhere environment

# Make the API call to reload the web app
curl -X POST \
    -H "Authorization: Token $API_TOKEN" \
    https://www.pythonanywhere.com/api/v0/user/$USERNAME/webapps/www.forro-festivals.com/reload/