"""Reusable calendar screen.

Renders the month grid, prev/next navigation, day-of-week header, streak label,
and swipe gestures. The game supplies (via CalendarConfig): a CalendarState-like
data source, a day-cell factory, the day-select action, and the month-badge color
mapping. Highlight colors come from the theme. No game logic lives here.

The data source (`new_state()`) must expose: `year`, `month`, `prev_month()`,
`next_month() -> bool` (False if it won't advance), and `fetch_data()` returning
an object with `month_name`, `streak_text`, `month_status` (date_iso -> per-variant
status), `month_crown`, and `protected_dates`.
"""

from __future__ import annotations

import calendar as _calendar
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

from ...uikit import DayLabel, MonthLabel, PanelLayout, RoundedButton, TitleSmLabel, disable_widget, styled
from ...uikit.theme import (
    PADDING_CELL,
    SPACING,
    SWIPE_DISTANCE_THRESHOLD,
    TOP_SPACER_HEIGHT,
    get_styles,
    get_theme,
)
from .base import BackgroundedScreen

_DAY_NAMES = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]


@dataclass
class CalendarConfig:
    new_state: Callable[[], Any]                       # -> CalendarState-like object
    make_cell: Callable[[int, Any], Any]               # (day, day_status) -> cell widget
    on_day: Callable[[date], None]                     # a past/today date was tapped
    month_badge_color: Callable[[Any], tuple | None]   # month_crown -> color, or None
    day_names: list[str] = field(default_factory=lambda: list(_DAY_NAMES))


class CalendarScreen(BackgroundedScreen):
    """Subclass and implement calendar_config()."""

    def calendar_config(self) -> CalendarConfig:
        raise NotImplementedError

    def build_content(self) -> None:
        cfg = self._config = self.calendar_config()
        self.cal_state = cfg.new_state()
        layout = self.content_layout

        layout.add_widget(BoxLayout(size_hint_y=None, height=dp(TOP_SPACER_HEIGHT)))

        header = styled(BoxLayout, "header_bar")
        prev_btn = RoundedButton(text="<", **get_styles()["nav_btn"])
        prev_btn.bind(on_press=self.prev_month)
        header.add_widget(prev_btn)
        self.month_label = MonthLabel("")
        header.add_widget(self.month_label)
        next_btn = RoundedButton(text=">", **get_styles()["nav_btn"])
        next_btn.bind(on_press=self.next_month)
        header.add_widget(next_btn)
        layout.add_widget(header)

        panel_pad_v = dp(PADDING_CELL[1] * 2)
        self.calendar_panel = PanelLayout(orientation="vertical", size_hint_y=None,
                                          padding=[dp(PADDING_CELL[0] * 2), panel_pad_v], spacing=dp(SPACING["min"]))
        days_header = styled(GridLayout, "days_header")
        for name in cfg.day_names:
            days_header.add_widget(DayLabel(name))
        self.calendar_panel.add_widget(days_header)

        self.calendar_grid = styled(GridLayout, "calendar_grid")
        self.calendar_grid.bind(minimum_height=self.calendar_grid.setter("height"))
        self.calendar_panel.add_widget(self.calendar_grid)

        def update_panel_height(*args: Any) -> None:
            self.calendar_panel.height = (days_header.height + self.calendar_grid.height
                                          + panel_pad_v * 2 + dp(SPACING["min"]))
        self.calendar_grid.bind(height=update_panel_height)
        days_header.bind(height=update_panel_height)
        layout.add_widget(self.calendar_panel)

        self.streak_label = TitleSmLabel("")
        layout.add_widget(self.streak_label)
        layout.add_widget(BoxLayout())
        self.add_back_button()

        self.refresh_calendar()

    def prev_month(self, instance: Any) -> None:
        self.cal_state.prev_month()
        self.refresh_calendar()

    def next_month(self, instance: Any) -> None:
        if self.cal_state.next_month():
            self.refresh_calendar()

    def _style_month_label(self) -> None:
        from kivy.graphics import Color, RoundedRectangle
        lbl = self.month_label
        lbl.color = get_theme().text_white
        with lbl.canvas.before:
            Color(*get_theme().button)
            RoundedRectangle(pos=lbl.pos, size=lbl.size, radius=[dp(8)])

    def _draw_month_badge(self, color: tuple[float, ...]) -> None:
        from kivy.core.image import Image as CoreImage
        from kivy.graphics import Color, PopMatrix, PushMatrix, Rectangle, Rotate
        # Load per-draw (called once per calendar refresh) so a theme change is
        # honored, rather than caching the first theme's badge icon on the class.
        texture = CoreImage(get_theme().badge_icon).texture
        lbl = self.month_label
        icon_size = lbl.height * 0.45
        ix = lbl.right - icon_size - dp(4)
        iy = lbl.top - icon_size - dp(2)
        with lbl.canvas.after:
            Color(*color)
            PushMatrix()
            Rotate(angle=-20, origin=(ix + icon_size / 2, iy + icon_size / 2))
            Rectangle(texture=texture, pos=(ix, iy), size=(icon_size, icon_size))
            PopMatrix()

    def refresh_calendar(self) -> None:
        cfg = self._config
        st = self.cal_state
        data = st.fetch_data()

        self.month_label.text = data.month_name
        self.month_label.canvas.before.clear()
        self.month_label.canvas.after.clear()
        self.calendar_grid.clear_widgets()
        self.streak_label.text = data.streak_text

        today = date.today()
        self._style_month_label()

        badge_color = cfg.month_badge_color(data.month_crown)
        if badge_color:
            self._draw_month_badge(badge_color)

        for day in _calendar.Calendar(firstweekday=0).itermonthdays(st.year, st.month):
            if day == 0:
                self.calendar_grid.add_widget(styled(Label, "cell", text=""))
                continue
            day_date = date(st.year, st.month, day)
            status = data.month_status.get(day_date.isoformat())
            cell = cfg.make_cell(day, status)
            if day_date > today:
                disable_widget(cell)
            else:
                cell.bind(on_press=lambda x, d=day_date: cfg.on_day(d))
                if day_date == today:
                    cell.background_color = get_theme().calendar_today
                elif day_date.isoformat() in data.protected_dates:
                    cell.background_color = get_theme().calendar_protected
            self.calendar_grid.add_widget(cell)

    def on_enter(self) -> None:
        self.refresh_calendar()

    def on_touch_down(self, touch: Any) -> bool:
        touch.ud["start_x"] = touch.x
        touch.ud["start_y"] = touch.y
        return super().on_touch_down(touch)

    def on_touch_up(self, touch: Any) -> bool:
        dx = touch.x - touch.ud.get("start_x", touch.x)
        dy = abs(touch.y - touch.ud.get("start_y", touch.y))
        if abs(dx) > dp(SWIPE_DISTANCE_THRESHOLD) and abs(dx) > dy:
            (self.next_month if dx < 0 else self.prev_month)(None)
            return True
        return super().on_touch_up(touch)
