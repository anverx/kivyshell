"""Text input factories (ported from yaque's widgets/core.py)."""

from __future__ import annotations

from typing import Any

from kivy.uix.textinput import TextInput

from .labels import styled

__all__ = ["UrlInput", "CodeInput"]


def UrlInput(text: str, **kwargs: Any) -> TextInput:
    """Readonly text input for displaying URLs (small font, selectable)."""
    return styled(TextInput, "url_input", text=text, **kwargs)


def CodeInput(**kwargs: Any) -> TextInput:
    """Text input for entering codes."""
    kwargs.setdefault("hint_text", "Enter code here...")
    return styled(TextInput, "code_input", **kwargs)
