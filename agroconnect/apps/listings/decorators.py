from django.core.cache import cache
from django.http import HttpResponse


def rate_limit(key_prefix, limit, window_seconds):
    def decorator(view_func):
        def wrapped(request, *args, **kwargs):
            if request.user.is_authenticated:
                key = f"rl:{key_prefix}:user:{request.user.pk}"
            else:
                ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '0.0.0.0'))
                key = f"rl:{key_prefix}:ip:{ip}"
            count = cache.get(key, 0)
            if count >= limit:
                return HttpResponse("Rate limit exceeded. Please try again later.", status=429)
            cache.set(key, count + 1, timeout=window_seconds)
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator
