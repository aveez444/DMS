# accounts/custom_auth.py
from rest_framework import authentication
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class HeaderBasedAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        if request.method == 'OPTIONS' or request.path.startswith('/admin/'):
            logger.debug("Skipping authentication for OPTIONS or admin request")
            return None

        session_id = request.META.get('HTTP_X_SESSION_ID')
        if session_id:
            logger.debug(f"Found session ID: {session_id}")
            try:
                session = Session.objects.get(session_key=session_id)
                session_data = session.get_decoded()
                user_id = session_data.get('_auth_user_id')
                if user_id:
                    user = User.objects.get(id=user_id)
                    if hasattr(request, 'tenant') and user.tenant != request.tenant:
                        logger.warning(f"Invalid tenant: {user.username} tried to access {request.tenant}")
                        raise exceptions.AuthenticationFailed('Invalid tenant access')
                    logger.debug(f"Successfully authenticated via session ID: {user.username}")
                    return (user, None)
            except (Session.DoesNotExist, User.DoesNotExist) as e:
                logger.warning(f"Session auth failed: {str(e)}")
                return None
        logger.debug("No session ID provided")
        return None