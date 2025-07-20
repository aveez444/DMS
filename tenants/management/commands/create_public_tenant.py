from django.core.management.base import BaseCommand
from tenants.models import Client, Domain
import os

class Command(BaseCommand):
    help = 'Create public tenant and domain for production deployment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--domain',
            type=str,
            default=None,
            help='Domain for the public tenant',
        )

    def handle(self, *args, **options):
        environment = os.getenv('ENVIRONMENT', 'development')
        
        # Determine the correct domain
        if options['domain']:
            domain_name = options['domain']
        elif environment == 'production':
            domain_name = 'dms-g5l7.onrender.com'  # Your actual production domain
        else:
            domain_name = 'localhost:8000'
        
        # Create or update public tenant
        public_tenant, created = Client.objects.get_or_create(
            schema_name='public',
            defaults={
                'name': 'Public Site',
                'description': 'Main public tenant for universal login',
                'is_active': True
            }
        )
        
        if not created:
            public_tenant.name = 'Public Site'
            public_tenant.description = 'Main public tenant for universal login'
            public_tenant.is_active = True
            public_tenant.save()
        
        # Create or update public domain
        domain, domain_created = Domain.objects.get_or_create(
            tenant=public_tenant,
            domain=domain_name,
            defaults={'is_primary': True}
        )
        
        if not domain_created:
            domain.is_primary = True
            domain.save()
        
        self.stdout.write(
            self.style.SUCCESS(f'Public tenant {"created" if created else "updated"}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Public domain {"created" if domain_created else "updated"} - {domain_name}')
        )
        
        # Create dealership tenants for production
        if environment == 'production':
            self.create_dealership_tenants(domain_name)
    
    def create_dealership_tenants(self, base_domain):
        """Create dealership tenants with single-domain configuration"""
        dealerships = [
            {'schema': 'dealership1', 'name': 'Dealership One'},
            {'schema': 'dealership2', 'name': 'Dealership Two'},
        ]
        
        for dealer_info in dealerships:
            # Create or update tenant
            tenant, created = Client.objects.get_or_create(
                schema_name=dealer_info['schema'],
                defaults={
                    'name': dealer_info['name'],
                    'description': f'Tenant for {dealer_info["name"]}',
                    'is_active': True
                }
            )
            
            if not created:
                tenant.name = dealer_info['name']
                tenant.description = f'Tenant for {dealer_info["name"]}'
                tenant.is_active = True
                tenant.save()
            
            # For single-domain approach, use the same base domain
            # The tenant will be identified by headers, not subdomains
            domain, domain_created = Domain.objects.get_or_create(
                tenant=tenant,
                domain=base_domain,  # Same domain for all tenants
                defaults={'is_primary': True}
            )
            
            if not domain_created:
                domain.domain = base_domain
                domain.is_primary = True
                domain.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Dealership {dealer_info["name"]} tenant {"created" if created else "updated"} - {base_domain}'
                )
            )