"""The contracts that make the shell game-agnostic.

A game plugs into the shell by implementing `GameAdapter` (its game logic + the
one truly different piece, the game panel widget) and choosing a `StorageAdapter`
(a generic SQLite one ships in `kivyshell.shell.storage`).

Design notes (from analyzing yaque):
- The shell keys everything on (variant_id, date) + an opaque `code` string; any
  game-specific fields (board size, num_solutions, difficulty, the answer word)
  ride along in an opaque `meta` dict the shell never inspects.
- yaque variants are board sizes 6/7/8; yawop variants are packs/difficulties.
- yaque needs slow async generation (LoadingPopup + cancel); yawop's make_game is
  instant — so async generation is optional and defaults to synchronous.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Protocol, runtime_checkable


class Completion(Enum):
    """Generic completion state for a (variant, date). Apps map to their own
    labels/colors (yaque: NONE=gray, ON_TIME=gold crown, LATE=silver crown)."""
    NONE = "none"
    ON_TIME = "on_time"   # solved on the puzzle's own date
    LATE = "late"         # solved on a later date


@dataclass(frozen=True)
class Variant:
    """A selectable puzzle variant shown on the menu / calendar (e.g. a board
    size, or a word pack+difficulty)."""
    id: str
    label: str
    meta: dict = field(default_factory=dict)


@dataclass
class PlayRecord:
    """One logbook/history entry (game-agnostic view of a play)."""
    variant_id: str
    date: str | None            # ISO date for daily puzzles, None for random
    code: str
    started_at: str
    completed_at: str | None
    duration_ms: int | None
    completed: bool
    rating: int | None = None


@dataclass
class MonthStatus:
    """Everything the CalendarScreen needs for one month, game-agnostically."""
    month_name: str
    streak_text: str
    days: dict[str, dict[str, Completion]]   # date_iso -> {variant_id -> Completion}
    month_badge: Completion
    protected_dates: set[str] = field(default_factory=set)


@runtime_checkable
class GameAdapter(Protocol):
    """Implemented by each game. The game panel is the only piece that truly
    differs between games; everything else is menu/calendar/logbook scaffolding."""

    title: str
    subtitle: str

    def theme(self) -> Any: ...                                  # kivyshell.uikit.theme.Theme
    def variants(self) -> list[Variant]: ...

    def make_game(self, variant: Variant, *, seed: Any = None, date: str | None = None) -> Any:
        """Create an opaque game/state object for a variant."""

    def build_panel(self, game: Any, *, on_win: Callable[[int], None]) -> Any:
        """Return the Kivy Widget that plays `game`; call on_win(duration_ms) when solved."""

    def encode(self, game: Any) -> str: ...
    def decode(self, code: str) -> Any: ...

    # --- optional: slow generation with progress/cancel (yaque). Default: sync make_game. ---
    def generate(self, variant: Variant, *,
                 on_progress: Callable[[str, str], None] | None = None) -> Any:
        return self.make_game(variant)

    # Colors/labels for the three Completion states (badges/crowns).
    def completion_style(self, status: Completion) -> dict: ...


@runtime_checkable
class StorageAdapter(Protocol):
    """Persists challenges + plays generically. A SQLite default ships with the shell."""

    def open(self, data_dir: str) -> None: ...
    def close(self) -> None: ...

    def record_challenge(self, variant_id: str, date: str | None, code: str,
                         meta: dict | None = None) -> int: ...
    def start_play(self, challenge_id: int) -> int: ...
    def complete_play(self, play_id: int, duration_ms: int) -> None: ...
    def rate_play(self, play_id: int, rating: int) -> None: ...

    def completion_today(self, date: str, variant_ids: list[str]) -> dict[str, Completion]: ...
    def month_status(self, year: int, month: int, variant_ids: list[str]) -> MonthStatus: ...
    def all_plays(self, limit: int = 50, offset: int = 0, sort_by: str = "time") -> list[PlayRecord]: ...
    def stats(self) -> dict: ...
    def streak(self, ref_date: str | None = None) -> int: ...
