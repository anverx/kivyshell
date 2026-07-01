"""Theme system for kivyshell.

Generalized from yaque's ui_constants: the spacing/dimension scale and the
CSS-like STYLES scaffold are generic and live here; the color/font/asset tokens
that differ per game are collected in a `Theme` dataclass that each app supplies.

    from kivyshell.uikit import theme
    theme.set_theme(Theme(button=(...), background_image="assets/bg.jpg", ...))
    styles = theme.get_styles()          # dp-scaled STYLES built from the active theme
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from kivy.metrics import dp

# --- generic dimension scale (raw numbers; dp() applied when styles are built) --
SPACING = {"min": 1, "xs": 2, "sm": 4, "md": 8, "lg": 10, "xl": 15, "xxl": 20}
RADIUS = {"sm": 8, "md": 12}
BUTTON_HEIGHT = {"sm": 40, "md": 48, "lg": 58}
ROW_HEIGHT = 36
CELL_HEIGHT = 52
STAT_ROW_HEIGHT = 24
ICON_BTN_SIZE = 40
ICON_LABEL_HEIGHT = 12
ICON_LABEL_TOTAL = 14  # icon label height + padding
POPUP_WIDTH = 0.85          # default popup size_hint_x
POPUP_WIDTH_NARROW = 0.78
SPINNER_LINE_WIDTH = 2
TOP_SPACER_HEIGHT = 70
PADDING_CELL = (2, 2)
SWIPE_DISTANCE_THRESHOLD = 100


@dataclass(frozen=True)
class Theme:
    """Per-app visual tokens. Defaults are a neutral palette; apps override."""

    # Fonts
    font_name: str = "Roboto"
    button_font_size: str = "22sp"

    # Text colors
    text_dark: tuple = (0.3, 0.3, 0.3, 1)
    text_medium: tuple = (0.5, 0.5, 0.5, 1)
    text_light: tuple = (0.4, 0.4, 0.4, 1)
    text_header: tuple = (0.2, 0.2, 0.2, 1)
    text_white: tuple = (1, 1, 1, 1)

    # Surfaces
    overlay: tuple = (1, 1, 1, 0.7)
    row_bg: tuple = (1, 1, 1, 0.7)
    row_pressed: tuple = (0.9, 0.9, 0.9, 1)
    panel_bg: tuple = (0, 0, 0, 0.3)
    popup_bg: tuple = (1, 1, 1, 0.95)
    input_bg: tuple = (0.95, 0.95, 0.95, 1)

    # Buttons
    button: tuple = (0.55, 0.78, 0.4, 1)
    button_down: tuple = (0.45, 0.68, 0.3, 1)
    button_gray: tuple = (0.75, 0.75, 0.75, 1)
    button_gray_down: tuple = (0.6, 0.6, 0.6, 1)
    button_unselected: tuple = (0.7, 0.7, 0.7, 1)

    # Feedback / links
    status_success: tuple = (0.2, 0.6, 0.2, 1)
    status_error: tuple = (0.8, 0.2, 0.2, 1)
    link: tuple = (0.2, 0.5, 0.8, 1)
    spinner_border: tuple = (0.8, 0.8, 0.8, 1)

    # Completion badges (calendar cells + menu). yaque = gold/silver crowns.
    badge_on_time: tuple = (1.0, 0.84, 0.0, 1)
    badge_late: tuple = (0.85, 0.88, 0.95, 1)
    badge_none: tuple = (0.5, 0.5, 0.5, 0.3)

    # Calendar day highlights
    calendar_today: tuple = (0.4, 0.7, 0.9, 1)
    calendar_protected: tuple = (0.85, 0.65, 0.3, 1)

    # Assets (paths, app-relative)
    background_image: str = ""
    icons_dir: str = ""    # directory of named icon PNGs used by IconButton
    loader_icon: str = ""  # was yaque's spinning queen.png
    badge_icon: str = ""   # was yaque's crown / queen-small.png

    disabled_opacity: float = 0.4

    def with_(self, **changes) -> "Theme":
        return replace(self, **changes)


DEFAULT_THEME = Theme()
_active: Theme = DEFAULT_THEME
_styles_cache: dict | None = None
_registered_styles: dict | None = None


def set_theme(theme: Theme) -> None:
    """Install the active theme and invalidate the built styles."""
    global _active, _styles_cache
    _active = theme
    _styles_cache = None


def get_theme() -> Theme:
    return _active


def register_styles(styles: dict) -> None:
    """Use an app-supplied STYLES dict verbatim instead of the built-in scaffold.

    Lets an existing app (yaque) hand its already-tuned, dp-scaled STYLES to the
    shared primitives so rendering is unchanged during migration. New apps can
    skip this and rely on build_styles(theme).
    """
    global _registered_styles
    _registered_styles = styles


def get_styles() -> dict:
    """Active STYLES: the registered dict if an app supplied one, else built
    (and cached) from the active theme."""
    global _styles_cache
    if _registered_styles is not None:
        return _registered_styles
    if _styles_cache is None:
        _styles_cache = build_styles(_active)
    return _styles_cache


def build_styles(theme: Theme) -> dict:
    """Build the full CSS-like STYLES dict from a theme (dp-scales size fields).

    Complete set used by the uikit widgets and shell screens, so an app only needs
    to supply a Theme (no register_styles). Dimensions are raw numbers here and
    dp-scaled at the end. Game-screen-specific styles are not included; a game that
    needs extra keys can add them via register_styles(get_styles() | {...}).
    """
    td, tl, tm, th, tw = theme.text_dark, theme.text_light, theme.text_medium, theme.text_header, theme.text_white
    styles = {
        "default": {"color": td},
        # Labels
        "title_lg": {"font_size": "24sp", "color": td, "size_hint_y": None, "height": 40},
        "title_md": {"font_size": "20sp", "color": td, "size_hint_y": None, "height": 40},
        "title": {"font_size": "18sp", "color": td, "size_hint_y": None, "height": 35},
        "title_sm": {"font_size": "16sp", "color": td, "size_hint_y": None, "height": 22},
        "subtitle": {"font_size": "14sp", "color": tl, "size_hint_y": None, "height": 25},
        "caption": {"font_size": "12sp", "color": tm},
        "clock": {"font_size": "36sp", "color": (0, 0, 0, 1)},
        "month": {"font_size": "22sp", "color": th},
        "day": {"font_size": "14sp"},
        "table_header": {"font_size": "11sp", "color": tw, "halign": "center"},
        "table_cell": {"font_size": "13sp", "color": td, "halign": "center"},
        "rating_cell": {"font_size": "13sp", "color": (1, 0.8, 0, 1), "halign": "center", "markup": True},
        "icon_label": {"font_size": "9sp", "color": tm},
        "status_label": {"font_size": "16sp", "halign": "center", "valign": "middle", "size_hint_y": None, "height": 45},
        # Rows / layouts
        "button_row": {"size_hint_y": None, "height": BUTTON_HEIGHT["md"], "spacing": SPACING["lg"]},
        "selection_row": {"size_hint_y": None, "height": BUTTON_HEIGHT["sm"], "spacing": SPACING["md"]},
        "popup_content": {"orientation": "vertical", "padding": [SPACING["xl"], SPACING["lg"]], "spacing": SPACING["lg"]},
        "top_spacer": {"size_hint_y": None, "height": TOP_SPACER_HEIGHT},
        "header_bar": {"size_hint_y": None, "height": 50, "spacing": SPACING["lg"]},
        "list_layout": {"orientation": "vertical", "size_hint_y": None, "spacing": SPACING["xs"], "padding": [0, 5]},
        "logbook_row": {"size_hint_y": None, "height": ROW_HEIGHT, "padding": [SPACING["lg"], SPACING["sm"]], "spacing": SPACING["md"]},
        "date_separator": {"size_hint_y": None, "height": 22, "padding": [SPACING["lg"], SPACING["sm"]]},
        "table_header_row": {"size_hint_y": None, "height": 20, "padding": [SPACING["lg"], 0], "spacing": SPACING["md"]},
        "status_area": {"size_hint_y": None, "height": 22},
        "timer_area": {"size_hint_y": None, "height": 18},
        "spacer_sm": {"size_hint_y": None, "height": 5},
        # Calendar
        "nav_btn": {"size_hint_x": None, "width": 50},
        "days_header": {"cols": 7, "size_hint_y": None, "height": 30, "spacing": SPACING["xs"]},
        "calendar_grid": {"cols": 7, "size_hint_y": None, "spacing": SPACING["sm"]},
        "cell": {"size_hint_y": None, "height": CELL_HEIGHT},
        # Buttons
        "selection_btn": {"font_size": "14sp"},
        "small_centered_btn": {"size_hint": (None, None), "width": 100, "height": BUTTON_HEIGHT["sm"], "pos_hint": {"center_x": 0.5}},
        "tall_btn": {"height": BUTTON_HEIGHT["lg"], "line_height": 0.6},
        "back_btn": {"font_size": "18sp"},
        "link_btn": {"font_size": "12sp", "size_hint_y": None, "height": 30, "background_color": (0, 0, 0, 0), "color": theme.link},
        # Inputs / popups
        "qr_image": {"size_hint_y": None, "height": 180},
        "url_input": {"font_size": "11sp", "size_hint_y": None, "height": BUTTON_HEIGHT["sm"],
                      "padding": [SPACING["md"], SPACING["lg"]], "readonly": True, "multiline": False,
                      "background_color": theme.input_bg, "foreground_color": td},
        "code_input": {"font_size": "16sp", "size_hint_y": None, "height": BUTTON_HEIGHT["md"],
                       "padding": [SPACING["lg"], SPACING["xl"]], "multiline": False,
                       "background_color": theme.input_bg, "foreground_color": th,
                       "cursor_color": td, "hint_text_color": (0.6, 0.6, 0.6, 1)},
    }
    for style in styles.values():
        for key in ("height", "width", "spacing"):
            if isinstance(style.get(key), (int, float)):
                style[key] = dp(style[key])
        if isinstance(style.get("padding"), (list, tuple)):
            style["padding"] = [dp(v) if isinstance(v, (int, float)) else v for v in style["padding"]]
    return styles
