#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Install dependencies
pip install -r requirements.txt

# 2. Collect static files
python manage.py collectstatic --noinput

# 3. Apply database migrations
python manage.py migrate

# 4. Create superuser ONLY if env vars exist (safe)
if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
  python manage.py createsuperuser --noinput || true
fi

# ❌ Removed loaddata (it was breaking deployment)