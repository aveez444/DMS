# accounts/middleware.py
from django.http import HttpResponseForbidden
from django_tenants.utils import get_tenant_model, get_tenant_domain_model, get_public_schema_name
import logging

logger = logging.getLogger(__name__)

class SimpleTenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant_model = get_tenant_model()
        try:
            public_tenant = tenant_model.objects.get(schema_name=get_public_schema_name())
        except tenant_model.DoesNotExist:
            logger.error("Public tenant does not exist")
            return HttpResponseForbidden("Public tenant not found")

        if request.path.startswith('/admin/'):
            request.tenant = public_tenant
            return self.get_response(request)

        hostname = request.get_host().split(':')[0]
        try:
            domain = get_tenant_domain_model().objects.get(domain=hostname)
            request.tenant = domain.tenant
            logger.debug(f"Set tenant: {request.tenant.name}, ID: {request.tenant.id}")
        except get_tenant_domain_model().DoesNotExist:
            logger.warning(f"No tenant found for hostname: {hostname}")
            request.tenant = public_tenant

        return self.get_response(request)