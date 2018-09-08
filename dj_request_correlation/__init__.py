__version__ = "0.1.0"

from contextvars import ContextVar


current_request_id: ContextVar[str] = ContextVar("request_id")
