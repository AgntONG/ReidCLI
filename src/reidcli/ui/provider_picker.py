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
from prompt_toolkit.layout import Float, FloatContainer, HSplit, Layout, VSplit, Window
from prompt_toolkit.layout.containers import ConditionalContainer
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Frame

from reidcli.provider.popular import POPULAR_PROVIDERS
from reidcli.ui.theme import PRIMARY

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
    seen: set[tuple[str, str]] = set()
    for name, kind, base_url, default_model, description in POPULAR_PROVIDERS:
        key = (kind, base_url)
        if key in seen:
            continue
        seen.add(key)
        # Derive a clean provider name from the first entry for this kind/base_url
        provider_name = name.split(" — ")[0] if " — " in name else name
        entries.append(ProviderEntry(
            name=provider_name,
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


class ProviderPicker:
    CUSTOM_FIELD_SPECS = [
        ("name", "Provider Name", "my-provider", "Unique name (e.g., 'my-llama', 'company-gpt')"),
        ("kind", "Provider Kind", "openai-compatible", "anthropic | openai | openai-compatible | ollama"),
        ("base_url", "Base URL", "https://api.example.com/v1", "API endpoint (empty for defaults)"),
        ("api_key", "API Key", "", "Your API key (hidden)"),
        ("default_model", "Default Model", "model-name", "Default model (e.g., 'llama-3.1-70b')"),
    ]

    def __init__(self, on_select: Callable[[ProviderEntry], None], on_custom: Callable[[dict], None], on_cancel: Callable[[], None]) -> None:
        self.on_select = on_select
        self.on_custom = on_custom
        self.on_cancel = on_cancel

        self.entries = PROVIDER_ENTRIES
        self.filtered_entries = list(self.entries)
        self.selected_index = 0
        self.search_query = ""
        self.mode = "list"
        self.custom_field_index = 0
        self.custom_buffers: dict[str, Buffer] = {}
        self._anim_start = time.time()
        self._app: Optional[Application] = None

        self._build_search_buffer()
        self._build_custom_buffers()
        self._build_key_bindings()

    def _build_search_buffer(self) -> None:
        self.search_buffer = Buffer()

    def _build_custom_buffers(self) -> None:
        for field_id, label, default, help_text in self.CUSTOM_FIELD_SPECS:
            buf = Buffer()
            if default:
                buf.text = default
            self.custom_buffers[field_id] = buf

    def _build_key_bindings(self) -> None:
        self.kb = KeyBindings()

        @self.kb.add("up")
        def _up(event) -> None:
            if self.mode != "list":
                return
            if self.selected_index > 0:
                self.selected_index -= 1
            event.app.invalidate()

        @self.kb.add("down")
        def _down(event) -> None:
            if self.mode != "list":
                return
            max_idx = len(self.filtered_entries)
            if self.selected_index < max_idx:
                self.selected_index += 1
            event.app.invalidate()

        @self.kb.add("pageup")
        def _page_up(event) -> None:
            if self.mode != "list":
                return
            self.selected_index = max(0, self.selected_index - 8)
            event.app.invalidate()

        @self.kb.add("pagedown")
        def _page_down(event) -> None:
            if self.mode != "list":
                return
            self.selected_index = min(len(self.filtered_entries), self.selected_index + 8)
            event.app.invalidate()

        @self.kb.add("home")
        def _home(event) -> None:
            if self.mode != "list":
                return
            self.selected_index = 0
            event.app.invalidate()

        @self.kb.add("end")
        def _end(event) -> None:
            if self.mode != "list":
                return
            self.selected_index = len(self.filtered_entries)
            event.app.invalidate()

        @self.kb.add("enter")
        def _enter(event) -> None:
            if self.mode == "custom":
                self._submit_custom()
                event.app.exit()
                return
            if self.selected_index >= len(self.filtered_entries):
                self.mode = "custom"
                self.custom_field_index = 0
                event.app.layout.focus(self.custom_buffers["name"])
            elif self.filtered_entries:
                self.on_select(self.filtered_entries[self.selected_index])
                event.app.exit()
            event.app.invalidate()

        @self.kb.add("escape")
        def _escape(event) -> None:
            if self.mode == "custom":
                self.mode = "list"
                event.app.layout.focus(self.search_buffer)
            else:
                self.on_cancel()
                event.app.exit()
            event.app.invalidate()

        @self.kb.add("c-c")
        def _ctrl_c(event) -> None:
            self.on_cancel()
            event.app.exit()

        def on_search_change(buf: Buffer) -> None:
            self.search_query = buf.text
            self._filter_entries()
            self.selected_index = 0
            if self._app:
                self._app.invalidate()

        self.search_buffer.on_text_changed += on_search_change

        @self.kb.add("tab")
        def _tab(event) -> None:
            if self.mode == "custom":
                self.custom_field_index = (self.custom_field_index + 1) % len(self.CUSTOM_FIELD_SPECS)
                field_id = self.CUSTOM_FIELD_SPECS[self.custom_field_index][0]
                event.app.layout.focus(self.custom_buffers[field_id])
            else:
                focused = event.app.layout.current_window
                search_window = self._search_window
                if focused == search_window:
                    event.app.layout.focus(self._list_control)
                else:
                    event.app.layout.focus(self.search_buffer)

        @self.kb.add("s-tab")
        def _shift_tab(event) -> None:
            if self.mode == "custom":
                self.custom_field_index = (self.custom_field_index - 1) % len(self.CUSTOM_FIELD_SPECS)
                field_id = self.CUSTOM_FIELD_SPECS[self.custom_field_index][0]
                event.app.layout.focus(self.custom_buffers[field_id])
            else:
                focused = event.app.layout.current_window
                search_window = self._search_window
                if focused == search_window:
                    event.app.layout.focus(self._list_control)
                else:
                    event.app.layout.focus(self.search_buffer)

        @self.kb.add("/")
        def _slash(event) -> None:
            if self.mode != "custom":
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
        if self.selected_index >= len(self.filtered_entries):
            self.selected_index = max(0, len(self.filtered_entries) - 1)

    def _submit_custom(self) -> None:
        values = {}
        for field_id, label, default, help_text in self.CUSTOM_FIELD_SPECS:
            values[field_id] = self.custom_buffers[field_id].text
        self.on_custom(values)
        self.mode = "list"

    def _get_custom_field_prompt(self, field_id: str, label: str, index: int) -> list:
        is_sel = self.custom_field_index == index
        prefix = "▸ " if is_sel else "  "
        style = "class:picker-title" if is_sel else "class:picker-footer"
        return [(style, f"{prefix}{label}: ")]

    def _build_container(self):
        search_prompt_control = FormattedTextControl(
            lambda: [("class:picker-search-prompt", "  ⌕  Search providers...")]
        )

        self._search_control = BufferControl(buffer=self.search_buffer, focusable=True, lexer=None)
        search_input_window = Window(content=self._search_control, style="class:picker-search")
        self._search_window = search_input_window

        search_row = VSplit([
            Window(content=search_prompt_control, width=22, style="class:picker-search"),
            search_input_window,
        ], height=1)

        def get_list_fragments():
            fragments = []
            now = time.time()
            pulse_val = (int((now - self._anim_start) * 2) % 2)

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

            if self.mode == "list":
                marker = "✦" if pulse_val else "✧"
                customs_style = "class:picker-custom-highlight" if (self.selected_index >= len(self.filtered_entries)) else "class:picker-custom"
                if fragments:
                    fragments.append(("", "\n"))
                fragments.append((customs_style, f"  {marker} Create custom provider"))

            return fragments

        list_control = FormattedTextControl(get_list_fragments, focusable=True)
        self._list_control = list_control
        list_window = Window(content=list_control, style="class:picker-bg")

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
            if self.mode == "custom":
                return [
                    ("class:picker-shortcut", " Tab "),
                    ("class:picker-footer", "next field   "),
                    ("class:picker-shortcut", "Enter "),
                    ("class:picker-footer", "save   "),
                    ("class:picker-shortcut", "Esc "),
                    ("class:picker-footer", "cancel"),
                ]
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

        footer_control = FormattedTextControl(get_footer_fragments)

        title_text = "  ✦ Create Custom Provider  " if self.mode == "custom" else "  ✦ Select LLM Provider  "
        title_bar = Window(
            content=FormattedTextControl(lambda: [("class:picker-title", title_text)]),
            height=1,
            style="class:picker-card",
        )

        list_body = HSplit([
            title_bar,
            Window(height=1, char="─", style="class:picker-border"),
            search_row,
            Window(height=1, char="─", style="class:picker-border"),
            list_window,
            Window(height=1, char="─", style="class:picker-border"),
            VSplit([
                Window(content=footer_control, style="class:picker-bg"),
                count_bar,
            ]),
        ])

        custom_field_rows = []
        for i, (field_id, label, default, help_text) in enumerate(self.CUSTOM_FIELD_SPECS):
            is_password = field_id == "api_key"

            prompt_control = FormattedTextControl(
                lambda fid=field_id, lbl=label, idx=i: self._get_custom_field_prompt(fid, lbl, idx)
            )

            field_window = Window(
                content=BufferControl(buffer=self.custom_buffers[field_id], focusable=True),
                height=1,
                style="class:picker-search",
            )

            help_control = FormattedTextControl(
                lambda ht=help_text: [("class:picker-subtitle", f"    {ht}")]
            )
            help_window = Window(content=help_control, height=1, style="class:picker-bg")

            custom_field_rows.append(HSplit([
                Window(content=prompt_control, height=1, style="class:picker-bg"),
                field_window,
                help_window,
            ]))

        custom_body = HSplit([
            title_bar,
            Window(height=1, char="─", style="class:picker-border"),
            Window(height=1, style="class:picker-bg"),
            *custom_field_rows,
            Window(height=1, style="class:picker-bg"),
        ])

        body = ConditionalContainer(
            content=list_body,
            filter=Condition(lambda: self.mode == "list"),
        )
        body_custom = ConditionalContainer(
            content=custom_body,
            filter=Condition(lambda: self.mode == "custom"),
        )

        outer = HSplit([body, body_custom])

        frame = Frame(body=outer, style="class:picker-border")

        root = FloatContainer(
            content=frame,
            floats=[
                Float(
                    xcursor=True,
                    ycursor=True,
                    content=CompletionsMenu(max_height=12, scroll_offset=1, display_arrows=True),
                ),
            ],
        )

        return root

    async def run_async(self) -> None:
        root = self._build_container()
        app = Application(
            layout=Layout(root, focused_element=self.search_buffer),
            key_bindings=self.kb,
            style=PICKER_STYLE,
            full_screen=True,
            mouse_support=True,
        )
        self._app = app
        try:
            await app.run_async()
        except (EOFError, KeyboardInterrupt):
            self.on_cancel()


def pick_provider(
    on_select: Callable[[ProviderEntry], None],
    on_custom: Callable[[dict], None],
    on_cancel: Callable[[], None],
) -> None:
    import asyncio
    import threading

    def run_picker():
        try:
            picker = ProviderPicker(on_select, on_custom, on_cancel)
            asyncio.run(picker.run_async())
        except Exception as e:
            from reidcli.ui import render
            render.print_error(f"Provider picker error: {e}")

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        run_picker()
    else:
        t = threading.Thread(target=run_picker, daemon=True)
        t.start()
        t.join()