"""Views for productivity app."""

from django.core.exceptions import ValidationError
from django.http import HttpRequest, JsonResponse

from productivity.models import Productivity


def index(request: HttpRequest) -> JsonResponse:
    """Create Productivity object if POST.

    Args:
        request:
            HttpRequest object.
                - If POST, below data required in body.
                    - item
                    - frequency
                    - group

    Returns:
        JSON Response of Productivity object or error message.
    """
    if request.method == "POST":
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

    return JsonResponse({"error": "Request method not allowed"}, status=405)
