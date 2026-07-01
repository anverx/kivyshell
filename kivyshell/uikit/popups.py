"""Generic dialog primitives: a loading popup, a share dialog, a code-load dialog.

Ported from yaque's popups.py — the game-agnostic dialogs. The game-specific
selectors (board size / strategy / solutions) stay in the app. Callbacks keep the
game logic out of here: `load_code_popup` takes an `on_submit(text) -> error|None`.
"""

from __future__ import annotations

import io
from collections.abc import Callable
from typing import Any

from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.image import Image as CoreImage
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView

from .buttons import FixedGrayRoundedButton, GrayRoundedButton, RoundedButton
from .inputs import CodeInput, UrlInput
from .labels import CaptionLabel, StatusLabel, SubtitleLabel, TitleLabel, styled
from .layouts import ButtonRow, Popup, PopupContent
from .spinner import LoaderSpinner
from .theme import POPUP_WIDTH_NARROW, SPACING, get_styles, get_theme

__all__ = ["LoadingPopup", "share_popup", "load_code_popup"]


class LoadingPopup(ModalView):
    """A loading popup with a spinning themed icon, elapsed timer, and cancel."""

    def __init__(self, on_cancel: Callable[[], None] | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.size_hint = (POPUP_WIDTH_NARROW, 0.45)
        self.auto_dismiss = False
        self.background_color = get_theme().popup_bg
        self.on_cancel_callback = on_cancel
        self.elapsed_time: float = 0.0
        self._animation_event: Any = None
        self._timer_event: Any = None

        layout = PopupContent(padding=[dp(SPACING["xxl"]), dp(SPACING["xl"])])

        status_group = BoxLayout(orientation="vertical", size_hint_y=None, spacing=0)
        status_group.bind(minimum_height=status_group.setter("height"))
        self.status_label = StatusLabel("Loading...")
        self.status_label.bind(texture_size=lambda inst, sz: setattr(inst, "height", sz[1]))
        status_group.add_widget(self.status_label)
        self.subtitle_label = CaptionLabel("", size_hint_y=None)
        self.subtitle_label.halign = "center"
        self.subtitle_label.bind(texture_size=lambda inst, sz: setattr(inst, "height", sz[1]))
        status_group.add_widget(self.subtitle_label)
        layout.add_widget(status_group)

        self.spinner = LoaderSpinner(size_hint=(1, 1))
        layout.add_widget(self.spinner)

        self.timer_label = CaptionLabel("0:00", **get_styles()["timer_area"])
        layout.add_widget(self.timer_label)

        cancel_btn = GrayRoundedButton(text="Cancel", **get_styles()["small_centered_btn"])
        cancel_btn.bind(on_press=self._on_cancel)
        layout.add_widget(cancel_btn)

        self.add_widget(layout)

    def _animate(self, dt: float) -> None:
        self.spinner.rotate()

    def _update_timer(self, dt: float) -> None:
        self.elapsed_time += dt
        m, s = int(self.elapsed_time) // 60, int(self.elapsed_time) % 60
        self.timer_label.text = f"{m}:{s:02d}"

    def set_status(self, text: str, subtitle: str = "") -> None:
        self.status_label.text = text
        self.subtitle_label.text = subtitle

    def open(self, *args: Any, **kwargs: Any) -> None:
        super().open(*args, **kwargs)
        self.spinner.reset()
        self.elapsed_time = 0.0
        self.timer_label.text = "0:00"
        self._animation_event = Clock.schedule_interval(self._animate, 1 / 60)
        self._timer_event = Clock.schedule_interval(self._update_timer, 1)

    def dismiss(self, *args: Any, **kwargs: Any) -> None:
        for ev in ("_animation_event", "_timer_event"):
            if getattr(self, ev):
                getattr(self, ev).cancel()
                setattr(self, ev, None)
        super().dismiss(*args, **kwargs)

    def _on_cancel(self, instance: Any) -> None:
        if self.on_cancel_callback:
            self.on_cancel_callback()
        self.dismiss()


def share_popup(share_url: str, code: str, title: str = "Share") -> None:
    """QR code + copy-URL / copy-code dialog for any shareable URL + code.

    Requires the optional `qrcode` extra: pip install 'kivyshell[qr]'.
    """
    try:
        import qrcode
    except ImportError as exc:
        raise RuntimeError("share_popup requires qrcode; install with: pip install 'kivyshell[qr]'") from exc

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=2)
    qr.add_data(share_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    qr_img.save(buf, format="PNG")
    buf.seek(0)
    core_img = CoreImage(buf, ext="png")

    content = PopupContent()
    content.add_widget(TitleLabel(title))
    content.add_widget(styled(Image, "qr_image", texture=core_img.texture))
    content.add_widget(UrlInput(share_url))

    status_label = CaptionLabel("", color=get_theme().status_success, **get_styles()["status_area"])
    content.add_widget(status_label)

    def _copy(value: str, msg: str) -> Callable[[Any], None]:
        def handler(btn: Any) -> None:
            Clipboard.copy(value)
            status_label.text = msg
            Clock.schedule_once(lambda dt: setattr(status_label, "text", ""), 2)
        return handler

    buttons = ButtonRow()
    url_btn = RoundedButton(text="Copy URL")
    url_btn.bind(on_press=_copy(share_url, "URL copied!"))
    buttons.add_widget(url_btn)
    code_btn = RoundedButton(text="Copy Code")
    code_btn.bind(on_press=_copy(code, "Code copied!"))
    buttons.add_widget(code_btn)
    content.add_widget(buttons)

    close_btn = FixedGrayRoundedButton(text="Close")
    content.add_widget(close_btn)

    popup = Popup(content, height=450)
    close_btn.bind(on_press=popup.dismiss)
    popup.open()


def load_code_popup(on_submit: Callable[[str], str | None], *, title: str = "Load",
                    subtitle: str = "Paste code or URL:", height: float = 300) -> None:
    """Paste-a-code dialog. `on_submit(text)` returns an error message to show,
    or None on success (the popup then closes). Game-specific parsing lives in
    the callback, keeping this dialog generic."""
    content = PopupContent()
    content.add_widget(TitleLabel(title))
    content.add_widget(SubtitleLabel(subtitle))
    text_input = CodeInput()
    content.add_widget(text_input)
    error_label = CaptionLabel("", color=get_theme().status_error, **get_styles()["status_area"])
    content.add_widget(error_label)

    popup = None

    def load(btn: Any) -> None:
        text = text_input.text.strip()
        if not text:
            error_label.text = "Please enter a code or URL"
            return
        error = on_submit(text)
        if error:
            error_label.text = error
        else:
            popup.dismiss()

    def paste(btn: Any) -> None:
        text_input.text = Clipboard.paste() or ""

    buttons = ButtonRow()
    paste_btn = GrayRoundedButton(text="Paste")
    paste_btn.bind(on_press=paste)
    buttons.add_widget(paste_btn)
    load_btn = RoundedButton(text="Load")
    load_btn.bind(on_press=load)
    buttons.add_widget(load_btn)
    content.add_widget(buttons)

    cancel_btn = FixedGrayRoundedButton(text="Cancel")
    content.add_widget(cancel_btn)

    popup = Popup(content, height=height, auto_dismiss=False)
    cancel_btn.bind(on_press=popup.dismiss)
    popup.open()
