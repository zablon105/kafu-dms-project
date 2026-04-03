#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Install dependencies
pip install -r requirements.txt

# 2. Collect static files (for CSS/Images)
python manage.py collectstatic --noinput

# 3. Apply database migrations
python manage.py migrate

# 4. Import your data from data.json
# Note: Ensure data.json is in your root folder next to manage.py
python manage.py loaddata data.json

# 5. Create superuser if it doesn't exist
# Uses DJANGO_SUPERUSER_USERNAME, etc. from Render Environment Variables
python manage.py createsuperuser --noinput || true