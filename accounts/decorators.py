# from django.http import JsonResponse
# from django_tenants.utils import tenant_context
# from .models import CustomUser, Client

# def validate_session(get_response):
#     def middleware(request):
#         session_id = request.headers.get('X-Session-ID') or request.session.session_key
#         tenant_id = request.session.get('tenant_id')

#         if session_id and tenant_id:
#             try:
#                 tenant = Client.objects.get(id=tenant_id)
#                 with tenant_context(tenant):
#                     # Verify session
#                     session = request.session
#                     user_id = session.get('_auth_user_id')
#                     if user_id:
#                         user = CustomUser.objects.get(id=user_id)
#                         request.user = user
#                         return get_response(request)
#             except (CustomUser.DoesNotExist, Client.DoesNotExist):
#                 pass
#         return JsonResponse({'error': 'Invalid user access'}, status=401)
#     return middleware