#!/bin/bash


if [[ -z "$1" ]]; then
    echo "run server";
    python manage.py migrate;
    python manage.py collectstatic --noinput;
    gunicorn -w 5 -b 0.0.0.0:8000 --access-logfile=- --error-logfile=- dome.wsgi;
elif [[ "$1" = "migrate" ]]; then
    echo "run migrate";
    python manage.py migrate
else
    echo "$@"
    exec "$@"
fi


