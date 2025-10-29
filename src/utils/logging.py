import sys
import logging
from pythonjsonlogger import jsonlogger
import structlog
from src.config.settings import settings
from src.config.constants import Environment

def _make_stdlib_handler() -> logging.Handler:
    """Create a stdlib handler with appropriate formatter based on environment."""
    handler = logging.StreamHandler(sys.stdout)

    if settings.ENVIRONMENT == Environment.DEVELOPMENT or settings.DEBUG:
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(fmt)
    else:
        json_fmt = "%(asctime)s %(name)s %(levelname)s %(message)s"
        formatter = jsonlogger.JsonFormatter(json_fmt)

    handler.setFormatter(formatter)
    return handler

def setup_logging() -> None:
    """
    Configure stdlib logging + structlog:
    - stdlib root logger gets a StreamHandler (human or JSON).
    - structlog configured with processors and JSON/console renderer.
    Call once at application startup (e.g. in `main()` or FastAPI startup).
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.addHandler(_make_stdlib_handler())

    renderer = (
        structlog.dev.ConsoleRenderer(colors=True)
        if settings.ENVIRONMENT == Environment.DEVELOPMENT or settings.DEBUG
        else structlog.processors.JSONRenderer()
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            renderer,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

def get_logger(name: str = None):
    """
    Return a structlog-bound logger. Use this for app logging.
    Example: logger = get_logger(__name__); logger.info("hello", foo=1)
    """
    return structlog.get_logger(name)
