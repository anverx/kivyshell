"""Label widgets and the generic `styled` factory.

Ported from yaque's widgets/labels.py. The factory reads the active STYLES and
font from the theme (`kivyshell.uikit.theme`) rather than importing an app's
constants module, so it is game-agnostic.
"""

from __future__ import annotations

from typing import Any

from kivy.metrics import dp
from kivy.uix.label import Label

from .theme import get_styles, get_theme

__all__ = [
    "styled", "styled_label", "StyledLabel",
    "TitleLgLabel", "TitleMdLabel", "TitleLabel", "TitleSmLabel",
    "SubtitleLabel", "CaptionLabel", "MonthLabel", "DayLabel",
    "TableHeaderLabel", "TableCellLabel", "RatingLabel", "ClockLabel",
    "IconLabel", "AboutTitleLabel", "AboutSubtitleLabel", "StatusLabel",
]


def _convert_dp_props(props: dict[str, Any]) -> dict[str, Any]:
    """Convert dimension values in caller overrides to dp units."""
    result = props.copy()
    for key in ("height", "width", "spacing"):
        if key in result and isinstance(result[key], (int, float)):
            result[key] = dp(result[key])
    if "padding" in result:
        if isinstance(result["padding"], (list, tuple)):
            result["padding"] = [dp(v) if isinstance(v, (int, float)) else v for v in result["padding"]]
        elif isinstance(result["padding"], (int, float)):
            result["padding"] = dp(result["padding"])
    return result


def styled(widget_class: type, style: str, **overrides: Any) -> Any:
    """Instantiate a widget with a named style from the active STYLES.

    Style dimension values are expected already dp-converted; caller overrides
    are dp-converted here. Text widgets get the theme font by default.
    """
    props = get_styles().get(style, {}).copy()
    if hasattr(widget_class, "font_name"):
        props.setdefault("font_name", get_theme().font_name)
    props.update(_convert_dp_props(overrides))
    return widget_class(**props)


def styled_label(style: str = "default", text: str = "", **overrides: Any) -> Label:
    return styled(Label, style, text=text, **overrides)


def StyledLabel(**kwargs: Any) -> Label:
    return styled_label("default", **kwargs)


def TitleLgLabel(text: str, **kwargs: Any) -> Label:
    return styled_label("title_lg", text, **kwargs)


def TitleMdLabel(text: str, **kwargs: Any) -> Label:
    return styled_label("title_md", text, **kwargs)


def TitleLabel(text: str, **kwargs: Any) -> Label:
    return styled_label("title", text, **kwargs)


def TitleSmLabel(text: str, **kwargs: Any) -> Label:
    return styled_label("title_sm", text, **kwargs)


def SubtitleLabel(text: str, **kwargs: Any) -> Label:
    return styled_label("subtitle", text, **kwargs)


def CaptionLabel(text: str, **kwargs: Any) -> Label:
    return styled_label("caption", text, **kwargs)


def MonthLabel(text: str, **kwargs: Any) -> Label:
    return styled_label("month", text, **kwargs)


def DayLabel(text: str, **kwargs: Any) -> Label:
    return styled_label("day", text, **kwargs)


def TableHeaderLabel(text: str, **kwargs: Any) -> Label:
    return styled_label("table_header", text, **kwargs)


def TableCellLabel(text: str, **kwargs: Any) -> Label:
    return styled_label("table_cell", text, **kwargs)


def RatingLabel(text: str, **kwargs: Any) -> Label:
    return styled_label("rating_cell", text, **kwargs)


def ClockLabel(text: str = "00:00", **kwargs: Any) -> Label:
    return styled_label("clock", text, **kwargs)


def IconLabel(text: str, **kwargs: Any) -> Label:
    return styled_label("icon_label", text, **kwargs)


def AboutTitleLabel(text: str, **kwargs: Any) -> Label:
    return styled_label("title_lg", text, font_size="28sp", **kwargs)


def AboutSubtitleLabel(text: str, **kwargs: Any) -> Label:
    return styled_label("subtitle", text, font_size="16sp", **kwargs)


def StatusLabel(text: str, **kwargs: Any) -> Label:
    label = styled(Label, "status_label", text=text, **kwargs)
    label.bind(width=lambda inst, w: setattr(inst, "text_size", (w, None)))
    return label
