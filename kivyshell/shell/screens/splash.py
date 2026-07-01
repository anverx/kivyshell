"""Splash screen: a full-bleed themed image shown at startup."""

from __future__ import annotations

from typing import Any

from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen

from ...uikit.theme import get_theme


class SplashScreen(Screen):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.add_widget(Image(source=get_theme().background_image, fit_mode="cover"))

    def set_status(self, text: str) -> None:
        """No-op, kept for API compatibility with apps that report load status."""
