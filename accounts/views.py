# accounts/views.py

from django.contrib.auth import authenticate, login
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.middleware.csrf import get_token
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django_tenants.utils import schema_context
from rest_framework.response import Response
from rest_framework import status
from tenants.models import Client, Domain
from django_tenants.utils import get_tenant_domain_model
from rest_framework.permissions import IsAuthenticated
from django_tenants.utils import tenant_context
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import CustomUser
from .serializers import CustomUserSerializer
import logging
from rest_framework_simplejwt.tokens import RefreshToken
from cryptography.fernet import Fernet
import base64


logger = logging.getLogger(__name__)
# accounts/views.py - Updated universal_login function

@csrf_exempt
def universal_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            tenants = Client.objects.exclude(schema_name='public')

            logger.debug(f"Login attempt for username: {username}")

            for tenant in tenants:
                with tenant_context(tenant):
                    try:
                        user = CustomUser.objects.get(username=username)
                        if user.check_password(password) and user.tenant == tenant:
                            # Log in user and set session
                            login(request, user)
                            logger.debug(f"User {username} logged in for tenant: {tenant.name}")

                            # Get domain
                            domain = Domain.objects.get(tenant=tenant)
                            
                            # Store session data
                            request.session['tenant_id'] = tenant.id
                            request.session['tenant_schema'] = tenant.schema_name
                            request.session['tenant_domain'] = domain.domain
                            request.session.modified = True
                            request.session.save()
                            session_key = request.session.session_key
                            
                            # Determine the API base URL (Option A: Single Domain)
                            environment = os.getenv('ENVIRONMENT', 'development')
                            if environment == 'production':
                                # Production: Single domain with path-based routing
                                api_base_url = "https://dms-g5l7.onrender.com"
                            else:
                                # Development: Still use localhost for universal login
                                api_base_url = "http://127.0.0.1:8000"

                            response = JsonResponse({
                                'success': True,
                                'message': f'Welcome to {tenant.name}',
                                'user': {
                                    'id': user.id,
                                    'uuid': str(user.uuid),
                                    'username': user.username,
                                    'email': user.email
                                },
                                'tenant': {
                                    'id': tenant.id,
                                    'schema_name': tenant.schema_name,
                                    'name': tenant.name,
                                    'domain': domain.domain,
                                    'api_base_url': api_base_url
                                },
                                'session_id': session_key
                            })

                            # Set appropriate cookie domain
                            cookie_domain = '.your-domain.com' if environment == 'production' else '.localhost'
                            
                            response.set_cookie(
                                'sessionid',
                                session_key,
                                httponly=True,
                                samesite='None' if environment == 'production' else 'Lax',
                                domain=cookie_domain,
                                secure=environment == 'production'
                            )
                            
                            return response
                    except CustomUser.DoesNotExist:
                        continue

            logger.warning(f"Login failed for username: {username}")
            return JsonResponse({'error': 'Invalid credentials'}, status=401)

        except Exception as e:
            logger.error(f"Login error: {str(e)}", exc_info=True)
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)
    
# accounts/views.py
from django.shortcuts import render

def public_login_page(request):
    """Render the universal login page"""
    return render(request, 'public_login.html')


from django.http import JsonResponse
from django.middleware.csrf import get_token

def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})


