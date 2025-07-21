#!/bin/bash
python manage.py create_tenant_user \
  --schema=dealership1 \
  --username=manager1 \
  --email=manager1@gmail.com \
  --password=securepass \
  --is_admin
