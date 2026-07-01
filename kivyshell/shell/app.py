"""Base Kivy App for daily-puzzle games.

Owns the standard scaffolding: ScreenManager wiring, the splash-then-menu startup,
navigation helpers, and the storage open/close lifecycle. Subclass and implement:

  - create_screens() -> list of screens to register (must include ones named
    'splash' and 'menu'; typically also 'calendar', 'game', 'logbook')
  - open_storage() / close_storage()  (e.g. init/close the SQLite store)
  - on_build()  (optional: extra setup after screens are registered)

Game-specific actions (starting/generating a game, sharing, about) live in the
subclass. Not imported by kivyshell.shell.__init__, so the shell's pure pieces
stay kivy-free.
"""

from __future__ import annotations

from typing import Any

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import FadeTransition, ScreenManager


class GameShellApp(App):
    splash_delay = 1.5  # seconds on the splash screen before switching to the menu

    def open_storage(self) -> None:
        """Override to initialize persistent storage."""

    def close_storage(self) -> None:
        """Override to close persistent storage."""

    def create_screens(self) -> list:
        """Return the screens to register (include 'splash' and 'menu')."""
        raise NotImplementedError

    def on_build(self) -> None:
        """Override for extra setup after screens are registered."""

    def build(self) -> ScreenManager:
        self.open_storage()
        self.sm = ScreenManager(transition=FadeTransition())
        for screen in self.create_screens():
            self.sm.add_widget(screen)
        self.sm.current = "splash"
        Clock.schedule_once(self._go_to_menu, self.splash_delay)
        self.on_build()
        return self.sm

    # --- navigation ---
    def _go_to_menu(self, dt: float | None = None) -> None:
        self.sm.current = "menu"

    def show_menu(self, instance: Any = None) -> None:
        self.sm.current = "menu"

    def show_calendar(self, instance: Any = None) -> None:
        self.sm.current = "calendar"

    def show_logbook(self, instance: Any = None) -> None:
        self.sm.current = "logbook"

    def exit_app(self, instance: Any = None) -> None:
        App.get_running_app().stop()

    def on_stop(self) -> None:
        self.close_storage()
