"""Views for authentication app."""

from django.contrib.auth import authenticate, login
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "POST"])
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
    elif request.method == "POST":
        json_response = login_user(request)

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


def login_user(request: HttpRequest) -> JsonResponse:
    """Login user & send Session cookie in Response.

    Args:
        request:
            HttpRequest object.

    Returns:
        JSON Response or error message.
    """
    try:
        username = request.POST["username"]
        password = request.POST["password"]
    except KeyError:
        return JsonResponse({"error": "Missing data"}, status=400)

    user = authenticate(username=username, password=password)
    if user is None:
        return JsonResponse({"error": "Invalid login"}, status=401)

    login(request, user)

    return JsonResponse({"info": "Login success"})
