from django.urls import path
from .views import get_csrf_token, create_tenant_user, get_dealership_permissions, get_dealership_users, assign_permission, remove_permission, get_access_token, auth_debug


urlpatterns = [

    path('api/create-user/', create_tenant_user, name='create_tenant_user'),
    path('api/permissions/', get_dealership_permissions, name='get_dealership_permissions'),
    path('api/dealership-users/', get_dealership_users, name='get_dealership_users'),
    path('api/assign-permission/', assign_permission, name='assign_permission'),
    path('api/remove-permission/', remove_permission, name='remove_permission'),
    path("api/csrf/", get_csrf_token, name="get_csrf_token"),
    path('api/get-token/', get_access_token, name='get_access_token'),
    path('api/auth-debug/', auth_debug, name='auth_debug'),
]
