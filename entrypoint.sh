#!/bin/bash

set -e

#echo "Applying Database migrations..."

#alembic upgrade head

#echo "Database migrations applied successfully!"

echo "Starting Gunicorn..."
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app  --bind 0.0.0.0:8080 --timeout 120
