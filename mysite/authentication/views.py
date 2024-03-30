"""Views for authentication app."""

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def authentication_login(request: HttpRequest) -> JsonResponse:
    """URL for login redirection.

    - Return error message as intended to be redirected from other Views if not
    logged in.

    Args:
        request:
            HttpRequest object.

    Returns:
        JSON Response of error message.
    """
    if request.method == "GET":
        json_response = JsonResponse({"error": "Login required"}, status=401)

    return json_response


@ensure_csrf_cookie
def csrftoken(request: HttpRequest) -> JsonResponse:
    """Send CSRF token in Response cookie.

    Args:
        request:
            HttpRequest object.

    Returns:
        Empty JSON Response with CSRF token in cookie.
    """
    return JsonResponse({})
