"""L2: the daily-puzzle app framework (adapters, storage, streak, screens).

The pieces re-exported here are pure-Python (no kivy); the reusable screens and
the App base class (added during the extraction phases) live in submodules that
pull kivy in.
"""

from .adapter import (
    Completion,
    GameAdapter,
    MonthStatus,
    PlayRecord,
    StorageAdapter,
    Variant,
)
from .storage import SqliteStore
from .streak import compute_streak, format_streak_text

__all__ = [
    "GameAdapter", "StorageAdapter", "Variant", "Completion", "PlayRecord", "MonthStatus",
    "SqliteStore", "compute_streak", "format_streak_text",
]
