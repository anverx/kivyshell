# kivyshell

Reusable building blocks for cross-platform Kivy daily-puzzle games — extracted
from [yaque](https://github.com/anverx/yaque) so that yaque and
[yawop](https://github.com/anverx/yawop) share one implementation of everything
that isn't the game itself.

> **Status: scaffold.** The foundation (theme, adapter contracts, generic
> storage, streak) is in place and tested. The UI primitives and reusable screens
> are being migrated out of yaque in phases — see
> [`docs/EXTRACTION_PLAN.md`](docs/EXTRACTION_PLAN.md).

## Two layers

```
kivyshell/
  uikit/   L1 — pure Kivy primitives + Theme      (requires kivy)
    theme.py         Theme dataclass + STYLES scaffold + dp scaling   ✅
    buttons/labels/layouts/inputs/popups/spinner/charts/screen        ⏳ (migrating)
  shell/   L2 — the daily-puzzle app framework
    adapter.py       GameAdapter + StorageAdapter contracts           ✅
    storage.py       generic SQLite StorageAdapter                    ✅
    streak.py        pure daily-streak logic                          ✅
    app.py           GameShellApp base (ScreenManager + navigation)   ⏳
    screens/         menu / calendar / logbook / splash               ⏳
```

The **shell's non-UI pieces import without kivy** (pure Python), so storage /
streak / contracts are unit-tested hermetically; only `uikit` and the screens
pull kivy in.

## The idea

A game plugs in by implementing one interface — **`GameAdapter`** — and picking a
**`StorageAdapter`** (a generic SQLite one ships here). The shell then provides the
menu, calendar, activity/logbook, streaks, daily/random flow, and sharing. The
**only genuinely game-specific piece is the game panel** (`GameAdapter.build_panel`):
yaque's queens board, yawop's word grid.

Everything keys on `(variant_id, date)` + an opaque `code` and a `meta` blob, so
the library never needs to understand a specific game.

```python
from kivyshell.shell import GameAdapter, Variant, SqliteStore

class WordGame(GameAdapter):
    title, subtitle = "yawop", "Yet Another WOrd Puzzle"
    def variants(self):     return [Variant("subtlex-us:easy", "Easy"), ...]
    def make_game(self, v, *, seed=None, date=None): ...   # worddata.pick_word(...)
    def build_panel(self, game, *, on_win): ...            # the word grid  ← only unique part
    def encode(self, g): ...
    def decode(self, c): ...
```

## Install

```sh
pip install -e .            # editable, for development (pulls kivy)
# consumers pin it as a git dependency until published to PyPI
```

## Tests

```sh
python -m unittest discover -s tests -v
```
