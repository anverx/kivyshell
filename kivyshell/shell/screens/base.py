"""Base screen scaffold: background image + white overlay + content column.

Ported from yaque's screens/base.py. Background/overlay/spacing come from the
theme; navigation assumes the shell's ScreenManager convention (a 'menu' screen).
Subclasses override build_content() to populate self.content_layout.
"""

from __future__ import annotations

from typing import Any

from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen

from ...uikit import BackButton, styled
from ...uikit.theme import SPACING, get_theme


class BackgroundedScreen(Screen):
    """Screen with a themed background image, white overlay, and content column."""

    def __init__(self, app: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.app = app

        root = FloatLayout()
        root.add_widget(Image(source=get_theme().background_image, fit_mode="cover"))

        overlay = BoxLayout()
        with overlay.canvas:
            Color(*get_theme().overlay)
            self._overlay_rect = Rectangle(pos=overlay.pos, size=overlay.size)
        overlay.bind(pos=self._update_overlay, size=self._update_overlay)
        root.add_widget(overlay)

        self.content_layout = BoxLayout(orientation="vertical",
                                        padding=dp(self.get_padding()), spacing=dp(self.get_spacing()))
        self.content_layout.add_widget(styled(BoxLayout, "top_spacer"))
        self.build_content()
        root.add_widget(self.content_layout)
        self.add_widget(root)

    def _update_overlay(self, instance: Any, value: Any) -> None:
        self._overlay_rect.pos = instance.pos
        self._overlay_rect.size = instance.size

    def get_padding(self) -> int:
        return SPACING["xxl"]

    def get_spacing(self) -> int:
        return SPACING["lg"]

    def build_content(self) -> None:
        """Override to add widgets to self.content_layout."""

    def add_back_button(self) -> BackButton:
        """A standard back button that returns to the menu, pushed to the bottom."""
        self.content_layout.add_widget(BoxLayout(size_hint_y=0.1))
        back_btn = BackButton()
        back_btn.bind(on_press=lambda x: setattr(self.app.sm, "current", "menu"))
        self.content_layout.add_widget(back_btn)
        return back_btn
