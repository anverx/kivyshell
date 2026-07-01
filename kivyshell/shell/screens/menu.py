"""Reusable main-menu screen.

Renders the standard daily-puzzle menu structure — a row of daily-variant
buttons (with completion badges), a Calendar button showing the streak, a set of
action buttons, and Exit — from a declarative MenuConfig. The app supplies the
variants, callbacks, streak text and completion state, so this screen holds no
game logic. yaque and yawop share the exact layout; only the config differs.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from kivy.uix.boxlayout import BoxLayout

from ...uikit import (
    BackButton,
    ButtonRow,
    CompletionBadge,
    FixedRoundedButton,
    RoundedButton,
    TallRoundedButton,
    TitleMdLabel,
    get_styles,
)
from ..adapter import Variant
from .base import BackgroundedScreen


@dataclass
class MenuConfig:
    daily_title: str
    daily_variants: list[Variant]
    on_daily: Callable[[Variant], None]
    calendar_label: str = "Calendar"
    on_calendar: Callable[[Any], None] | None = None
    streak_text: Callable[[], str] | None = None
    actions: list[tuple[str, Callable[[Any], None]]] = field(default_factory=list)
    exit_label: str = "Exit"
    on_exit: Callable[[Any], None] | None = None
    # variant_id -> completed? (drives the daily completion badges)
    daily_completion: Callable[[], dict[str, bool]] | None = None


class MenuScreen(BackgroundedScreen):
    """Subclass and implement menu_config()."""

    def menu_config(self) -> MenuConfig:
        raise NotImplementedError

    def build_content(self) -> None:
        cfg = self._config = self.menu_config()
        layout = self.content_layout

        layout.add_widget(BoxLayout(size_hint_y=0.2))
        layout.add_widget(TitleMdLabel(cfg.daily_title))

        daily_row = ButtonRow()
        self._badges: dict[str, CompletionBadge] = {}
        for variant in cfg.daily_variants:
            btn = RoundedButton(text=variant.label)
            btn.bind(on_press=lambda x, v=variant: cfg.on_daily(v))
            self._badges[variant.id] = CompletionBadge(btn)
            daily_row.add_widget(btn)
        layout.add_widget(daily_row)

        layout.add_widget(BoxLayout(size_hint_y=0.25))

        self._calendar_btn = None
        if cfg.on_calendar:
            self._calendar_btn = TallRoundedButton(text=cfg.calendar_label)
            self._calendar_btn.bind(on_press=cfg.on_calendar)
            layout.add_widget(self._calendar_btn)

        for label, callback in cfg.actions:
            btn = FixedRoundedButton(text=label)
            btn.bind(on_press=callback)
            layout.add_widget(btn)

        layout.add_widget(BoxLayout(size_hint_y=0.1))

        if cfg.on_exit:
            exit_btn = BackButton(text=cfg.exit_label)
            exit_btn.bind(on_press=cfg.on_exit)
            layout.add_widget(exit_btn)

    def on_enter(self) -> None:
        cfg = self._config
        if cfg.streak_text and self._calendar_btn is not None:
            caption_size = get_styles()["caption"]["font_size"]
            self._calendar_btn.text = f"{cfg.calendar_label}\n[size={caption_size}]{cfg.streak_text()}[/size]"
        if cfg.daily_completion:
            status = cfg.daily_completion()
            for vid, badge in self._badges.items():
                badge.show() if status.get(vid) else badge.hide()
