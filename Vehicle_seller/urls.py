"""
URL configuration for Vehicle_seller project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# Vehicle_seller/urls.py
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from accounts import views as account_views
from django.http import JsonResponse  # You should add this if not already

def health_check(request):
    return JsonResponse({"status": "Running", "message": "Welcome to Vehicle Seller API"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', health_check),  # ✅ This handles /
    path('api/universal-login/', account_views.universal_login, name='universal_login'),
    path('dealership/', include('dealership.urls')),
    path('accounts/', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


    # # Public schema specific URLs
# from django_tenants.utils import get_public_schema_name, get_tenant_model
# from django.db import connection

# # This check helps determine if we're in the public schema
# if connection.schema_name == get_public_schema_name():
#     urlpatterns += [
#         path('superadmin/', admin.site.urls),
#         # path('api/login/', account_views.login_api, name='login_api'),
#         path('', account_views.public_login_page, name='public_login'),  # Public login page
#     ]
