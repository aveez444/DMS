web: python manage.py migrate --noinput && python manage.py migrate_schemas --noinput && python manage.py collectstatic --noinput && daphne -b 0.0.0.0 -p $PORT Vehicle_seller.asgi:application
