from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, List, Optional

from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.filters import Condition
from prompt_toolkit.formatted_text import to_formatted_text
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Float, FloatContainer, HSplit, Layout, VSplit, Window
from prompt_toolkit.layout.containers import ConditionalContainer
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Box, Button, Frame

from reidcli.provider.popular import POPULAR_PROVIDERS
from reidcli.ui.theme import BOX, DANGER, DIM, PRIMARY, SUCCESS, WARN

PICKER_BG = "#0d0d0d"
PICKER_CARD_BG = "#161616"
PICKER_BORDER = PRIMARY
PICKER_ACCENT = "#ff8787"
PICKER_HIGHLIGHT = f"bg:{PRIMARY} #0d0d0d bold"
PICKER_SELECTED = f"bg:#1f1f1f {PICKER_ACCENT}"
PICKER_SEARCH_BG = "#1a1a1a"
PICKER_SEARCH_FG = "#ffffff"
PICKER_FOOTER = "#666666"
PICKER_MUTED = "#444444"
PICKER_KIND_ANTHROPIC = PRIMARY
PICKER_KIND_OPENAI = "#00d4aa"
PICKER_KIND_COMPAT = "#ffd75f"
PICKER_KIND_OLLAMA = "#8b5cf6"
PICKER_KIND_CUSTOM = "#ff6b6b"

KIND_LABELS = {
    "anthropic": "ANTHROPIC",
    "openai": "OPENAI",
    "openai-compatible": "OPENAI-COMPAT",
    "ollama": "OLLAMA",
}
KIND_COLORS = {
    "anthropic": PICKER_KIND_ANTHROPIC,
    "openai": PICKER_KIND_OPENAI,
    "openai-compatible": PICKER_KIND_COMPAT,
    "ollama": PICKER_KIND_OLLAMA,
}
KIND_ICONS = {
    "anthropic": "◇",
    "openai": "◆",
    "openai-compatible": "◆",
    "ollama": "⬢",
}

PICKER_STYLE = Style.from_dict({
    "picker-bg": f"bg:{PICKER_BG} #e0e0e0",
    "picker-card": f"bg:{PICKER_CARD_BG} #e0e0e0",
    "picker-border": f"{PICKER_BORDER}",
    "picker-title": f"bold {PICKER_ACCENT}",
    "picker-subtitle": f"{PICKER_MUTED}",
    "picker-highlight": PICKER_HIGHLIGHT,
    "picker-selected": PICKER_SELECTED,
    "picker-search": f"bg:{PICKER_SEARCH_BG} {PICKER_SEARCH_FG}",
    "picker-search-prompt": f"bg:{PICKER_SEARCH_BG} {PICKER_ACCENT}",
    "picker-footer": PICKER_FOOTER,
    "picker-custom": f"bg:{PICKER_CARD_BG} {PICKER_KIND_CUSTOM}",
    "picker-custom-highlight": f"bg:{PRIMARY} #0d0d0d bold",
    "picker-kind": "bold",
    "picker-model": f"{PICKER_MUTED}",
    "picker-desc": "#aaaaaa",
    "picker-count": f"{PICKER_MUTED}",
    "picker-shortcut": f"{PICKER_ACCENT} bold",
    "completion-menu": f"bg:{PICKER_SEARCH_BG} {PICKER_SEARCH_FG}",
    "completion-menu.completion": f"bg:{PICKER_SEARCH_BG} #d0d0d0",
    "completion-menu.completion.current": PICKER_HIGHLIGHT,
    "completion-menu.meta.completion": f"bg:{PICKER_SEARCH_BG} #8a8a8a",
    "scrollbar.background": f"bg:{PICKER_MUTED}",
    "scrollbar.button": f"bg:{PRIMARY}",
    "scrollbar.arrow": f"bg:{PICKER_BG} {PRIMARY}",
})


@dataclass
class ProviderEntry:
    name: str
    kind: str
    base_url: str
    default_model: str
    description: str
    is_custom: bool = False


def _build_entries() -> List[ProviderEntry]:
    entries = []
    for name, kind, base_url, default_model, description in POPULAR_PROVIDERS:
        entries.append(ProviderEntry(
            name=name,
            kind=kind,
            base_url=base_url,
            default_model=default_model,
            description=description,
            is_custom=False,
        ))
    return entries


