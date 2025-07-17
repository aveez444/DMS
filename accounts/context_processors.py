# accounts/context_processors.py
def tenant_context(request):
    """
    Add tenant information to template context
    """
    return {
        'tenant': getattr(request, 'tenant', None),
    }