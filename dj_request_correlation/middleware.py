import uuid
from typing import Callable

from django.conf import settings
from django.http.request import HttpRequest
from django.http.response import HttpResponse

from . import current_request_id
from .utils import ClassBasedMiddleware

request_id_header: str = getattr(settings, "REQUEST_ID_HEADER", "X-Request-Id")


def get_request_id(request: HttpRequest, default: Callable = None) -> str:
    """
    Get the request ID from the configrued HTTP header, or generate one.

    We attempt to take the header from the HTTP request, and if there isn't one,
    generate one by calling `default`."""

    # we need to turn the HTTP Header string into the nonsense that WSGI uses
    # in order to retrieve the header from the django request META object.
    meta_header = "HTTP_" + request_id_header.replace("-", "_").upper()
    return request.META.get(meta_header, default())


class RequestIDMiddleware(ClassBasedMiddleware):
    """ RequestIDMiddleware assigns a request ID to every HTTP request
    as `request.request_id` for correlation across services and logs.

    Defaults to configurations for Heroku's `X-Request-ID` correlation header,
    which is probably the closest there is to a standard. Override the REQUEST_ID_HEADER
    setting to specify a custom header.

    The request ID is added to the HttpRequest object for other code to use and
    be aware of it. It's also stored in a ContextVar for when you need to access the
    current request id without passsing it around, like in the logger.

    This should be your VERY first middleware, so that even if a request is denied by
    the SecurityMiddleware, you can correlate it with the router logs."""

    def __call__(self, request: HttpRequest) -> HttpResponse:
        req_id = get_request_id(request, uuid.uuid4)

        # set the request ID in a thread local ContextVar and the current request.
        current_request_id.set(req_id)
        request.request_id = req_id

        # run the view and the rest of the middleware chain
        response = super().__call__(request=request)

        # include the request ID (in the same header) in the response
        response[request_id_header] = req_id
        return response

