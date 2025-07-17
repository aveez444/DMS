from django.contrib.auth.models import AbstractUser
from django.db import models
from tenants.models import Client
from django_tenants.utils import get_public_schema_name
import uuid

class CustomUser(AbstractUser):
    tenant = models.ForeignKey(
        Client, 
        on_delete=models.CASCADE, 
        related_name='users',
        null=True,
        blank=True
    )
    is_tenant_admin = models.BooleanField(default=False)
  
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


    def save(self, *args, **kwargs):
        # Allow superusers with no tenant or public tenant
        if self.is_superuser:
            if not self.tenant or self.tenant.schema_name == get_public_schema_name():
                # This is fine
                pass
            else:
                raise ValueError("Superadmin must be in public schema or have no tenant.")
        super().save(*args, **kwargs)