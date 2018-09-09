""" most of dj-request-correlation is django MIDDLEWARE classes

we use "new" (its been this way for a looong time) style MIDDLEWARE
"""
import uuid
import time
import logging
from typing import Callable

from django.db import connection
from django.conf import settings
from django.http.request import HttpRequest
from django.http.response import HttpResponse


from . import current_request_id
from .utils import ClassBasedMiddleware, logfmt

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


parent_logger = logging.getLogger("dj_request_correlation")
canonical_logger = logging.getLogger("dj_request_correlation.canonical")


class RequestTracker:
    def __init__(self, request):
        self.request = request
        self.response = None
        self.canonical_context = {}
        self.entered = False
        self.exited = False

    def __enter__(self,):
        self.canonical_context = dict(
            _start_perf_counter=time.perf_counter(),
            _start_process_time=time.process_time(),
        )
        self.entered = True
        return self

    def set_response(self, response):
        self.response = response

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert (
            self.entered
        ), f"{__class__.__name__} wasn't entered, so you cannot exit it"
        self.canonical_context.update(
            dict(
                _end_perf_counter=time.perf_counter(),
                _end_process_time=time.process_time(),
            )
        )
        self.exited = True

    def _check_exited(self):
        assert (
            self.exited
        ), f"{__class__.__name__} hasn't exited yet, so statistics aren't yet available"

    @property
    def perf_counter(self):
        self._check_exited()
        return (
            self.canonical_context["_end_perf_counter"]
            - self.canonical_context["_start_perf_counter"]
        )

    @property
    def process_time(self):
        self._check_exited()
        return (
            self.canonical_context["_end_process_time"]
            - self.canonical_context["_start_process_time"]
        )


class CanonicalLogLineMiddleware(ClassBasedMiddleware):
    """ CanonicalLogLineMiddleware emits a (you guessed it) canonical log line for
    every HTTP request, to the "dj_request_correlation.canonical" logger.
    """

    # TODO: installation specific parameters
    # TODO: should_not_log view decorator? route decorator? somethin.

    def __call__(self, request: HttpRequest) -> HttpResponse:
        with RequestTracker(request) as ctx:
            response = super().__call__(request=request)
            ctx.set_response(response)

        self._log_response(request, response, ctx)
        return response

    def _log_response(
        self, request: HttpRequest, response: HttpResponse, ctx: RequestTracker
    ) -> None:
        # breakpoint()
        log = logfmt(
            request_id=request.request_id,
            request_content_type=request.content_type,
            request_ip=request.META["REMOTE_ADDR"],
            request_method=request.method,
            request_path=request.path,
            user_agent=request.META["HTTP_USER_AGENT"],
            response_content_type=response["Content-Type"],
            response_status=response.status_code,
            user_id=getattr(getattr(request, "user", {}), "id", None),
            perf_counter=ctx.perf_counter,
            process_time=ctx.process_time,
        )
        canonical_logger.info(log)
