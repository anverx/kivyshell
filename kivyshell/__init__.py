"""kivyshell — reusable Kivy UI primitives (uikit) + a daily-puzzle app shell.

Subpackages:
  kivyshell.uikit  — pure Kivy primitives and the Theme system (requires kivy)
  kivyshell.shell  — the app framework: adapters, storage, streak, screens

The shell's non-UI pieces (adapter contracts, SQLite storage, streak) are
importable without kivy; only uikit and the screens pull kivy in.
"""

__version__ = "0.1.0"
