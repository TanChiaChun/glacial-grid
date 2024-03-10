"""Views for productivity app."""

from django.core.exceptions import ValidationError
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST

from productivity.models import Productivity


@require_POST
def create(request: HttpRequest) -> JsonResponse:
    """Create & save Productivity object into database.

    Args:
        request:
            HttpRequest object, with below data in body.
                - item
                - frequency
                - group

    Returns:
        JSON Response of created Productivity object.
    """
    try:
        p = Productivity(
            item=request.POST["item"],
            frequency=int(request.POST["frequency"]),
            group=request.POST["group"],
        )
    except KeyError:
        return JsonResponse({"detail": "Missing data"}, status=400)

    try:
        p.clean_fields()
    except ValidationError:
        return JsonResponse({"detail": "Data validation error"}, status=400)

    p.save()

    return JsonResponse(p.serialize_json())
