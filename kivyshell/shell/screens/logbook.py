"""Reusable tabbed logbook screen.

Provides the chrome — title, a tab switcher, an optional per-tab secondary control
row (e.g. a sort selector), a shared panel that swaps content, and a back button.
Each tab supplies its own content widget + refresh callback via LogbookTab, so all
the game/DB-specific rendering stays in the app. yaque and yawop share the tab
structure; only the tab content differs.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from ...uikit import (
    PanelLayout,
    SelectableButton,
    SelectableButtonGroup,
    TitleLgLabel,
    styled,
)
from ...uikit.theme import BUTTON_HEIGHT, PADDING_CELL, TOP_SPACER_HEIGHT, get_styles
from .base import BackgroundedScreen


@dataclass
class LogbookTab:
    key: str
    label: str
    build: Callable[[], Any]        # -> content Widget (built once)
    refresh: Callable[[], None]     # called when the tab is shown
    controls: Any = None            # optional secondary row widget (e.g. sort selector)


@dataclass
class LogbookConfig:
    title: str
    tabs: list[LogbookTab] = field(default_factory=list)


class LogbookScreen(BackgroundedScreen):
    """Subclass and implement logbook_config()."""

    def logbook_config(self) -> LogbookConfig:
        raise NotImplementedError

    def build_content(self) -> None:
        cfg = self._config = self.logbook_config()
        self._tabs = {t.key: t for t in cfg.tabs}
        self._built: dict[str, Any] = {}
        self._current: str | None = None
        layout = self.content_layout

        layout.add_widget(BoxLayout(size_hint_y=None, height=dp(TOP_SPACER_HEIGHT)))
        layout.add_widget(TitleLgLabel(cfg.title))

        tab_row = styled(BoxLayout, "selection_row")
        self._tab_group = SelectableButtonGroup(on_select=self._switch_tab)
        for i, tab in enumerate(cfg.tabs):
            btn = SelectableButton(text=tab.label, selected=(i == 0), **get_styles()["selection_btn"])
            self._tab_group.add(tab.key, btn)
            tab_row.add_widget(btn)
        tab_row.add_widget(Label(size_hint_x=1))
        layout.add_widget(tab_row)

        # Slot for the active tab's optional control row (e.g. sort).
        self._controls_slot = BoxLayout(orientation="vertical", size_hint_y=None, height=0)
        layout.add_widget(self._controls_slot)

        self.panel = PanelLayout(orientation="vertical",
                                 padding=[dp(PADDING_CELL[0]), dp(PADDING_CELL[1])])
        layout.add_widget(self.panel)
        self.add_back_button()

        if cfg.tabs:
            self._display_tab(cfg.tabs[0].key)  # show first tab; refresh deferred to on_enter

    def _display_tab(self, key: str) -> None:
        """Show a tab's content + controls without refreshing (no data access)."""
        self._current = key
        tab = self._tabs[key]
        if key not in self._built:
            self._built[key] = tab.build()
        self.panel.clear_widgets()
        self.panel.add_widget(self._built[key])

        self._controls_slot.clear_widgets()
        if tab.controls is not None:
            self._controls_slot.add_widget(tab.controls)
            self._controls_slot.height = getattr(tab.controls, "height", dp(BUTTON_HEIGHT["sm"]))
            self._controls_slot.opacity = 1
        else:
            self._controls_slot.height = 0
            self._controls_slot.opacity = 0

    def _switch_tab(self, key: str) -> None:
        self._display_tab(key)
        self._tabs[key].refresh()

    def on_enter(self) -> None:
        if self._current is not None:
            self._tabs[self._current].refresh()
