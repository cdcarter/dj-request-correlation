from abc import ABC, abstractmethod
from typing import Callable, Any, Iterable, Mapping, Optional

from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.template.response import (
    SimpleTemplateResponse
)  # it feels weird to import these deep types just to get the annotation correct...


class ClassBasedMiddleware(ABC):
    """ ClassBasedMiddleware handles the Django MIDDLEWARE protocol """

    get_response: Callable[[], HttpResponse]

    def __init__(self, get_response: Callable[[], HttpResponse]) -> None:
        self.get_response = get_response

    @abstractmethod
    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)  # execute the view
        return response

    def process_view(
        self,
        request: HttpRequest,
        view_func: Callable[..., HttpResponse],
        view_args: Iterable[Any],
        view_kwargs: Mapping[Any, Any],
    ) -> Optional[HttpResponse]:
        return None

    def process_exception(self, exception: Exception) -> Optional[HttpResponse]:
        return None

    def process_template_response(
        self, request: HttpRequest, response: SimpleTemplateResponse
    ) -> SimpleTemplateResponse:
        return response
