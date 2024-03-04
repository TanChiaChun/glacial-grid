"""Views for authentication app."""

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def acquire_csrf_token(request: HttpRequest) -> JsonResponse:
    """Send CSRF token in Response cookie.

    Args:
        request: HttpRequest object.

    Returns:
        Empty JSON Response with CSRF token in cookie.
    """
    return JsonResponse({})
