from django_tenants.middleware import TenantMainMiddleware
from django_tenants.utils import remove_www
from django_tenants.utils import get_tenant_model, get_tenant_domain_model
import logging
import os

logger = logging.getLogger(__name__)

class HeaderTenantMiddleware(TenantMainMiddleware):
    """
    Custom middleware that supports both header-based and subdomain-based tenant identification.
    Priority: HTTP Header > Session > Subdomain > Public tenant
    """
    
    @staticmethod
    def hostname_from_request(request):
        """
        Extracts tenant identifier from request using multiple strategies.
        Returns the appropriate hostname/domain for tenant resolution.
        """
        # Get the actual hostname as fallback
        hostname = remove_www(request.get_host().split(':')[0])
        
        # Strategy 1: Check for explicit tenant header (highest priority)
        tenant_domain = request.META.get('HTTP_X_TENANT_DOMAIN')
        if tenant_domain:
            logger.debug(f"Tenant identified via header: {tenant_domain}")
            return tenant_domain
        
        # Strategy 2: Check session for tenant domain (after login)
        if hasattr(request, 'session') and 'tenant_domain' in request.session:
            tenant_domain = request.session['tenant_domain']
            logger.debug(f"Tenant identified via session: {tenant_domain}")
            return tenant_domain
        
        # Strategy 3: Check for tenant schema in session
        if hasattr(request, 'session') and 'tenant_schema' in request.session:
            tenant_schema = request.session['tenant_schema']
            try:
                tenant_model = get_tenant_model()
                tenant = tenant_model.objects.get(schema_name=tenant_schema)
                domain_model = get_tenant_domain_model()
                domain = domain_model.objects.filter(tenant=tenant).first()
                if domain:
                    logger.debug(f"Tenant identified via session schema: {domain.domain}")
                    return domain.domain
            except Exception as e:
                logger.warning(f"Failed to resolve tenant from session schema: {e}")
        
        # Strategy 4: Use hostname (subdomain support for development)
        environment = os.getenv('ENVIRONMENT', 'development')
        if environment == 'development' and hostname not in ['127.0.0.1', 'localhost']:
            logger.debug(f"Development mode - using hostname: {hostname}")
            return hostname
        
        # Strategy 5: Default to public tenant domain
        try:
            tenant_model = get_tenant_model()
            public_tenant = tenant_model.objects.get(schema_name='public')
            domain_model = get_tenant_domain_model()
            public_domain = domain_model.objects.filter(tenant=public_tenant).first()
            if public_domain:
                logger.debug(f"Defaulting to public domain: {public_domain.domain}")
                return public_domain.domain
        except Exception as e:
            logger.error(f"Failed to get public tenant domain: {e}")
        
        # Final fallback
        logger.debug(f"Final fallback to hostname: {hostname}")
        return hostname

    def process_request(self, request):
        """
        Override to add additional logging and error handling
        """
        try:
            return super().process_request(request)
        except Exception as e:
            logger.error(f"Error in HeaderTenantMiddleware: {str(e)}")
            # Set public tenant as fallback
            tenant_model = get_tenant_model()
            try:
                request.tenant = tenant_model.objects.get(schema_name='public')
            except tenant_model.DoesNotExist:
                logger.critical("Public tenant not found - application cannot function")
                raise
            return None