from django.http import HttpResponseForbidden
from django_tenants.utils import get_tenant_model, get_tenant_domain_model, get_public_schema_name
import logging

logger = logging.getLogger(__name__)
class SimpleTenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.debug(f"Request path: {request.path}")

        tenant_model = get_tenant_model()
        
        # Create a reference to the public tenant
        try:
            public_tenant = tenant_model.objects.get(schema_name=get_public_schema_name())
        except tenant_model.DoesNotExist:
            logger.error("Public tenant does not exist")
            return HttpResponseForbidden("Public tenant not found")

        # Special handling for admin paths - use public schema
        if request.path.startswith('/admin/'):
            request.tenant = public_tenant
            # If user is authenticated, make sure it's properly set
            if hasattr(request, 'user') and request.user.is_authenticated:
                logger.debug(f"Admin authenticated user: {request.user.username}")
            return self.get_response(request)

        # Regular tenant handling
        hostname = request.get_host().split(':')[0]
        try:
            domain = get_tenant_domain_model().objects.get(domain=hostname)
            tenant = domain.tenant
            request.tenant = tenant
            logger.debug(f"Set tenant: {tenant.name}, ID: {tenant.id}")
        except get_tenant_domain_model().DoesNotExist:
            logger.warning(f"No tenant found for hostname: {hostname}")
            # Default to public schema
            request.tenant = public_tenant

        response = self.get_response(request)
        return response

