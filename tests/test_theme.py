"""Tests for the Theme system (requires kivy for kivy.metrics.dp)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from kivy.metrics import dp  # noqa: F401
    HAVE_KIVY = True
except Exception:
    HAVE_KIVY = False


@unittest.skipUnless(HAVE_KIVY, "kivy not installed")
class TestTheme(unittest.TestCase):
    def setUp(self):
        # Reset module-global theme state (other tests call register_styles/set_theme).
        from kivyshell.uikit import theme as t
        t._registered_styles = None
        t._styles_cache = None
        t.set_theme(t.DEFAULT_THEME)

    def test_override_and_activate(self):
        from kivyshell.uikit import Theme, get_theme, set_theme
        t = Theme(button=(1, 0, 0, 1), background_image="bg.jpg")
        set_theme(t)
        self.assertEqual(get_theme().button, (1, 0, 0, 1))
        self.assertEqual(get_theme().background_image, "bg.jpg")

    def test_with_returns_modified_copy(self):
        from kivyshell.uikit import DEFAULT_THEME
        t2 = DEFAULT_THEME.with_(font_name="DMSans")
        self.assertEqual(t2.font_name, "DMSans")
        self.assertNotEqual(DEFAULT_THEME.font_name, "DMSans")

    def test_build_styles_dp_scales_dimensions(self):
        from kivy.metrics import dp
        from kivyshell.uikit import DEFAULT_THEME, build_styles
        styles = build_styles(DEFAULT_THEME)
        # 'title' height is raw 35 in source -> dp(35) after build
        self.assertAlmostEqual(styles["title"]["height"], dp(35))
        self.assertEqual(styles["title"]["color"], DEFAULT_THEME.text_dark)

    def test_build_styles_covers_shell_screen_keys(self):
        from kivyshell.uikit import DEFAULT_THEME, build_styles
        keys = set(build_styles(DEFAULT_THEME))
        required = {
            "default", "title", "title_lg", "title_md", "title_sm", "subtitle", "caption",
            "clock", "month", "day", "table_header", "table_cell", "rating_cell", "icon_label",
            "status_label", "button_row", "selection_row", "popup_content", "top_spacer",
            "header_bar", "list_layout", "logbook_row", "date_separator", "table_header_row",
            "status_area", "timer_area", "spacer_sm", "nav_btn", "days_header", "calendar_grid",
            "cell", "selection_btn", "small_centered_btn", "tall_btn", "back_btn", "link_btn",
            "qr_image", "url_input", "code_input",
        }
        self.assertTrue(required <= keys, f"build_styles missing shell keys: {sorted(required - keys)}")

    def test_styles_cache_invalidated_on_set_theme(self):
        from kivyshell.uikit import Theme, get_styles, set_theme
        set_theme(Theme())
        first = get_styles()
        set_theme(Theme())
        self.assertIsNot(first, get_styles())


if __name__ == "__main__":
    unittest.main()
