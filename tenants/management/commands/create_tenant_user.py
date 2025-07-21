import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django_tenants.utils import tenant_context
from tenants.models import Client

logger = logging.getLogger(__name__)

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a user for a specific tenant'

    def add_arguments(self, parser):
        parser.add_argument('--schema', required=True, help='Tenant schema name')
        parser.add_argument('--username', required=True)
        parser.add_argument('--email', required=True)
        parser.add_argument('--password', required=True)
        parser.add_argument('--is_admin', action='store_true', help='Make user tenant admin')

    def handle(self, *args, **options):
        schema_name = options['schema']
        try:
            tenant = Client.objects.get(schema_name=schema_name)
            with tenant_context(tenant):
                # Check if user already exists
                try:
                    user = User.objects.get(username=options['username'])
                    self.stdout.write(self.style.WARNING(
                        f'User "{options["username"]}" already exists for tenant "{tenant.name}" - skipping creation'
                    ))
                    logger.debug(f"User {options['username']} already exists")
                except User.DoesNotExist:
                    # Create new user
                    user = User.objects.create_user(
                        username=options['username'],
                        email=options['email'],
                        password=options['password'],
                        tenant=tenant,
                        is_tenant_admin=options['is_admin']
                    )

                    self.stdout.write(self.style.SUCCESS(
                        f'Successfully created user "{options["username"]}" for tenant "{tenant.name}"'
                    ))
                    logger.debug(f"Created user {options['username']}")

        except Client.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Tenant with schema "{schema_name}" does not exist'))
            logger.error(f'Tenant with schema "{schema_name}" does not exist')