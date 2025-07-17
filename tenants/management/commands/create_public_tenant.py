# tenants/management/commands/create_public_tenant.py
from django.core.management.base import BaseCommand
from tenants.models import Client, Domain

class Command(BaseCommand):
    help = 'Create public tenant and domain'

    def handle(self, *args, **options):
        # Create public tenant if it doesn't exist
        public_tenant, created = Client.objects.get_or_create(
            schema_name='public',
            defaults={
                'name': 'Public Site',
                'is_active': True
            }
        )
        
        # Create public domain
        domain, domain_created = Domain.objects.get_or_create(
            tenant=public_tenant,
            domain='127.0.0.1'
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Public tenant {"created" if created else "already exists"}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Public domain {"created" if domain_created else "already exists"}')
        )