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
        
        # Create or get public domain - FIXED: Handle existing domains properly
        try:
            domain = Domain.objects.get(tenant=public_tenant, domain=domain_name)
            domain_created = False
            self.stdout.write(
                self.style.WARNING(f'Public domain already exists - {domain_name}')
            )
        except Domain.DoesNotExist:
            domain = Domain.objects.create(
                tenant=public_tenant,
                domain=domain_name,
                is_primary=True
            )
            domain_created = True
            self.stdout.write(
                self.style.SUCCESS(f'Public domain created - {domain_name}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Public tenant {"created" if created else "already exists"}')
        )
        
        # Create sample dealership tenants for production
        if environment == 'production':
            self.create_sample_dealerships(domain_name)
    
    def create_sample_dealerships(self, base_domain):
        """Create sample dealership tenants with proper domains - FIXED VERSION"""
        dealerships = [
            {'schema': 'dealership1', 'name': 'Dealership One'},
            {'schema': 'dealership2', 'name': 'Dealership Two'},
        ]
        
        for dealer_info in dealerships:
            # Create tenant
            tenant, created = Client.objects.get_or_create(
                schema_name=dealer_info['schema'],
                defaults={
                    'name': dealer_info['name'],
                    'is_active': True
                }
            )
            
            # FIXED: Handle existing domains properly for dealership tenants
            try:
                # Check if domain already exists for this tenant
                domain = Domain.objects.get(tenant=tenant, domain=base_domain)
                domain_created = False
                self.stdout.write(
                    self.style.WARNING(f'Dealership {dealer_info["name"]} domain already exists - {base_domain}')
                )
            except Domain.DoesNotExist:
                # Check if domain exists for ANY tenant (this is what was causing the error)
                existing_domain = Domain.objects.filter(domain=base_domain).first()
                if existing_domain:
                    # Domain exists but for different tenant - this is the issue
                    # For single-domain approach, we need to handle this differently
                    self.stdout.write(
                        self.style.WARNING(
                            f'Domain {base_domain} already exists for tenant {existing_domain.tenant.name}. '
                            f'Skipping domain creation for {dealer_info["name"]} - will use header-based routing.'
                        )
                    )
                    domain_created = False
                else:
                    # Safe to create new domain
                    domain = Domain.objects.create(
                        tenant=tenant,
                        domain=base_domain,
                        is_primary=True
                    )
                    domain_created = True
                    self.stdout.write(
                        self.style.SUCCESS(f'Dealership {dealer_info["name"]} domain created - {base_domain}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Dealership {dealer_info["name"]} tenant {"created" if created else "exists"}'
                )
            )