PROVIDER_ENTRIES = _build_entries()


class ProviderCompleter(Completer):
    def __init__(self, entries: List[ProviderEntry], get_query: Callable[[], str]) -> None:
        self.entries = entries
        self.get_query = get_query

    def get_completions(self, document, complete_event):
        query = self.get_query().lower().strip()
        if not query:
            return

        for entry in self.entries:
            if (query in entry.name.lower() or
                query in entry.kind.lower() or
                query in entry.description.lower() or
                query in entry.default_model.lower()):
                kind_label = KIND_LABELS.get(entry.kind, entry.kind)
                kind_color = KIND_COLORS.get(entry.kind, "#ffffff")
                icon = KIND_ICONS.get(entry.kind, "◆")
                display = [
                    ("class:picker-highlight", f"  {icon} {entry.name} "),
                    (f"{kind_color}", f"[{kind_label}] "),
                    ("class:picker-desc", entry.description),
                ]
                yield Completion(
                    entry.name,
                    start_position=0,
                    display=to_formatted_text(display),
                    display_meta=f"{entry.kind} · {entry.default_model}",
                )

        if query:
            yield Completion(
                "✦ Create custom provider",
                start_position=0,
                display=to_formatted_text([("class:picker-custom-highlight", "  ✦ Create custom provider")]),
                display_meta="Enter your own provider details",
            )


class CustomProviderForm:
    FIELDS = [
        ("name", "Provider Name", "my-provider", "Unique name (e.g., 'my-llama', 'company-gpt')"),
        ("kind", "Provider Kind", "openai-compatible", "anthropic | openai | openai-compatible | ollama"),
        ("base_url", "Base URL", "https://api.example.com/v1", "API endpoint (empty for defaults)"),
        ("api_key", "API Key", "", "Your API key (hidden)"),
        ("default_model", "Default Model", "model-name", "Default model (e.g., 'llama-3.1-70b')"),
    ]

    def __init__(self, on_submit: Callable[[dict], None], on_cancel: Callable[[], None]) -> None:
        self.on_submit = on_submit
        self.on_cancel = on_cancel
        self.current_field = 0
        self.buffers = {}
        self._build_ui()

    def _build_ui(self) -> None:
        for field_id, label, default, help_text in self.FIELDS:
            buf = Buffer()
            if default:
                buf.text = default
            self.buffers[field_id] = buf

        field_rows = []
        for i, (field_id, label, default, help_text) in enumerate(self.FIELDS):
            is_password = field_id == "api_key"

            def make_prompt(fid=field_id, lbl=label):
                is_sel = self.current_field == self.FIELDS.index((fid, lbl, default, help_text))
                prefix = "▸ " if is_sel else "  "
                style = "class:picker-title" if is_sel else "class:picker-footer"
                return [(style, f"{prefix}{lbl}: ")]

            prompt_control = FormattedTextControl(make_prompt)

            field_window = Window(
                content=BufferControl(buffer=self.buffers[field_id], focusable=True, password=is_password),
                height=1,
                style="class:picker-search",
            )

            def make_help(ht=help_text):
                return [( "class:picker-subtitle", f"    {ht}")]

            help_control = FormattedTextControl(make_help)
            help_window = Window(content=help_control, height=1, style="class:picker-bg")

            field_rows.append(HSplit([
                Window(content=prompt_control, height=1, style="class:picker-bg"),
                field_window,
                help_window,
            ]))

        submit_btn = Button(text="✓ Save", handler=self._submit)
        cancel_btn = Button(text="✕ Cancel", handler=self._cancel)

        button_row = VSplit([
            Window(width=2),
            submit_btn,
            Window(width=3),
            cancel_btn,
            Window(width=2),
        ], height=1)

        title_bar = Window(
            content=FormattedTextControl(lambda: [("class:picker-title", "  ✦ Create Custom Provider  ")]),
            height=1,
            style="class:picker-card",
        )

        self.container = Frame(
            body=HSplit([
                title_bar,
                Window(height=1, char="─", style="class:picker-border"),
                *field_rows,
                Window(height=1, style="class:picker-bg"),
                button_row,
            ]),
            style="class:picker-border",
        )

    def _submit(self) -> None:
        result = {fid: self.buffers[fid].text for fid, _, _, _ in self.FIELDS}
        self.on_submit(result)

    def _cancel(self) -> None:
        self.on_cancel()

    def __pt_container__(self):
        return self.container


