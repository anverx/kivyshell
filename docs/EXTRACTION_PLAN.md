# kivyshell extraction plan

Extract the reusable parts of **yaque** into an independent library that both
yaque and **yawop** consume. Only the *game panel* differs between the two; the
menu, calendar, activity/logbook, streaks, daily/random flow, storage, and theming
are shared.

## Goal architecture

```
 yaque game            yawop game            ← GameAdapter impl + game panel + theme
 (queens board,        (word grid,
  solver, encoding)     dictionaries)
        └──────────────┬──────────────┘  implements GameAdapter
                       ▼
 L2  kivyshell.shell — App base (ScreenManager+nav), Menu/Calendar/Logbook/Splash,
     daily/random/share/load flows, driven by GameAdapter + StorageAdapter
                       ▼
 L1  kivyshell.uikit — pure Kivy primitives + Theme (knows nothing about games)
```

## What goes where (from analyzing yaque `src/`)

Three tiers currently live together in `src/widgets/`:

| Tier | Items | Destination |
|------|-------|-------------|
| Pure primitives | `RoundedButton` family, all `*Label`, `styled*`, `Popup/PopupContent`, `ButtonRow/PanelLayout`, `UrlInput/CodeInput`, `BarChart`, `disable_widget`, `BackgroundedScreen` | **L1 `uikit`** |
| App-shell components | `DayCell`, `LogbookRow`, `StatRow`, `DateSeparator`, badge/crown, `SizeButtonRow`, menu/calendar/logbook/splash screens, App skeleton | **L2 `shell`** (parameterized) |
| Game-specific | `BoardWidget`, `SolutionIndicator`, `QueenSpinner`, `game*.py`, `solver_pkg`, game-specific popups | **stays in the game** |

## Contracts (pinned; implemented in `shell/adapter.py`)

Everything keys on **`(variant_id, date)` + opaque `code` + `meta` blob** — the
library never parses game state.

- **`GameAdapter`** (each game): `title/subtitle`, `theme()`, `variants()`,
  `make_game(variant, seed, date)`, **`build_panel(game, on_win)` ← the only truly
  unique piece**, `encode/decode`, optional `generate(on_progress)` for slow
  generation (yaque; yawop is instant), `completion_style(status)`.
- **`StorageAdapter`** (generic SQLite default in `shell/storage.py`):
  `record_challenge`, `start/complete/rate_play`, `completion_today`,
  `month_status`, `all_plays`, `stats`, `streak`.

### Storage generalization (from yaque's `database.py`)

yaque's `puzzles(size, seed, num_solutions, kingdom_strategy, difficulty_score,
board_state…)` collapses to `challenges(variant_id, date, code, meta_json)` — the
game-specific columns become the opaque `meta` blob. The `plays` table
(`started_at/completed_at/duration_ms/completed/rating`) is already generic and
carries over unchanged. `calendar_logic` (streak, month status) is pure and ports
directly; the GOLD/SILVER "same-day vs later" rule becomes the generic
`Completion.ON_TIME / LATE / NONE`, with apps supplying colors via
`completion_style`.

## Coupling to fix (during the yaque refactor)

| Leak today | Fix |
|---|---|
| `widgets/layouts.py` → `calendar_logic.CompletionStatus` | Move `DayCell`/coloring to L2; take generic `Completion` + `completion_style` from the adapter |
| `widgets/board.py` → `game` | Game-specific — leave in the game |
| `QueenSpinner`, queen icons, `QUEEN_GOLD` in `buttons.py`/`spinner.py` | Generalize to `Spinner(icon=…)` / `IconButton(icon=…)`; icons/colors come from `Theme` |
| `ui_constants` mixes generic scaffold + queen/kingdom/board tokens | Split: L1 ships the `STYLES` scaffold + spacing/dp machinery + `Theme`; the queen/board tokens become yaque's `Theme` values |
| screens `import database/game/calendar_logic` directly | Inject via `GameAdapter`/`StorageAdapter` instead of module-level imports |
| flat `from ui_constants import X` | package imports + active `Theme` |

## Migration phases (refactor yaque in place first — keep it runnable throughout)

0. **Decouple in place (yaque only):** introduce `Theme`, remove the leaks above,
   extract a `GameAdapter`/`StorageAdapter` boundary in `app.py`/screens. Verify
   yaque launches + solver tests pass.
1. **Lift L1 → `kivyshell.uikit`**, yaque imports from it. ← *scaffolded here (theme done; widgets next)*
2. **Lift L2 → `kivyshell.shell`** (screens + App base + storage). yaque becomes:
   adapter impl + game core + its `Theme`. Verify.
3. **yawop implements the adapter** (word-grid `build_panel`, `make_game` via
   `worddata.pick_word`, packs/difficulties as `Variant`s, its `Theme`) and gets
   menu/calendar/activity/random for free.

## Verification

yaque's tests cover solver/logic, not UI, so phases 0–2 lean on "launches cleanly"
+ logic tests. This library adds hermetic tests for the pieces that *can* be tested
without a GL context (storage, streak, contracts, theme dp-scaling), which already
run in CI across Python 3.11–3.13. Widget/screen smoke tests (build against a fake
adapter under a mock window) are added as the UI migrates.

## Open items

- Port yaque's streak **protection** milestones (banked at 10/30 consecutive days)
  into `shell/streak.py` (core consecutive-day logic already ported).
- Decide the game-screen chrome that's optional per game (timer, solution cycling,
  share) — expose as feature flags on the shell `GameScreen`.
- Publish to PyPI vs. consume as a pinned git dependency (git for now).
