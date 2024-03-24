"""Views for productivity app."""

from typing import cast

from django.core.exceptions import ValidationError
from django.http import HttpRequest, JsonResponse, QueryDict
from django.views.decorators.http import require_http_methods

from productivity.models import Productivity


def create_productivity(request_post: QueryDict) -> JsonResponse:
    """Create Productivity object.

    Args:
        request_post:
            `QueryDict` object with Productivity fields.
                - item
                - frequency
                - group

    Returns:
        JSON Response of Productivity object or error message.
    """
    try:
        productivity = Productivity(
            item=cast(str, request_post["item"]),
            frequency=int(cast(str, request_post["frequency"])),
            group=cast(str, request_post["group"]),
        )
    except KeyError:
        return JsonResponse({"error": "Missing data"}, status=400)

    try:
        productivity.clean_fields()
    except ValidationError:
        return JsonResponse({"error": "Data validation error"}, status=400)

    productivity.save()

    return JsonResponse(productivity.serialize_json(), status=201)


def get_productivity_object(productivity_id: int) -> Productivity:
    """Get a Productivity object by ID (primary key).

    Args:
        productivity_id:
            ID (primary key) of Productivity object.

    Returns:
        Productivity object.

    Raises:
        productivity.models.Productivity.DoesNotExist:
            Productivity object not found.
    """
    return Productivity.objects.get(pk=productivity_id)


def get_productivities() -> JsonResponse:
    """Return list of Productivity objects."""
    productivities = Productivity.objects.all()

    return JsonResponse(
        [p.serialize_json() for p in productivities], safe=False
    )


@require_http_methods(["GET", "POST"])
def index(request: HttpRequest) -> JsonResponse:
    """Get Productivity objects if GET, create if POST.

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
        json_response = get_productivities()
    elif request.method == "POST":
        json_response = create_productivity(request.POST)

    return json_response


@require_http_methods(["GET"])
def index_detail(request: HttpRequest, productivity_id: int) -> JsonResponse:
    """Get Productivity object.

    Args:
        request:
            HttpRequest object.
        productivity_id:
            `id` field (primary key) of Productivity object.

    Returns:
        JSON Response of Productivity object or error message.
    """
    try:
        productivity = get_productivity_object(productivity_id)
    except Productivity.DoesNotExist:
        return JsonResponse({"error": "ID not found"}, status=404)

    if request.method == "GET":
        json_response = JsonResponse(productivity.serialize_json())

    return json_response
