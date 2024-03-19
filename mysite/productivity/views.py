"""Views for productivity app."""

from typing import cast

from django.core.exceptions import ValidationError
from django.http import HttpRequest, JsonResponse, QueryDict

from productivity.models import Productivity


def create_productivity(request_post: QueryDict) -> JsonResponse:
    """Create Productivity object.

    Args:
        request_post:
            QueryDict object.

    Returns:
        JSON Response of Productivity object or error message.
    """
    try:
        p = Productivity(
            item=cast(str, request_post["item"]),
            frequency=int(cast(str, request_post["frequency"])),
            group=cast(str, request_post["group"]),
        )
    except KeyError:
        return JsonResponse({"error": "Missing data"}, status=400)

    try:
        p.clean_fields()
    except ValidationError:
        return JsonResponse({"error": "Data validation error"}, status=400)

    p.save()

    return JsonResponse(p.serialize_json(), status=201)


def get_productivity(productivity_id: int) -> JsonResponse:
    """Get a Productivity object by ID (primary key).

    Args:
        productivity_id:
            ID (primary key) of Productivity object.

    Returns:
        JSON Response of Productivity object or error message.
    """
    try:
        productivity = Productivity.objects.get(pk=productivity_id)
    except Productivity.DoesNotExist:
        return JsonResponse({"error": "ID not found"}, status=404)

    return JsonResponse(productivity.serialize_json())


def get_productivities() -> JsonResponse:
    """Return list of Productivity objects."""
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
        json_response = get_productivities()
    elif request.method == "POST":
        json_response = create_productivity(request.POST)
    else:
        json_response = JsonResponse(
            {"error": "Request method not allowed"}, status=405
        )

    return json_response


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
    if request.method == "GET":
        json_response = get_productivity(productivity_id)
    else:
        json_response = JsonResponse(
            {"error": "Request method not allowed"}, status=405
        )

    return json_response
