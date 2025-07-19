# tenants/management/commands/create_public_tenant.py
from django.core.management.base import BaseCommand
from tenants.models import Client, Domain
import os

class Command(BaseCommand):
    help = 'Create public tenant and domain'

    def add_arguments(self, parser):
        parser.add_argument(
            '--domain',
            type=str,
            default=None,
            help='Domain for the public tenant (e.g., dms-g5l7.onrender.com or your-domain.com)',
        )

    def handle(self, *args, **options):
        # Determine the environment and domain
        environment = os.getenv('ENVIRONMENT', 'development')
        
        if options['domain']:
            domain_name = options['domain']
        elif environment == 'production':
            # Use your production domain
            domain_name = 'dms-g5l7.onrender.com'  # or your custom domain
        else:
            # Development domain
            domain_name = 'localhost:8000'
        
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
            domain=domain_name
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Public tenant {"created" if created else "already exists"}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Public domain {"created" if domain_created else "already exists"} - {domain_name}')
        )
        
        # Create sample dealership tenants for production
        if environment == 'production':
            self.create_sample_dealerships()
    
    def create_sample_dealerships(self):
        """Create sample dealership tenants with proper domains"""
        dealerships = [
            {'schema': 'dealership1', 'name': 'Dealership One', 'subdomain': 'dealership1'},
            {'schema': 'dealership2', 'name': 'Dealership Two', 'subdomain': 'dealership2'},
        ]
        
        base_domain = 'dms-g5l7.onrender.com'  # Change to your domain
        
        for dealer_info in dealerships:
            # Create tenant
            tenant, created = Client.objects.get_or_create(
                schema_name=dealer_info['schema'],
                defaults={
                    'name': dealer_info['name'],
                    'is_active': True
                }
            )
            
            # Create domain (for production, you'd use subdomains)
            domain_name = f"{dealer_info['subdomain']}.{base_domain}"
            domain, domain_created = Domain.objects.get_or_create(
                tenant=tenant,
                domain=domain_name
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Dealership {dealer_info["name"]} tenant {"created" if created else "exists"} - {domain_name}')
            )