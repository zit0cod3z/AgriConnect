#!/usr/bin/env bash
# Render build script — runs on every deploy
set -o errexit

echo "==> Installing Python dependencies..."
pip install -r requirements.txt

echo "==> Collecting static files..."
python manage.py collectstatic --no-input

echo "==> Running database migrations..."
python manage.py migrate --no-input

echo "==> Creating/fixing admin superuser..."
python manage.py fix_admin

echo "==> Verifying admin auth..."
python manage.py debug_auth

echo "==> Build complete ✅"
