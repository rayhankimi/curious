#!/bin/sh

set -e

python manage.py wait_for_db
python manage.py collectstatic --noinput
python manage.py migrate

granian --bind 0.0.0.0:8000 --workers 4 app.asgi:application
