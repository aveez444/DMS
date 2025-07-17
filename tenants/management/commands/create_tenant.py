# tenants/management/commands/create_tenant.py
from django.core.management.base import BaseCommand
from tenants.models import Client, Domain
from django.db import connection

class Command(BaseCommand):
    help = 'Create a new tenant with domain'

    def add_arguments(self, parser):
        parser.add_argument('--schema_name', required=True, help='Schema name for the tenant')
        parser.add_argument('--name', required=True, help='Tenant name')
        parser.add_argument('--domain', required=True, help='Domain for the tenant')

    def handle(self, *args, **options):
        schema_name = options['schema_name']
        name = options['name']
        domain_str = options['domain']
        
        # Check if tenant exists
        if Client.objects.filter(schema_name=schema_name).exists():
            self.stdout.write(self.style.ERROR(f'Tenant with schema "{schema_name}" already exists'))
            return
            
        # Create tenant
        tenant = Client(schema_name=schema_name, name=name)
        tenant.save()
        
        # Create domain for tenant
        domain = Domain(domain=domain_str, tenant=tenant, is_primary=True)
        domain.save()
        
        # Confirm creation
        self.stdout.write(self.style.SUCCESS(f'Successfully created tenant "{name}" with schema "{schema_name}" and domain "{domain_str}"'))