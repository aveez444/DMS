# accounts/authentication.py
from rest_framework.authentication import SessionAuthentication
from rest_framework import exceptions
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class CustomSessionAuthentication(SessionAuthentication):
    def authenticate(self, request):
        # Use default session auth for admin paths
        if request.path.startswith('/admin/'):
            return super().authenticate(request)

        # Try standard session authentication first
        auth_result = super().authenticate(request)
        if auth_result:
            return auth_result

        # Fallback to custom session header
        session_id = request.META.get('HTTP_X_SESSION_ID')
        if not session_id:
            return None

        logger.debug(f"Authenticating with session ID: {session_id}")
        try:
            session = Session.objects.get(session_key=session_id)
            session_data = session.get_decoded()
            user_id = session_data.get('_auth_user_id')
            if not user_id:
                return None

            user = User.objects.get(id=user_id)
            if hasattr(request, 'tenant') and user.tenant != request.tenant:
                logger.warning(f"Invalid tenant access for user {user.username}")
                raise exceptions.AuthenticationFailed('Invalid tenant access')

            logger.debug(f"Authenticated user: {user.username}")
            return (user, None)
        except (Session.DoesNotExist, User.DoesNotExist) as e:
            logger.warning(f"Session authentication failed: {str(e)}")
            return None