web: python manage.py migrate --noinput && python manage.py migrate_schemas --noinput && python manage.py collectstatic --noinput && gunicorn Vehicle_seller.wsgi --bind 0.0.0.0:8080
