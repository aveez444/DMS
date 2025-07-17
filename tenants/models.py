from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class Client(TenantMixin):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_on = models.DateField(auto_now_add=True)
    
    # Add any additional tenant-specific fields
    is_active = models.BooleanField(default=True)

    auto_create_schema = True  # Automatically create PostgreSQL schema

    def __str__(self):
        return self.name

class Domain(DomainMixin):
    def __str__(self):
        return self.domain