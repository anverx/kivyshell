"""Animated loading spinner.

Generalized from yaque's QueenSpinner: a themed icon (`theme.loader_icon`)
spinning inside a bordered white circle. yaque uses a queen; yawop can use any
icon. `QueenSpinner` is kept as a back-compat alias.
"""

from __future__ import annotations

from typing import Any

from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, Ellipse, Line, PopMatrix, PushMatrix, Rectangle, Rotate
from kivy.metrics import dp
from kivy.uix.widget import Widget

from .theme import SPINNER_LINE_WIDTH, get_theme

__all__ = ["LoaderSpinner", "QueenSpinner"]


class LoaderSpinner(Widget):
    """A spinning themed icon for loading indicators."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.rotation_angle: float = 0
        self.icon_texture = CoreImage(get_theme().loader_icon).texture
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *args: Any) -> None:
        self.canvas.clear()
        w, h = self.size
        x, y = self.pos
        cx, cy = x + w / 2, y + h / 2
        circle_radius = min(w, h) / 2 * 0.7
        icon_size = circle_radius * 1.3
        theme = get_theme()
        with self.canvas:
            Color(*theme.text_white)
            Ellipse(pos=(cx - circle_radius, cy - circle_radius),
                    size=(circle_radius * 2, circle_radius * 2))
            Color(*theme.spinner_border)
            Line(ellipse=(cx - circle_radius, cy - circle_radius, circle_radius * 2, circle_radius * 2),
                 width=dp(SPINNER_LINE_WIDTH))
            PushMatrix()
            Rotate(angle=self.rotation_angle, origin=(cx, cy))
            Color(*theme.text_white)
            Rectangle(pos=(cx - icon_size / 2, cy - icon_size / 2),
                      size=(icon_size, icon_size), texture=self.icon_texture)
            PopMatrix()

    def rotate(self, angle_delta: float = 3) -> None:
        self.rotation_angle = (self.rotation_angle + angle_delta) % 360
        self._draw()

    def reset(self) -> None:
        self.rotation_angle = 0
        self._draw()


# Back-compat alias (yaque calls it QueenSpinner).
QueenSpinner = LoaderSpinner
