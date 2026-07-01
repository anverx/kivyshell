"""Layout primitives: rows, panels, popups, and small icon factories.

Ported from yaque's widgets/layouts.py — the game-agnostic pieces. The
calendar day cell and logbook row (which know about a specific game's
completion model and play schema) stay in the app and move to the L2 shell
screens later. Colors/dimensions come from the active theme.
"""

from __future__ import annotations

import os
from typing import Any

from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView
from kivy.uix.widget import Widget

from .labels import CaptionLabel, styled
from .theme import POPUP_WIDTH, RADIUS, STAT_ROW_HEIGHT, get_styles, get_theme

__all__ = [
    "PopupContent", "styled_layout", "ButtonRow", "SizeButtonRow", "PanelLayout",
    "StatRow", "DateSeparator", "Popup", "TypeIcon", "CompletionIcon", "CrownIcon",
]


def PopupContent(**kwargs: Any) -> BoxLayout:
    return styled(BoxLayout, "popup_content", **kwargs)


def styled_layout(style: str = "button_row", **overrides: Any) -> BoxLayout:
    return styled(BoxLayout, style, **overrides)


def ButtonRow(**kwargs: Any) -> BoxLayout:
    return styled_layout("button_row", **kwargs)


def SizeButtonRow(**kwargs: Any) -> BoxLayout:
    return styled_layout("button_row", **kwargs)


class PanelLayout(BoxLayout):
    """BoxLayout with a dark rounded background panel."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._update_panel_bg()
        self.bind(pos=self._update_panel_bg, size=self._update_panel_bg)

    def _update_panel_bg(self, *args: Any) -> None:
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_theme().panel_bg)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(RADIUS["sm"])])


class StatRow(BoxLayout):
    """A row with a light rounded background for stats display."""

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(STAT_ROW_HEIGHT))
        super().__init__(**kwargs)
        self._update_bg()
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *args: Any) -> None:
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_theme().row_bg)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(RADIUS["sm"])])


class DateSeparator(BoxLayout):
    """A date separator row (label on a transparent strip)."""

    def __init__(self, date_str: str, **kwargs: Any) -> None:
        style_props = get_styles().get("date_separator", {})
        for key in ("size_hint_y", "height", "padding"):
            if key in style_props:
                kwargs.setdefault(key, style_props[key])
        super().__init__(**kwargs)
        self.add_widget(CaptionLabel(date_str, color=get_theme().text_white, halign="left", valign="middle"))


def TypeIcon(is_daily: bool | Any, **kwargs: Any) -> Image:
    """Calendar icon for daily entries, dice for random. Resolves against
    theme.icons_dir (expects calendar.png / dice.png)."""
    icon_name = "calendar" if is_daily else "dice"
    kwargs.setdefault("color", get_theme().text_medium)
    kwargs.setdefault("fit_mode", "contain")
    return Image(source=os.path.join(get_theme().icons_dir, f"{icon_name}.png"), **kwargs)


def CompletionIcon(color: tuple[float, ...], **kwargs: Any) -> Image:
    """Small tinted completion badge icon (theme.badge_icon). yaque = crown."""
    kwargs.setdefault("fit_mode", "contain")
    return Image(source=get_theme().badge_icon, color=color, **kwargs)


# Back-compat alias (yaque calls it CrownIcon).
CrownIcon = CompletionIcon


def Popup(content: Widget, height: float, width_hint: float = POPUP_WIDTH,
          auto_dismiss: bool = True) -> ModalView:
    """A styled ModalView popup sized in dp height, size_hint_x width."""
    popup = ModalView(size_hint=(width_hint, None), height=dp(height),
                      auto_dismiss=auto_dismiss, background_color=get_theme().popup_bg)
    popup.add_widget(content)
    return popup
