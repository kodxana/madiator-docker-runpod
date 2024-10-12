#!/bin/bash
set -e

# Set Flask environment variables
export FLASK_ENV=production

# Use APP_PATH environment variable if set, otherwise use a default
APP_PATH=${APP_PATH:-"/app/app.py"}

# Extract the directory and filename
APP_DIR=$(dirname "$APP_PATH")
APP_FILE=$(basename "$APP_PATH")

# Change to the app directory
cd "$APP_DIR"

# Start Gunicorn with your Flask app
exec gunicorn --bind 0.0.0.0:7223 --worker-class gevent --workers 1 "${APP_FILE%.*}:app"  # Changed port to 7223