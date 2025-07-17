# dealership/middleware.py
from django.core.exceptions import PermissionDenied
from rest_framework.views import APIView

class AutoPermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        return response
        
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Get the actual view class for DRF views
        view_class = getattr(view_func, 'cls', None)
        
        if not view_class or not issubclass(view_class, APIView):
            return None
            
        # Check for permission_required attribute
        permission = getattr(view_class, 'permission_required', None)
        if not permission:
            return None
            
        if not request.user.has_perm(permission):
            raise PermissionDenied("You don't have permission to access this resource")