@api_view(['POST'])
@csrf_exempt  # 🚨 WARNING: Remove this in production
# @permission_classes([IsAuthenticated])  # Ensure authentication is required
def create_tenant_user(request):
    """
    API for a Tenant Admin to create a user within their dealership (tenant schema).
    """
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

    # ✅ Ensure the requester is a Tenant Admin
    if not hasattr(request.user, 'is_tenant_admin') or not request.user.is_tenant_admin:
        return Response({'error': 'Only tenant admins can create users.'}, status=status.HTTP_403_FORBIDDEN)

    # ✅ Get the tenant schema from the requester's user model
    tenant = request.user.tenant
    if not tenant:
        return Response({'error': 'User does not belong to any tenant.'}, status=status.HTTP_400_BAD_REQUEST)

    data = request.data

    # ✅ Validate required fields
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data or not data[field]:
            return Response({f'error': f'{field} is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Create the user inside the correct tenant schema
    with tenant_context(tenant):
        new_user = CustomUser.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            tenant=tenant,  # Assign the same tenant as the requester
            is_tenant_admin=data.get('is_tenant_admin', False)  # Default: False unless explicitly set
        )

    return Response({
        'message': 'User created successfully!',
        'user': CustomUserSerializer(new_user).data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dealership_permissions(request):
    """
    API to fetch dealership-specific permissions for a sub-admin.
    """
    user = request.user

    # Check if user has permission to view permissions (using Django's permission system)
    if not (user.has_perm('accounts.view_permission') or user.groups.filter(name='sub-admins').exists()):
        return Response({'error': 'You do not have permission to view permissions.'}, 
                       status=status.HTTP_403_FORBIDDEN)

    # Fetch only permissions relevant to dealership
    content_types = ContentType.objects.filter(app_label__in=['dealership', 'accounts'])
    permissions = Permission.objects.filter(content_type__in=content_types).values('id', 'name', 'codename')

    return Response({'permissions': list(permissions)}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dealership_users(request):
    """
    API to fetch users belonging to the sub-admin's dealership.
    """
    user = request.user

    # Check if user has permission to view users (using Django's permission system)
    if not (user.has_perm('accounts.view_customuser') or user.groups.filter(name='sub-admins').exists()):
        return Response({'error': 'You do not have permission to view users.'}, 
                       status=status.HTTP_403_FORBIDDEN)

    # Fetch only users from the same dealership
    users = CustomUser.objects.filter(tenant=user.tenant).values('id', 'username', 'email', 'is_tenant_admin')

    return Response({'users': list(users)}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_permission(request):
    """
    API to assign a permission to a user in the dealership.
    """
    user = request.user

    # Check if user has permission to change permissions (using Django's permission system)
    if not (user.has_perm('accounts.change_customuser') or user.groups.filter(name='sub-admins').exists()):
        return Response({'error': 'You do not have permission to assign permissions.'}, 
                       status=status.HTTP_403_FORBIDDEN)

    data = request.data
    user_id = data.get('user_id')
    permission_id = data.get('permission_id')

    if not user_id or not permission_id:
        return Response({'error': 'User ID and Permission ID are required.'}, 
                       status=status.HTTP_400_BAD_REQUEST)

    try:
        # Fetch user & ensure they belong to the same dealership
        dealership_user = CustomUser.objects.get(id=user_id, tenant=user.tenant)
        permission = Permission.objects.get(id=permission_id)

        # Assign permission
        dealership_user.user_permissions.add(permission)

        return Response({'message': 'Permission assigned successfully.'}, 
                       status=status.HTTP_200_OK)

    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found or does not belong to your dealership.'}, 
                       status=status.HTTP_404_NOT_FOUND)
    except Permission.DoesNotExist:
        return Response({'error': 'Invalid permission ID.'}, 
                       status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_permission(request):
    """
    API to remove a permission from a user in the dealership.
    """
    user = request.user

    # ✅ Ensure only tenant admins can remove permissions
    if not user.is_tenant_admin:
        return Response({'error': 'Only dealership sub-admins can remove permissions.'}, status=status.HTTP_403_FORBIDDEN)

    data = request.data
    user_id = data.get('user_id')
    permission_id = data.get('permission_id')

    # ✅ Validate required fields
    if not user_id or not permission_id:
        return Response({'error': 'User ID and Permission ID are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # ✅ Fetch user & ensure they belong to the same dealership
        dealership_user = CustomUser.objects.get(id=user_id, tenant=user.tenant)
        permission = Permission.objects.get(id=permission_id)

        # ✅ Remove permission
        dealership_user.user_permissions.remove(permission)

        return Response({'message': 'Permission removed successfully.'}, status=status.HTTP_200_OK)

    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found or does not belong to your dealership.'}, status=status.HTTP_404_NOT_FOUND)
    except Permission.DoesNotExist:
        return Response({'error': 'Invalid permission ID.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_access_token(request):
    user = request.user
    refresh = RefreshToken.for_user(user)
    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def auth_debug(request):
    """Debug endpoint to check authentication status"""
    return Response({
        'is_authenticated': request.user.is_authenticated,
        'user': request.user.username if request.user.is_authenticated else None,
        'session_id': request.META.get('HTTP_X_SESSION_ID'),
        'encrypted_uid': request.META.get('HTTP_X_ENCRYPTED_UID'),
        'tenant': request.tenant.name if hasattr(request, 'tenant') else None,
        'request_host': request.get_host(),
        'cookies_received': dict(request.COOKIES),
    })