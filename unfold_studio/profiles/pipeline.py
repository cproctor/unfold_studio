import re
import random
import string
from django.contrib.auth.models import User
from profiles.models import DeprecatedUsername


def sanitize_username(strategy, details, backend, user=None, *args, **kwargs):
    """Replace characters invalid for Django usernames and handle collisions."""
    if user:
        return  # existing user; nothing to do

    username = details.get('username', '')
    if not username:
        return

    # Keep only letters, digits, and underscores; replace others with _
    sanitized = re.sub(r'[^\w]', '_', username, flags=re.ASCII)
    # Must start with a letter
    if sanitized and not sanitized[0].isalpha():
        sanitized = 'u' + sanitized
    # Truncate to 145 chars (leaves room for _XXXXX suffix)
    sanitized = sanitized[:145]
    # Ensure uniqueness and avoid deprecated usernames
    candidate = sanitized
    while (User.objects.filter(username=candidate).exists() or
           DeprecatedUsername.objects.filter(old_username=candidate).exists()):
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        candidate = f'{sanitized}_{suffix}'

    details['username'] = candidate
