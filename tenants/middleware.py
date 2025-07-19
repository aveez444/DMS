# tenants/middleware.py
from django.http import HttpResponseForbidden
from django_tenants.utils import get_tenant_model, get_tenant_domain_model, get_public_schema_name
import logging
import os

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


class TenantIdentificationMiddleware:
    """
    Middleware to identify tenant from session or headers in production (Option A)
    Uses single domain with path-based routing
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant_model = get_tenant_model()
        environment = os.getenv('ENVIRONMENT', 'development')
        
        # Always start with public tenant as default
        try:
            public_tenant = tenant_model.objects.get(schema_name='public')
        except tenant_model.DoesNotExist:
            logger.error("Public tenant does not exist")
            return HttpResponseForbidden("Public tenant not found")
        
        # For admin URLs, always use public tenant
        if request.path.startswith('/admin/'):
            request.tenant = public_tenant
            return self.get_response(request)
        
        try:
            if environment == 'production':
                # Production: Single domain with tenant identification via session/headers
                tenant_schema = None
                
                # Method 1: Check for tenant in session (after login)
                if hasattr(request, 'session') and 'tenant_schema' in request.session:
                    tenant_schema = request.session['tenant_schema']
                    logger.debug(f"Tenant from session: {tenant_schema}")
                
                # Method 2: Check for tenant in custom header (for API calls)
                elif request.META.get('HTTP_X_TENANT_SCHEMA'):
                    tenant_schema = request.META.get('HTTP_X_TENANT_SCHEMA')
                    logger.debug(f"Tenant from header: {tenant_schema}")
                
                # Method 3: Check for tenant in URL parameter (alternative)
                elif request.GET.get('tenant'):
                    tenant_schema = request.GET.get('tenant')
                    logger.debug(f"Tenant from URL param: {tenant_schema}")
                
                # If we have a tenant schema, try to get that tenant
                if tenant_schema and tenant_schema != 'public':
                    try:
                        request.tenant = tenant_model.objects.get(schema_name=tenant_schema)
                        logger.debug(f"Set tenant: {request.tenant.name} ({tenant_schema})")
                    except tenant_model.DoesNotExist:
                        logger.warning(f"Tenant not found: {tenant_schema}, using public")
                        request.tenant = public_tenant
                else:
                    # Default to public tenant for universal login, admin, etc.
                    request.tenant = public_tenant
                    
            else:
                # Development: use domain-based routing as before
                hostname = request.get_host().split(':')[0]
                if hostname == '127.0.0.1' or hostname == 'localhost':
                    request.tenant = public_tenant
                else:
                    try:
                        domain = get_tenant_domain_model().objects.get(domain=hostname)
                        request.tenant = domain.tenant
                        logger.debug(f"Development - Set tenant: {request.tenant.name}")
                    except get_tenant_domain_model().DoesNotExist:
                        logger.warning(f"No tenant found for hostname: {hostname}")
                        request.tenant = public_tenant
                        
        except Exception as e:
            logger.error(f"Error in TenantIdentificationMiddleware: {str(e)}")
            request.tenant = public_tenant

        return self.get_response(request)