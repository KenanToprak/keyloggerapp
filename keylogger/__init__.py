"""Educational keyboard listener package (authorized local use only)."""

from keylogger.keylogger import (
    DEFAULT_LOG_PATH,
    append_log_entry,
    create_listener,
    create_on_press,
    format_key_event,
    main,
    on_release,
    run_listener,
)

__all__ = [
    "DEFAULT_LOG_PATH",
    "append_log_entry",
    "create_listener",
    "create_on_press",
    "format_key_event",
    "main",
    "on_release",
    "run_listener",
]
