""" context manager based trackers for profiling requests and background jobs
"""

import time
from collections import ChainMap
import functools
from typing import ContextManager, Mapping, List

from django.http.request import HttpRequest
from django.http.response import HttpResponse


def ready_property(arg):
    class _r:
        def __init__(self, getter):
            self.getter = getter

        def __get__(self, obj, objtype=None):
            if obj is None:
                return self

            obj.raise_if_not_ready()
            return self.getter(obj)

    return _r(arg)


class Tracker(ContextManager):  # pylint: disable=E0239
    """ tracker is a timing context manager that you can do other tracking with """

    _entered: bool = False
    _exited: bool = False
    ready: bool = False
    ctx: ChainMap
    parent: "Tracker" = None
    children: Mapping[str, "Tracker"]

    def __init__(
        self, start: Mapping = None, parent: "Tracker" = None
    ):  # pylint: disable=W0231
        if not start:
            start = {}
        if isinstance(start, ChainMap):
            self.ctx = start
        else:
            self.ctx = ChainMap(start)

        self.children = {}
        if parent:
            self.parent = parent

    def __enter__(self,) -> "Tracker":
        if self.parent:
            assert (
                self.parent._entered
            ), "the parent tracker must be entered to exit the child tracker"
        self._enter_tracker()
        self.ctx.update(
            dict(
                _start_perf_counter=time.perf_counter(),
                _start_process_time=time.process_time(),
                _start_time=time.time(),
            )
        )
        self._entered = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for child in self.children.values():
            if not child._exited:
                child.__exit__()
        assert (
            self._entered
        ), f"cannot exit a {__class__.__name__} that hasn't been entered"
        self.ctx.update(
            dict(
                _end_perf_counter=time.perf_counter(),
                _end_process_time=time.process_time(),
                _end_time=time.time(),
            )
        )
        self._exit_tracker()
        self._exited = True

    def _enter_tracker(self,):
        """ subclasses may implement behavior for tracker start """
        pass

    def _exit_tracker(self,):
        """ subclasses may implement behavior for tracker end """
        pass

    def _prepare_log(self,) -> Mapping:
        return {k: v for k, v in self.ctx.items() if not k.startswith("_")}

    def _check_complete(self,) -> bool:
        return True

    def raise_if_not_ready(self):
        if self.ready:
            return
        assert (
            self._exited
        ), f"{__class__.__name__} hasn't exited yet, so statistics aren't yet available"
        assert (
            self._check_complete()
        ), f"{__class__.__name__} hasn't been passed all necessary data yet"
        self.ready = True

    def new_child(self, name, tracker_cls=None) -> "Tracker":
        """ create a child tracker """

        if name in self.children.keys():
            raise ValueError(f"Child tracker named {name} already exists!")
        if tracker_cls is None:
            tracker_cls = self.__class__
        child = tracker_cls(start=self.ctx.new_child(), parent=self)
        self.children[name] = child
        return child

    @ready_property
    def perf_counter(self):
        """ get the delta of time.perf_counter() for the request """
        return self.ctx["_end_perf_counter"] - self.ctx["_start_perf_counter"]

    @ready_property
    def process_time(self):
        """ get the delta of time.process_time() for the request """
        return self.ctx["_end_process_time"] - self.ctx["_start_process_time"]

    @ready_property
    def time(self):
        return self.ctx["_end_time"] - self.ctx["_start_time"]

    @ready_property
    def log(self):
        log = self._prepare_log()

        # TODO: Rollup child time and also unaccounted for time

        log.update(
            dict(
                time=self.time,
                process_time=self.process_time,
                perf_counter=self.perf_counter,
            )
        )
        return log


class RequestTracker(Tracker):
    """ a basic tracker for the django http request/response cycle """

    # TODO: installation specific parameters

    def __init__(self, request):
        super().__init__()
        self.ctx["request"] = request

    def _check_complete(self):
        assert (
            self.response
        ), f"stats for {__class__.__name__} not available til response is set"
        return True

    @property
    def response(self) -> HttpResponse:
        return self.ctx["response"]

    @response.setter
    def response(self, value: HttpResponse):
        self.ctx["response"] = value

    @property
    def request(self) -> HttpRequest:
        return self.ctx["request"]

    def _prepare_log(self,) -> Mapping:
        return dict(
            request_id=self.request.request_id,
            request_content_type=self.request.content_type,
            request_ip=self.request.META["REMOTE_ADDR"],
            request_method=self.request.method,
            request_path=self.request.path,
            user_agent=self.request.META["HTTP_USER_AGENT"],
            response_content_type=self.response["Content-Type"],
            response_status=self.response.status_code,
            user_id=getattr(getattr(self.request, "user", {}), "id", None),
        )
