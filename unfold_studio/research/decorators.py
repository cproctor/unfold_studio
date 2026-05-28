import functools
from django.http import JsonResponse
from django.utils import timezone


def require_api_key(view_func):
    """
    Require a valid Bearer API key on the request.
    Sets request.api_key to the matching APIKey instance.
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from research.models import APIKey
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth.startswith('Bearer '):
            return JsonResponse({"error": "Authorization required. Use 'Authorization: Bearer <key>' header."}, status=401)
        key_value = auth[7:].strip()
        try:
            api_key = APIKey.objects.get(key=key_value, revoked=False)
        except APIKey.DoesNotExist:
            return JsonResponse({"error": "Invalid or revoked API key."}, status=401)
        api_key.last_used_at = timezone.now()
        api_key.save(update_fields=['last_used_at'])
        request.api_key = api_key
        return view_func(request, *args, **kwargs)
    return wrapper
