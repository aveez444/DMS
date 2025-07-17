from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

class SimpleTenantBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Skip for admin URLs - let default backend handle it
        if request and request.path.startswith('/admin/'):
            return None
            
        try:
            user = super().authenticate(request, username=username, password=password, **kwargs)
            if user:
                # Add your tenant validation logic here if needed
                return user
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
        return None