class ProviderPicker:
    def __init__(self, on_select: Callable[[ProviderEntry], None], on_custom: Callable[[dict], None], on_cancel: Callable[[], None]) -> None:
        self.on_select = on_select
        self.on_custom = on_custom
        self.on_cancel = on_cancel

        self.entries = PROVIDER_ENTRIES
        self.filtered_entries = list(self.entries)
        self.selected_index = 0
        self.search_query = ""
        self.show_custom_form = False
        self.custom_form: Optional[CustomProviderForm] = None
        self._anim_start = time.time()

        self._build_ui()
        self._build_key_bindings()

    def _build_ui(self) -> None:
        self.search_buffer = Buffer()
        self.search_control = BufferControl(buffer=self.search_buffer, focusable=True, lexer=None)

        self.search_prompt = FormattedTextControl(
            lambda: [("class:picker-search-prompt", "  ⌕  Search providers...")]
        )

        search_row = VSplit([
            Window(content=self.search_prompt, width=22, style="class:picker-search"),
            Window(content=self.search_control, style="class:picker-search"),
        ], height=1)

        def get_list_fragments():
            fragments = []
            now = time.time()
            pulse = (now - self._anim_start) * 3

            for i, entry in enumerate(self.filtered_entries):
                is_selected = (i == self.selected_index)
                prefix = "▸ " if is_selected else "  "
                style = "class:picker-selected" if is_selected else "class:picker-card"

                kind_label = KIND_LABELS.get(entry.kind, entry.kind)
                kind_color = KIND_COLORS.get(entry.kind, "#ffffff")
                icon = KIND_ICONS.get(entry.kind, "◆")

                fragments.append((style, prefix))
                fragments.append((style, f"{icon} {entry.name} "))
                fragments.append((f"class:picker-kind {kind_color}", f"[{kind_label}] "))
                if entry.default_model:
                    fragments.append(("class:picker-model", f"{entry.default_model} "))
                fragments.append(("class:picker-desc", entry.description))
                if i < len(self.filtered_entries) - 1:
                    fragments.append(("", "\n"))
            return fragments

        self.list_control = FormattedTextControl(get_list_fragments, focusable=True)

        def get_custom_fragments():
            if not self.filtered_entries or self.selected_index >= len(self.filtered_entries):
                pulse = int((time.time() - self._anim_start) * 2) % 2
                marker = "✦" if pulse else "✧"
                return [("class:picker-custom", f"  {marker} Create custom provider  ")]
            return []

        self.custom_control = FormattedTextControl(get_custom_fragments, focusable=True)

        def get_count_fragments():
            total = len(self.entries)
            shown = len(self.filtered_entries)
            if self.search_query:
                return [("class:picker-count", f"  {shown}/{total} providers  ")]
            return [("class:picker-count", f"  {total} providers  ")]

        count_bar = Window(
            content=FormattedTextControl(get_count_fragments),
            height=1,
            align="right",
            style="class:picker-bg",
        )

        def get_footer_fragments():
            return [
                ("class:picker-shortcut", " ↑/↓ "),
                ("class:picker-footer", "navigate   "),
                ("class:picker-shortcut", "Enter "),
                ("class:picker-footer", "select   "),
                ("class:picker-shortcut", "Type "),
                ("class:picker-footer", "to filter   "),
                ("class:picker-shortcut", "Esc "),
                ("class:picker-footer", "cancel"),
            ]

        self.footer = FormattedTextControl(get_footer_fragments)

        title_bar = Window(
            content=FormattedTextControl(lambda: [("class:picker-title", "  ✦ Select LLM Provider  ")]),
            height=1,
            style="class:picker-card",
        )

        body = HSplit([
            title_bar,
            Window(height=1, char="─", style="class:picker-border"),
            search_row,
            Window(height=1, char="─", style="class:picker-border"),
            Window(content=self.list_control, style="class:picker-bg"),
            ConditionalContainer(
                content=Window(content=self.custom_control, height=1, style="class:picker-custom"),
                filter=Condition(lambda: True),
            ),
            Window(height=1, char="─", style="class:picker-border"),
            VSplit([
                Window(content=self.footer, style="class:picker-bg"),
                count_bar,
            ]),
        ])

        self.frame = Frame(body=body, style="class:picker-border")

        self.root_container = FloatContainer(
            content=self.frame,
            floats=[
                Float(
                    xcursor=True,
                    ycursor=True,
                    content=CompletionsMenu(max_height=12, scroll_offset=1, display_arrows=True),
                ),
            ],
        )

    def _build_key_bindings(self) -> None:
        self.kb = KeyBindings()

        @self.kb.add("up")
        def _up(event) -> None:
            if self.show_custom_form:
                return
            if self.selected_index > 0:
                self.selected_index -= 1
            event.app.invalidate()

        @self.kb.add("down")
        def _down(event) -> None:
            if self.show_custom_form:
                return
            max_idx = len(self.filtered_entries)
            if self.selected_index < max_idx:
                self.selected_index += 1
            event.app.invalidate()

        @self.kb.add("pageup")
        def _page_up(event) -> None:
            if self.show_custom_form:
                return
            self.selected_index = max(0, self.selected_index - 8)
            event.app.invalidate()

        @self.kb.add("pagedown")
        def _page_down(event) -> None:
            if self.show_custom_form:
                return
            self.selected_index = min(len(self.filtered_entries), self.selected_index + 8)
            event.app.invalidate()

        @self.kb.add("home")
        def _home(event) -> None:
            if self.show_custom_form:
                return
            self.selected_index = 0
            event.app.invalidate()

        @self.kb.add("end")
        def _end(event) -> None:
            if self.show_custom_form:
                return
            self.selected_index = len(self.filtered_entries)
            event.app.invalidate()

        @self.kb.add("enter")
        def _enter(event) -> None:
            if self.show_custom_form:
                return
            if self.selected_index >= len(self.filtered_entries):
                self._show_custom_form()
            elif self.filtered_entries:
                self.on_select(self.filtered_entries[self.selected_index])
            event.app.invalidate()

        @self.kb.add("escape")
        def _escape(event) -> None:
            if self.show_custom_form:
                self._hide_custom_form()
            else:
                self.on_cancel()

        @self.kb.add("c-c")
        def _ctrl_c(event) -> None:
            self.on_cancel()

        def on_search_change(buf: Buffer) -> None:
            self.search_query = buf.text
            self._filter_entries()
            self.selected_index = 0
            event.app.invalidate()

        self.search_buffer.on_text_changed += on_search_change

        @self.kb.add("tab")
        def _tab(event) -> None:
            if event.app.layout.current_window == self.frame.body.children[2].children[1].content:
                event.app.layout.focus(self.list_control)
            else:
                event.app.layout.focus(self.search_buffer)

        @self.kb.add("/")
        def _slash(event) -> None:
            if event.app.layout.current_window != self.search_buffer:
                event.app.layout.focus(self.search_buffer)

    def _filter_entries(self) -> None:
        query = self.search_query.lower().strip()
        if not query:
            self.filtered_entries = list(self.entries)
        else:
            self.filtered_entries = [
                e for e in self.entries
                if (query in e.name.lower() or
                    query in e.kind.lower() or
                    query in e.description.lower() or
                    query in e.default_model.lower())
            ]

    def _show_custom_form(self) -> None:
        self.show_custom_form = True

        def on_submit(values: dict) -> None:
            self.on_custom(values)
            self.show_custom_form = False
            self.custom_form = None
            event.app.invalidate()

        def on_cancel() -> None:
            self.show_custom_form = False
            self.custom_form = None
            event.app.invalidate()

        self.custom_form = CustomProviderForm(on_submit, on_cancel)
        self.frame.body = self.custom_form.container
        event.app.layout.focus(self.custom_form.buffers["name"])

    def _hide_custom_form(self) -> None:
        self.show_custom_form = False
        self.custom_form = None
        self._build_ui()
        event.app.layout.focus(self.search_buffer)

    def run(self) -> None:
        app = Application(
            layout=Layout(self.root_container, focused_element=self.search_buffer),
            key_bindings=self.kb,
            style=PICKER_STYLE,
            full_screen=True,
            mouse_support=True,
        )
        app.run()


def pick_provider(
    on_select: Callable[[ProviderEntry], None],
    on_custom: Callable[[dict], None],
    on_cancel: Callable[[], None],
) -> None:
    picker = ProviderPicker(on_select, on_custom, on_cancel)
    picker.run()