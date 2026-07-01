"""L1: pure Kivy UI primitives + theme (requires kivy)."""

from .buttons import (
    BackButton,
    ColorTuple,
    CompletionBadge,
    CrownBadge,
    FixedGrayRoundedButton,
    FixedRoundedButton,
    GrayRoundedButton,
    IconButton,
    LinkButton,
    RoundedButton,
    SelectableButton,
    SelectableButtonGroup,
    SmallRoundedButton,
    TallRoundedButton,
    disable_widget,
)
from .inputs import CodeInput, UrlInput
from .layouts import (
    ButtonRow,
    CompletionIcon,
    CrownIcon,
    DateSeparator,
    PanelLayout,
    Popup,
    PopupContent,
    SizeButtonRow,
    StatRow,
    TypeIcon,
    styled_layout,
)
from .popups import LoadingPopup, load_code_popup, share_popup
from .spinner import LoaderSpinner, QueenSpinner
from .labels import (
    AboutSubtitleLabel,
    AboutTitleLabel,
    CaptionLabel,
    ClockLabel,
    DayLabel,
    IconLabel,
    MonthLabel,
    RatingLabel,
    StatusLabel,
    StyledLabel,
    SubtitleLabel,
    TableCellLabel,
    TableHeaderLabel,
    TitleLabel,
    TitleLgLabel,
    TitleMdLabel,
    TitleSmLabel,
    styled,
    styled_label,
)
from .theme import (
    DEFAULT_THEME,
    Theme,
    build_styles,
    get_styles,
    get_theme,
    register_styles,
    set_theme,
)

__all__ = [
    # theme
    "Theme", "DEFAULT_THEME", "set_theme", "get_theme", "get_styles", "build_styles", "register_styles",
    # buttons
    "ColorTuple", "RoundedButton", "GrayRoundedButton", "FixedRoundedButton", "TallRoundedButton",
    "FixedGrayRoundedButton", "SmallRoundedButton", "BackButton", "LinkButton",
    "CompletionBadge", "CrownBadge", "SelectableButton", "SelectableButtonGroup",
    "IconButton", "disable_widget",
    # layouts
    "PopupContent", "styled_layout", "ButtonRow", "SizeButtonRow", "PanelLayout", "StatRow",
    "DateSeparator", "Popup", "TypeIcon", "CompletionIcon", "CrownIcon",
    # inputs / spinner / popups
    "UrlInput", "CodeInput", "LoaderSpinner", "QueenSpinner",
    "LoadingPopup", "share_popup", "load_code_popup",
    # labels + factory
    "styled", "styled_label", "StyledLabel",
    "TitleLgLabel", "TitleMdLabel", "TitleLabel", "TitleSmLabel", "SubtitleLabel",
    "CaptionLabel", "MonthLabel", "DayLabel", "TableHeaderLabel", "TableCellLabel",
    "RatingLabel", "ClockLabel", "IconLabel", "AboutTitleLabel", "AboutSubtitleLabel", "StatusLabel",
]
