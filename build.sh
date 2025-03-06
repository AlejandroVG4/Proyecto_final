#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requisitos.txt

python manage.py makemigrations

# Apply any outstanding database migrations
python manage.py migrate

# Load fixtures
python manage.py loaddata ubicaciones_fixtures
python manage.py loaddata enfermedades_fixtures
python manage.py loaddata tratamientos_fixtures