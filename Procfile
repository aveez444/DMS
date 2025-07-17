release: python manage.py migrate --noinput && python manage.py migrate_schemas --noinput
     web: python manage.py collectstatic --noinput && gunicorn Vehicle_seller.wsgi