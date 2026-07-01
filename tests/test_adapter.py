"""Tests that the adapter contracts are satisfiable (no kivy)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kivyshell.shell import Completion, GameAdapter, StorageAdapter, SqliteStore, Variant  # noqa: E402


class FakeGame(GameAdapter):
    title = "Fake"
    subtitle = "test game"

    def theme(self):
        return None

    def variants(self):
        return [Variant("easy", "Easy"), Variant("hard", "Hard")]

    def make_game(self, variant, *, seed=None, date=None):
        return {"variant": variant.id, "answer": "ABIDE"}

    def build_panel(self, game, *, on_win):
        return object()  # a fake widget

    def encode(self, game):
        return game["answer"]

    def decode(self, code):
        return {"answer": code}

    def completion_style(self, status):
        return {"color": (1, 1, 1, 1)}


class TestContracts(unittest.TestCase):
    def test_fake_game_satisfies_protocol(self):
        self.assertIsInstance(FakeGame(), GameAdapter)

    def test_variants_and_roundtrip(self):
        g = FakeGame()
        self.assertEqual([v.id for v in g.variants()], ["easy", "hard"])
        game = g.make_game(g.variants()[0])
        self.assertEqual(g.decode(g.encode(game))["answer"], "ABIDE")

    def test_sqlite_store_satisfies_storage_protocol(self):
        self.assertIsInstance(SqliteStore(), StorageAdapter)

    def test_completion_enum(self):
        self.assertEqual({c.value for c in Completion}, {"none", "on_time", "late"})


if __name__ == "__main__":
    unittest.main()
