#!/usr/bin/env bash
# build.sh - Render build script

set -o errexit  # Exit on error

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate --run-syncdb

echo "Creating public tenant..."
python manage.py create_public_tenant --domain=dms-g5l7.onrender.com

echo "Creating admin user for dealership1..."
python manage.py create_tenant_user \
  --schema=dealership1 \
  --username=manager1 \
  --email=manager1@gmail.com \
  --password=securepass \
  --is_admin

echo "Build completed successfully!"