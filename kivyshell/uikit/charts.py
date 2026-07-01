"""Bar chart widget (ported from yaque's widgets/bar_chart.py).

Generic: bars can be simple (int) or stacked (dict key->count). The stacked
segment colors are supplied by the caller via `segment_colors` rather than being
hard-coded to board sizes, so the chart knows nothing about a specific game.
Font/label color come from the theme.
"""

from __future__ import annotations

from typing import Any

from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from .theme import RADIUS, get_theme

__all__ = ["BarChart"]

_Y_AXIS_WIDTH = dp(28)
_DEFAULT_SEGMENT_COLOR = (1, 1, 1, 0.85)
_MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


class BarChart(BoxLayout):
    """A vertical bar chart with axis labels and guide lines.

    data: list of (label, {key: count}) for stacked bars, or (label, int) for simple bars.
    bar_color: color for simple bars (defaults to theme.button).
    segment_colors: {key: color} for stacked-bar segments (unknown keys -> white).
    """

    def __init__(self, data: list[tuple[str, dict[Any, int] | int]],
                 bar_color: tuple[float, ...] | None = None,
                 segment_colors: dict[Any, tuple[float, ...]] | None = None,
                 **kwargs: Any) -> None:
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("size_hint_y", None)
        super().__init__(**kwargs)
        self.data = data
        self.bar_color = bar_color or get_theme().button
        self.segment_colors = segment_colors or {}
        self.height = dp(180)

        max_val = 0
        for _, val in data:
            max_val = max(max_val, sum(val.values()) if isinstance(val, dict) else val)

        chart_row = BoxLayout(orientation="horizontal", size_hint_y=1)
        chart_row.add_widget(_YAxis(max_val=max_val, size_hint_x=None, width=_Y_AXIS_WIDTH))
        chart_row.add_widget(_BarArea(data=data, bar_color=self.bar_color,
                                      segment_colors=self.segment_colors, max_val=max_val, size_hint_y=1))
        self.add_widget(chart_row)

        bottom_row = BoxLayout(size_hint_y=None, height=dp(14))
        bottom_row.add_widget(Widget(size_hint_x=None, width=_Y_AXIS_WIDTH))
        label_row = BoxLayout(size_hint_x=1)
        if data:
            n = len(data)
            seen, unique_positions = set(), []
            for p in [0, n // 4, n // 2, 3 * n // 4, n - 1]:
                if p not in seen:
                    seen.add(p)
                    unique_positions.append(p)
            prev = 0
            font_name, text_light = get_theme().font_name, get_theme().text_light
            for pos in unique_positions:
                if pos > prev:
                    label_row.add_widget(Widget(size_hint_x=pos - prev))
                parts = data[pos][0][5:].split("-")  # "MM-DD"
                short = f"{_MONTHS[int(parts[0])]} {int(parts[1])}"
                lbl = Label(text=short, font_name=font_name, font_size="9sp", color=text_light,
                            size_hint_x=1, halign="center")
                lbl.bind(size=lbl.setter("text_size"))
                label_row.add_widget(lbl)
                prev = pos + 1
            if n - prev > 0:
                label_row.add_widget(Widget(size_hint_x=n - prev))
        bottom_row.add_widget(label_row)
        self.add_widget(bottom_row)


class _YAxis(Widget):
    """Vertical axis labels at 0/25/50/75/100% of max value."""

    def __init__(self, max_val: int, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.max_val = max_val
        self._labels: list[tuple[float, Label]] = []
        if max_val == 0:
            return
        seen_vals, fracs = set(), []
        for frac in [0, 0.25, 0.5, 0.75, 1.0]:
            val = int(max_val * frac)
            if val not in seen_vals:
                seen_vals.add(val)
                fracs.append((frac, val))
        font_name, text_light = get_theme().font_name, get_theme().text_light
        for frac, val in fracs:
            lbl = Label(text=str(val), font_name=font_name, font_size="9sp", color=text_light,
                        size_hint=(None, None), halign="right", valign="middle")
            lbl.size = (self.width, dp(12))
            lbl.text_size = lbl.size
            self._labels.append((frac, lbl))
            self.add_widget(lbl)
        self.bind(pos=self._layout, size=self._layout)

    def _layout(self, *args: Any) -> None:
        chart_h = self.height * 0.9
        for frac, lbl in self._labels:
            lbl.size = (self.width - dp(3), dp(12))
            lbl.text_size = lbl.size
            lbl.pos = (self.x, self.y + frac * chart_h - dp(6))


class _BarArea(Widget):
    """Canvas-based bar rendering area with guide lines."""

    def __init__(self, data: list[tuple[str, dict[Any, int] | int]], bar_color: tuple[float, ...],
                 segment_colors: dict[Any, tuple[float, ...]], max_val: int, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.data = data
        self.bar_color = bar_color
        self.segment_colors = segment_colors
        self.max_val = max_val
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *args: Any) -> None:
        self.canvas.clear()
        if not self.data or self.max_val == 0:
            return
        max_val = self.max_val
        chart_h = self.height * 0.9
        n = len(self.data)
        bar_width = self.width / n
        gap = max(dp(1), bar_width * 0.15)
        actual_bar_w = bar_width - gap
        radius = min(dp(RADIUS["sm"]), actual_bar_w / 2)

        with self.canvas:
            for frac in [0, 0.25, 0.5, 0.75, 1.0]:
                y = self.y + frac * chart_h
                Color(1, 1, 1, 0.2)
                Line(points=[self.x, y, self.x + self.width, y], width=1)

            for i, (_, val) in enumerate(self.data):
                x = self.x + i * bar_width + gap / 2
                if isinstance(val, dict):
                    y_offset = self.y
                    if sum(val.values()) == 0:
                        continue
                    segments = sorted(val.items())
                    for j, (key, count) in enumerate(segments):
                        if count == 0:
                            continue
                        seg_h = (count / max_val) * chart_h
                        Color(*self.segment_colors.get(key, _DEFAULT_SEGMENT_COLOR))
                        is_top = j == len(segments) - 1 or all(v == 0 for _, v in segments[j + 1:])
                        r = [radius, radius, 0, 0] if is_top else [0, 0, 0, 0]
                        RoundedRectangle(pos=(x, y_offset), size=(actual_bar_w, seg_h), radius=r)
                        y_offset += seg_h
                else:
                    if val == 0:
                        continue
                    bar_h = (val / max_val) * chart_h
                    Color(*self.bar_color)
                    RoundedRectangle(pos=(x, self.y), size=(actual_bar_w, bar_h), radius=[radius, radius, 0, 0])
