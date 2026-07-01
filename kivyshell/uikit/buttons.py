"""Rounded/icon/selectable buttons + a completion badge.

Ported from yaque's widgets/buttons.py. Colors, fonts and icon paths come from
the active theme (`kivyshell.uikit.theme`) instead of an app constants module, so
the game-specific bits (the "crown" badge icon/color, the icons directory) are
supplied by each app's Theme rather than hard-coded.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, PopMatrix, PushMatrix, Rectangle, Rotate, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from .labels import IconLabel, styled
from .theme import (
    BUTTON_HEIGHT,
    ICON_BTN_SIZE,
    ICON_LABEL_HEIGHT,
    ICON_LABEL_TOTAL,
    RADIUS,
    get_styles,
    get_theme,
)

__all__ = [
    "ColorTuple", "RoundedButton", "GrayRoundedButton", "FixedRoundedButton",
    "TallRoundedButton", "FixedGrayRoundedButton", "SmallRoundedButton",
    "BackButton", "LinkButton", "CompletionBadge", "CrownBadge", "SelectableButton",
    "SelectableButtonGroup", "IconButton", "disable_widget",
]

ColorTuple = tuple[float, float, float, float]


class RoundedButton(ButtonBehavior, Label):
    """A button with rounded corners. Colors default to the active theme."""

    def __init__(self, bg_color: ColorTuple | None = None,
                 bg_color_down: ColorTuple | None = None, **kwargs: Any) -> None:
        theme = get_theme()
        kwargs.setdefault("font_name", theme.font_name)
        kwargs.setdefault("font_size", theme.button_font_size)
        kwargs.setdefault("color", theme.text_white)
        kwargs.setdefault("markup", True)
        kwargs.setdefault("halign", "center")
        kwargs.setdefault("valign", "middle")
        kwargs.setdefault("height", dp(BUTTON_HEIGHT["md"]))
        super().__init__(**kwargs)
        self.bg_color = bg_color or theme.button
        self.bg_color_down = bg_color_down or theme.button_down
        self._radius = dp(RADIUS["md"])
        self._update_bg()
        self.bind(pos=self._update_bg, size=self._update_bg, state=self._update_bg)
        self.bind(size=self._update_text_size)

    def _update_text_size(self, *args: Any) -> None:
        self.text_size = self.size

    def _update_bg(self, *args: Any) -> None:
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*(self.bg_color_down if self.state == "down" else self.bg_color))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self._radius])


def GrayRoundedButton(**kwargs: Any) -> RoundedButton:
    theme = get_theme()
    kwargs.setdefault("color", theme.text_dark)
    return RoundedButton(bg_color=theme.button_gray, bg_color_down=theme.button_gray_down, **kwargs)


def FixedRoundedButton(**kwargs: Any) -> RoundedButton:
    kwargs.setdefault("size_hint_y", None)
    return RoundedButton(**kwargs)


def TallRoundedButton(**kwargs: Any) -> RoundedButton:
    kwargs.setdefault("size_hint_y", None)
    return RoundedButton(**get_styles()["tall_btn"], **kwargs)


def FixedGrayRoundedButton(**kwargs: Any) -> RoundedButton:
    kwargs.setdefault("size_hint_y", None)
    return GrayRoundedButton(**kwargs)


def SmallRoundedButton(**kwargs: Any) -> RoundedButton:
    kwargs.setdefault("font_size", "14sp")
    return RoundedButton(**kwargs)


def BackButton(**kwargs: Any) -> RoundedButton:
    kwargs.setdefault("text", "Back")
    return FixedGrayRoundedButton(**get_styles()["back_btn"], **kwargs)


def LinkButton(text: str, **kwargs: Any) -> Button:
    return styled(Button, "link_btn", text=text, **kwargs)


class CompletionBadge:
    """A tilted badge icon drawn on a button's canvas.before (menu completion mark).

    Icon and color come from the theme (`badge_icon`, `badge_on_time`). yaque uses
    a gold crown; yawop can point `badge_icon` at a stylized 'W'."""

    def __init__(self, btn: RoundedButton, visible: bool = False) -> None:
        self.btn = btn
        self.visible = visible
        # Instance-level texture so a later set_theme (dark mode, yawop's W badge,
        # tests) is honored; drawn to canvas.after so the button's own
        # canvas.before bg redraw can't clobber it (no callback-order dependency).
        self._texture = CoreImage(get_theme().badge_icon).texture
        btn.bind(pos=self._draw, size=self._draw, state=self._draw)

    def show(self) -> None:
        self.visible = True
        self._draw()

    def hide(self) -> None:
        self.visible = False
        self.btn.canvas.after.clear()

    def _draw(self, *args: Any) -> None:
        self.btn.canvas.after.clear()
        if not self.visible:
            return
        btn = self.btn
        with btn.canvas.after:
            Color(*get_theme().badge_on_time)
            icon_size = btn.height * 0.4
            ix = btn.right - icon_size - dp(4)
            iy = btn.top - icon_size - dp(2)
            PushMatrix()
            Rotate(angle=-20, origin=(ix + icon_size / 2, iy + icon_size / 2))
            Rectangle(texture=self._texture, pos=(ix, iy), size=(icon_size, icon_size))
            PopMatrix()


# Back-compat alias (yaque calls it CrownBadge).
CrownBadge = CompletionBadge


class SelectableButton(RoundedButton):
    """A radio-style selectable button. Use with SelectableButtonGroup."""

    def __init__(self, selected: bool = False, **kwargs: Any) -> None:
        if not selected:
            kwargs.setdefault("bg_color", get_theme().button_unselected)
        super().__init__(**kwargs)
        self._selected = selected

    @property
    def selected(self) -> bool:
        return self._selected

    @selected.setter
    def selected(self, value: bool) -> None:
        self._selected = value
        self.bg_color = get_theme().button_down if value else get_theme().button_unselected
        self._update_bg()


class SelectableButtonGroup:
    """Manages a group of SelectableButtons for radio-style selection."""

    def __init__(self, on_select: Callable[[Any], None] | None = None) -> None:
        self.buttons: dict[Any, SelectableButton] = {}
        self.selected_value: Any = None
        self.on_select = on_select

    def add(self, value: Any, button: SelectableButton) -> None:
        self.buttons[value] = button
        button.bind(on_press=lambda btn: self.select(value))
        if button.selected:
            self.selected_value = value

    def select(self, value: Any) -> None:
        self.selected_value = value
        for v, btn in self.buttons.items():
            btn.selected = (v == value)
        if self.on_select:
            self.on_select(value)


class IconButton(ButtonBehavior, BoxLayout):
    """A clickable image button with optional caption. Icons resolve against
    `theme.icons_dir` by name."""

    def __init__(self, icon_name: str, size_dp: int = ICON_BTN_SIZE,
                 label: str | None = None, **kwargs: Any) -> None:
        super().__init__(orientation="vertical", **kwargs)
        self.icon_name = icon_name
        self.size_hint = (None, None)

        self.icon = Image(source=self._icon_path(icon_name), size_hint=(None, None),
                          size=(dp(size_dp), dp(size_dp)), fit_mode="contain")
        self.add_widget(self.icon)

        if label:
            self.label_widget = IconLabel(label, size_hint=(None, None),
                                          size=(dp(size_dp), dp(ICON_LABEL_HEIGHT)), halign="center")
            self.label_widget.bind(size=self.label_widget.setter("text_size"))
            self.add_widget(self.label_widget)
            self.size = (dp(size_dp), dp(size_dp + ICON_LABEL_TOTAL))
        else:
            self.size = (dp(size_dp), dp(size_dp))

    @staticmethod
    def _icon_path(icon_name: str) -> str:
        return os.path.join(get_theme().icons_dir, f"{icon_name}.png")

    def set_icon(self, icon_name: str, label: str | None = None) -> None:
        self.icon_name = icon_name
        self.icon.source = self._icon_path(icon_name)
        if label and hasattr(self, "label_widget"):
            self.label_widget.text = label


def disable_widget(widget: Widget) -> None:
    widget.disabled = True
    widget.opacity = get_theme().disabled_opacity
