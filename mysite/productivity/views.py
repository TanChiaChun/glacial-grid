"""Views for productivity app."""

from django.core.exceptions import ValidationError
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET, require_POST

from productivity.models import Productivity


@require_POST
def create_productivity(request: HttpRequest) -> JsonResponse:
    """Create Productivity object.

    Args:
        request:
            HttpRequest object, with below data in body.
                - item
                - frequency
                - group

    Returns:
        JSON Response of Productivity object or error message.
    """
    try:
        p = Productivity(
            item=request.POST["item"],
            frequency=int(request.POST["frequency"]),
            group=request.POST["group"],
        )
    except KeyError:
        return JsonResponse({"error": "Missing data"}, status=400)

    try:
        p.clean_fields()
    except ValidationError:
        return JsonResponse({"error": "Data validation error"}, status=400)

    p.save()

    return JsonResponse(p.serialize_json(), status=201)


@require_GET
def get_productivities(request: HttpRequest) -> JsonResponse:
    """Get list of Productivity objects.

    Args:
        request:
            HttpRequest object.

    Returns:
        JSON Response of Productivity objects.
    """
    productivities = Productivity.objects.all()

    return JsonResponse(
        [p.serialize_json() for p in productivities], safe=False
    )


def index(request: HttpRequest) -> JsonResponse:
    """Get Productivity objects if GET, create Productivity object if POST.

    Args:
        request:
            HttpRequest object.
                - If POST, below data required in body.
                    - item
                    - frequency
                    - group

    Returns:
        JSON Response of Productivity object/objects or error message.
    """
    if request.method == "GET":
        json_response = get_productivities(request)
    elif request.method == "POST":
        json_response = create_productivity(request)
    else:
        json_response = JsonResponse(
            {"error": "Request method not allowed"}, status=405
        )

    return json_response
