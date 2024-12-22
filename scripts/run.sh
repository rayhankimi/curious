#!/bin/sh
set -e

python manage.py wait_for_db
python manage.py collectstatic --noinput
python manage.py migrate

granian \
  --interface wsgi \
  --workers 4 \
  --host 0.0.0.0 \
  --port 8000 \
  app.wsgi:application