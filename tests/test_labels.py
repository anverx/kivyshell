"""Tests for the styled() factory + labels (requires kivy; run under xvfb in CI)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import kivy  # noqa: F401
    HAVE_KIVY = True
except Exception:
    HAVE_KIVY = False


@unittest.skipUnless(HAVE_KIVY, "kivy not installed")
class TestLabels(unittest.TestCase):
    def setUp(self):
        from kivyshell.uikit import Theme, register_styles, set_theme
        set_theme(Theme(font_name="Roboto"))
        register_styles({
            "default": {"color": (0, 0, 0, 1)},
            "caption": {"font_size": "12sp", "color": (0.5, 0.5, 0.5, 1)},
        })

    def test_registered_styles_take_precedence(self):
        from kivyshell.uikit import get_styles
        self.assertIn("caption", get_styles())
        self.assertEqual(get_styles()["caption"]["color"], (0.5, 0.5, 0.5, 1))

    def test_styled_label_applies_style_and_theme_font(self):
        from kivyshell.uikit import CaptionLabel
        lbl = CaptionLabel("hello")
        self.assertEqual(lbl.text, "hello")
        self.assertEqual(lbl.font_name, "Roboto")

    def test_styled_factory_overrides(self):
        from kivy.uix.label import Label
        from kivyshell.uikit import styled
        lbl = styled(Label, "default", text="x", color=(1, 0, 0, 1))
        self.assertEqual(lbl.color, [1, 0, 0, 1])


if __name__ == "__main__":
    unittest.main()
