"""Mocked unit tests for keyloggerapp (NO live OS keyboard hooks)."""

from __future__ import annotations

import importlib
import os
import sys
import tempfile
import types
import unittest
from unittest.mock import MagicMock, patch

from keylogger import keylogger


def _make_fake_pynput() -> tuple[types.ModuleType, MagicMock, MagicMock, object]:
    """Create a synthetic pynput module with a mocked keyboard.Listener."""
    fake_pynput = types.ModuleType("pynput")
    fake_keyboard = types.ModuleType("pynput.keyboard")
    esc_sentinel = types.SimpleNamespace(name="esc")
    fake_keyboard.Key = types.SimpleNamespace(esc=esc_sentinel)

    listener_instance = MagicMock()
    listener_instance.__enter__.return_value = listener_instance
    listener_instance.__exit__.return_value = False
    listener_cls = MagicMock(return_value=listener_instance)
    fake_keyboard.Listener = listener_cls

    fake_pynput.keyboard = fake_keyboard
    return fake_pynput, listener_cls, listener_instance, esc_sentinel


class TestImportSafety(unittest.TestCase):
    def test_import_and_reload_never_starts_listener(self) -> None:
        fake_pynput, listener_cls, listener_instance, _ = _make_fake_pynput()
        with patch.dict(
            sys.modules,
            {"pynput": fake_pynput, "pynput.keyboard": fake_pynput.keyboard},
        ):
            reloaded = importlib.reload(keylogger)
            self.assertIsNotNone(reloaded)
            listener_cls.assert_not_called()
            listener_instance.join.assert_not_called()


class TestKeyFormattingAndLogging(unittest.TestCase):
    def test_format_key_event_handles_char_none_and_missing_attr(self) -> None:
        char_key = types.SimpleNamespace(char="a")
        self.assertEqual(keylogger.format_key_event(char_key), "a")

        none_char_key = types.SimpleNamespace(char=None)
        result_none = keylogger.format_key_event(none_char_key)
        self.assertNotEqual(result_none, "None")
        self.assertEqual(result_none, str(none_char_key))

        class SpecialKey:
            def __str__(self) -> str:
                return "Key.space"

        self.assertEqual(keylogger.format_key_event(SpecialKey()), "Key.space")

    def test_append_log_entry_writes_and_handles_os_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "sub", "test.log")
            self.assertTrue(keylogger.append_log_entry(log_path, "x"))
            self.assertTrue(keylogger.append_log_entry(log_path, "Key.enter"))
            with open(log_path, "r", encoding="utf-8") as fh:
                self.assertEqual(fh.read(), "x\nKey.enter\n")

        with patch("builtins.open", side_effect=OSError("permission denied")):
            self.assertFalse(keylogger.append_log_entry("unwritable.log", "a"))

    def test_create_on_press_logs_formatted_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "press.log")
            on_press = keylogger.create_on_press(log_path)
            on_press(types.SimpleNamespace(char="k"))
            on_press(types.SimpleNamespace(char=None))
            with open(log_path, "r", encoding="utf-8") as fh:
                lines = fh.read().splitlines()
            self.assertEqual(lines[0], "k")
            self.assertNotEqual(lines[1], "None")


class TestReleaseAndConsentGate(unittest.TestCase):
    def test_on_release_stops_on_esc_and_continues_otherwise(self) -> None:
        fake_pynput, _, _, esc_sentinel = _make_fake_pynput()
        with patch.dict(
            sys.modules,
            {"pynput": fake_pynput, "pynput.keyboard": fake_pynput.keyboard},
        ):
            self.assertFalse(keylogger.on_release(esc_sentinel))
            self.assertIsNone(keylogger.on_release(types.SimpleNamespace(char="a")))

    def test_main_blocks_listener_without_explicit_confirmation(self) -> None:
        fake_pynput, listener_cls, _, _ = _make_fake_pynput()
        outputs: list[str] = []
        with patch.dict(
            sys.modules,
            {"pynput": fake_pynput, "pynput.keyboard": fake_pynput.keyboard},
        ):
            code = keylogger.main(
                argv=["--log-file", "dummy.log"],
                input_fn=lambda _: "no",
                output_fn=outputs.append,
            )
            self.assertEqual(code, 1)
            listener_cls.assert_not_called()

            code_eof = keylogger.main(
                argv=["--log-file", "dummy.log"],
                input_fn=lambda _: (_ for _ in ()).throw(EOFError()),
                output_fn=outputs.append,
            )
            self.assertEqual(code_eof, 1)
            listener_cls.assert_not_called()

    def test_main_wires_mocked_listener_when_confirmed(self) -> None:
        fake_pynput, listener_cls, listener_instance, esc_sentinel = _make_fake_pynput()
        outputs: list[str] = []
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "session.log")
            with patch.dict(
                sys.modules,
                {"pynput": fake_pynput, "pynput.keyboard": fake_pynput.keyboard},
            ):
                code = keylogger.main(
                    argv=["--log-file", log_path, "--i-understand-educational-use"],
                    output_fn=outputs.append,
                )
            self.assertEqual(code, 0)
            listener_cls.assert_called_once()
            kwargs = listener_cls.call_args.kwargs
            self.assertTrue(callable(kwargs["on_press"]))
            self.assertTrue(callable(kwargs["on_release"]))
            listener_instance.join.assert_called_once()

            # Verify wired callbacks against temp file and Esc sentinel
            kwargs["on_press"](types.SimpleNamespace(char="z"))
            self.assertFalse(kwargs["on_release"](esc_sentinel))
            with open(log_path, "r", encoding="utf-8") as fh:
                self.assertEqual(fh.read(), "z\n")


if __name__ == "__main__":
    unittest.main()
