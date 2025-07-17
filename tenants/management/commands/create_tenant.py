from django.core.management.base import BaseCommand
from django_tenants.utils import tenant_context
from tenants.models import Client, Domain
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Create a new tenant with domain and schema'

    def add_arguments(self, parser):
        parser.add_argument('--schema_name', required=True, help='Schema name for the tenant')
        parser.add_argument('--name', required=True, help='Tenant name')
        parser.add_argument('--domain', required=True, help='Domain for the tenant')

    def handle(self, *args, **options):
        schema_name = options['schema_name']
        tenant_name = options['name']
        domain_name = options['domain']

        # Check if tenant with the schema already exists
        if Client.objects.filter(schema_name=schema_name).exists():
            self.stdout.write(self.style.ERROR(
                f'Tenant with schema "{schema_name}" already exists.'
            ))
            return

        # Create new tenant
        tenant = Client.objects.create(
            schema_name=schema_name,
            name=tenant_name
        )

        # Create primary domain for the tenant
        Domain.objects.create(
            domain=domain_name,
            tenant=tenant,
            is_primary=True
        )

        # Run migrations in tenant context
        with tenant_context(tenant):
            call_command('migrate', interactive=False)

        self.stdout.write(self.style.SUCCESS(
            f'Successfully created tenant "{tenant_name}" '
            f'with schema "{schema_name}" and domain "{domain_name}".'
        ))
