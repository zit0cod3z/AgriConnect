from functools import wraps
from django.core.cache import cache
from django.http import HttpResponse


def rate_limit(key_prefix, limit, window_seconds):
    """
    Rate-limiting decorator that works on both function-based views
    and class-based view methods (where self is the first argument).
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            # Class-based view: args = (self, request, ...)
            # Function-based view: args = (request, ...)
            if args and hasattr(args[0], 'request'):
                # Called as an unbound method — shouldn't happen but guard anyway
                request = args[0].request
            elif len(args) >= 2 and hasattr(args[1], 'META'):
                # args[0] = self (view instance), args[1] = request
                request = args[1]
            elif args and hasattr(args[0], 'META'):
                # args[0] = request (function-based view)
                request = args[0]
            else:
                # Can't determine request — just pass through
                return view_func(*args, **kwargs)

            if request.user.is_authenticated:
                key = f"rl:{key_prefix}:user:{request.user.pk}"
            else:
                ip = (
                    request.META.get('HTTP_X_FORWARDED_FOR', '')
                    .split(',')[0]
                    .strip()
                    or request.META.get('REMOTE_ADDR', '0.0.0.0')
                )
                key = f"rl:{key_prefix}:ip:{ip}"

            count = cache.get(key, 0)
            if count >= limit:
                return HttpResponse(
                    "Rate limit exceeded. Please slow down and try again later.",
                    status=429
                )
            cache.set(key, count + 1, timeout=window_seconds)
            return view_func(*args, **kwargs)
        return wrapped
    return decorator
