#!/usr/bin/env python3
"""Generate every Violeeter export from `violeeter.json`.

# Why a generator

A palette is thirty-six hex values times one file per terminal. Copied by hand,
the copies drift — and a palette that is *almost* the same in two terminals is
worse than two different palettes, because the difference reads as a rendering
bug rather than as a choice. `violeeter.json` is the only file anyone edits.

Usage:
    python3 build.py            # write dist/
    python3 build.py --check    # verify contrast, exit non-zero on failure
"""

from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent
SOURCE = ROOT / "violeeter.json"
DIST = ROOT / "dist"

ORDER = [
    "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
    "brightBlack", "brightRed", "brightGreen", "brightYellow",
    "brightBlue", "brightMagenta", "brightCyan", "brightWhite",
]

# Nothing is exempt.
#
# There used to be an exemption here for `white` and `brightWhite` in the light
# variant, on the reasoning that they mean "the palest thing available" and so
# are surfaces rather than text. That reasoning is correct about the *name* and
# wrong about the *use*: colour 7 is the default foreground of a large share of
# terminal programs. Opening btop under the light variant showed it plainly —
# `Used:`, `Available:`, `Cached:` and every figure beside them rendered at
# 1.61:1 and simply were not there.
#
# So the light variant's 7 and 15 are legible text now, and the checker has no
# way to look away. An exemption is a place a bug can hide, and this one hid a
# whole class of program.
LIGHT_FILLS: set[str] = set()

# Which entries of the `ui` block carry text. The line number column is read by
# a person looking for a line, so it is text and is held to AA; the rest are
# surfaces and only have to be distinguishable from the background.
UI_TEXT = {"gutter", "gutterActive"}


def rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _channel(c: int) -> float:
    v = c / 255
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def luminance(h: str) -> float:
    r, g, b = rgb(h)
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------

def iterm(v: dict) -> str:
    """iTerm2 wants floats per channel, and its own key names."""
    def component(h: str, key: str) -> str:
        r, g, b = rgb(h)
        return (
            f"\t<key>{key}</key>\n\t<dict>\n"
            f"\t\t<key>Color Space</key>\n\t\t<string>sRGB</string>\n"
            f"\t\t<key>Red Component</key>\n\t\t<real>{r / 255:.6f}</real>\n"
            f"\t\t<key>Green Component</key>\n\t\t<real>{g / 255:.6f}</real>\n"
            f"\t\t<key>Blue Component</key>\n\t\t<real>{b / 255:.6f}</real>\n"
            f"\t\t<key>Alpha Component</key>\n\t\t<real>1</real>\n\t</dict>\n"
        )

    body = "".join(
        component(v["ansi"][name], f"Ansi {i} Color")
        for i, name in enumerate(ORDER)
    )
    body += component(v["background"], "Background Color")
    body += component(v["foreground"], "Foreground Color")
    body += component(v["cursor"], "Cursor Color")
    body += component(v["background"], "Cursor Text Color")
    body += component(v["selection"], "Selection Color")
    body += component(v["foreground"], "Selected Text Color")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
        '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
        '<plist version="1.0">\n<dict>\n' + body + "</dict>\n</plist>\n"
    )


def alacritty(v: dict) -> str:
    a = v["ansi"]
    return f"""# {v['name']} — https://github.com/grippado/violeet
[colors.primary]
background = "{v['background']}"
foreground = "{v['foreground']}"

[colors.cursor]
cursor = "{v['cursor']}"
text = "{v['background']}"

[colors.selection]
background = "{v['selection']}"
text = "{v['foreground']}"

[colors.normal]
black = "{a['black']}"
red = "{a['red']}"
green = "{a['green']}"
yellow = "{a['yellow']}"
blue = "{a['blue']}"
magenta = "{a['magenta']}"
cyan = "{a['cyan']}"
white = "{a['white']}"

[colors.bright]
black = "{a['brightBlack']}"
red = "{a['brightRed']}"
green = "{a['brightGreen']}"
yellow = "{a['brightYellow']}"
blue = "{a['brightBlue']}"
magenta = "{a['brightMagenta']}"
cyan = "{a['brightCyan']}"
white = "{a['brightWhite']}"
"""


def kitty(v: dict) -> str:
    a = v["ansi"]
    lines = [
        f"# {v['name']} — https://github.com/grippado/violeet",
        f"background {v['background']}",
        f"foreground {v['foreground']}",
        f"cursor {v['cursor']}",
        f"cursor_text_color {v['background']}",
        f"selection_background {v['selection']}",
        f"selection_foreground {v['foreground']}",
    ]
    lines += [f"color{i} {a[name]}" for i, name in enumerate(ORDER)]
    return "\n".join(lines) + "\n"


def ghostty(v: dict) -> str:
    a = v["ansi"]
    lines = [
        f"# {v['name']} — https://github.com/grippado/violeet",
        f"background = {v['background'].lstrip('#')}",
        f"foreground = {v['foreground'].lstrip('#')}",
        f"cursor-color = {v['cursor'].lstrip('#')}",
        f"selection-background = {v['selection'].lstrip('#')}",
        f"selection-foreground = {v['foreground'].lstrip('#')}",
    ]
    lines += [f"palette = {i}={a[name]}" for i, name in enumerate(ORDER)]
    return "\n".join(lines) + "\n"


def windows_terminal(v: dict) -> str:
    a = v["ansi"]
    scheme = {
        "name": v["name"],
        "background": v["background"],
        "foreground": v["foreground"],
        "cursorColor": v["cursor"],
        "selectionBackground": v["selection"],
        "black": a["black"], "red": a["red"], "green": a["green"],
        "yellow": a["yellow"], "blue": a["blue"], "purple": a["magenta"],
        "cyan": a["cyan"], "white": a["white"],
        "brightBlack": a["brightBlack"], "brightRed": a["brightRed"],
        "brightGreen": a["brightGreen"], "brightYellow": a["brightYellow"],
        "brightBlue": a["brightBlue"], "brightPurple": a["brightMagenta"],
        "brightCyan": a["brightCyan"], "brightWhite": a["brightWhite"],
    }
    return json.dumps(scheme, indent=2) + "\n"


def css(data: dict) -> str:
    """Both variants as custom properties, dark by default and light by query.

    This is what the project page renders itself with, so the page cannot drift
    from the palette it is advertising.
    """
    def block(v: dict, indent: str = "  ") -> str:
        a = v["ansi"]
        rows = [
            f"{indent}--violeeter-bg: {v['background']};",
            f"{indent}--violeeter-fg: {v['foreground']};",
            f"{indent}--violeeter-cursor: {v['cursor']};",
            f"{indent}--violeeter-selection: {v['selection']};",
        ]
        rows += [f"{indent}--violeeter-{name.lower()}: {a[name]};" for name in ORDER]
        return "\n".join(rows)

    dark, light = data["variants"]["dark"], data["variants"]["light"]
    return f"""/* Violeeter {data['version']} — https://github.com/grippado/violeet
   Generated by theme/build.py. Do not edit. */
:root {{
{block(light)}
}}

@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
{block(dark, "    ")}
  }}
}}

:root[data-theme="dark"] {{
{block(dark)}
}}
"""


def wezterm(v: dict) -> str:
    a = v["ansi"]
    normal = ", ".join(f'"{a[n]}"' for n in ORDER[:8])
    bright = ", ".join(f'"{a[n]}"' for n in ORDER[8:])
    return f"""# {v['name']} — https://github.com/grippado/violeeter
[colors]
foreground = "{v['foreground']}"
background = "{v['background']}"
cursor_bg = "{v['cursor']}"
cursor_fg = "{v['background']}"
cursor_border = "{v['cursor']}"
selection_bg = "{v['selection']}"
selection_fg = "{v['foreground']}"
ansi = [{normal}]
brights = [{bright}]
"""


# --- editors ---------------------------------------------------------------
#
# An editor port is the palette plus one mapping: which slot plays which part in
# code. The mapping lives in `violeeter.json` under `syntax` and is resolved
# here, so every editor gets the same green for a string. Re-picking colours per
# editor is how a theme ends up subtly different in each one.

def resolve(v: dict, syntax: dict, role: str) -> str:
    slot = syntax[role]
    if slot in v:
        return v[slot]
    return v["ansi"][slot]


def vscode(v: dict, syntax: dict) -> str:
    c = lambda role: resolve(v, syntax, role)
    ui = v["ui"]
    bg, fg = v["background"], v["foreground"]

    colors = {
        "editor.background": bg,
        "editor.foreground": fg,
        "editorCursor.foreground": v["cursor"],
        "editor.selectionBackground": v["selection"],
        "editor.lineHighlightBackground": ui["lineHighlight"],
        "editorLineNumber.foreground": ui["gutter"],
        "editorLineNumber.activeForeground": ui["gutterActive"],
        "editorIndentGuide.background1": ui["border"],
        "editorWhitespace.foreground": ui["border"],
        "editorGutter.addedBackground": c("added"),
        "editorGutter.deletedBackground": c("removed"),
        "editorGutter.modifiedBackground": c("modified"),
        "editorError.foreground": c("error"),
        "editorWarning.foreground": c("warning"),
        "editorInfo.foreground": c("info"),
        "activityBar.background": ui["surface"],
        "activityBar.foreground": fg,
        "activityBarBadge.background": ui["accent"],
        "activityBarBadge.foreground": ui["onAccent"],
        "sideBar.background": ui["surface"],
        "sideBar.foreground": fg,
        "sideBar.border": ui["border"],
        "sideBarSectionHeader.background": ui["surface"],
        "statusBar.background": ui["surface"],
        "statusBar.foreground": fg,
        "statusBar.border": ui["border"],
        "titleBar.activeBackground": ui["surface"],
        "titleBar.activeForeground": fg,
        "tab.activeBackground": bg,
        "tab.activeForeground": fg,
        "tab.inactiveBackground": ui["surface"],
        "tab.border": ui["border"],
        "tab.activeBorderTop": ui["accent"],
        "editorGroupHeader.tabsBackground": ui["surface"],
        "panel.background": ui["surface"],
        "panel.border": ui["border"],
        "terminal.background": bg,
        "terminal.foreground": fg,
        "terminalCursor.foreground": v["cursor"],
        "button.background": ui["accent"],
        "button.foreground": ui["onAccent"],
        "focusBorder": ui["accent"],
        "list.activeSelectionBackground": ui["surfaceRaised"],
        "list.activeSelectionForeground": fg,
        "list.hoverBackground": ui["surface"],
        "input.background": ui["surfaceRaised"],
        "input.border": ui["border"],
        "dropdown.background": ui["surfaceRaised"],
        "widget.border": ui["border"],
        "scrollbarSlider.background": ui["border"],
    }
    for i, name in enumerate(ORDER):
        key = "terminal.ansi" + name[0].upper() + name[1:]
        colors[key] = v["ansi"][name]

    scopes = [
        ("Comments", ["comment", "punctuation.definition.comment"], c("comment"), "italic"),
        ("Strings", ["string", "string.quoted", "punctuation.definition.string"], c("string"), None),
        ("String escapes", ["constant.character.escape"], c("stringEscape"), None),
        ("Numbers", ["constant.numeric"], c("number"), None),
        ("Booleans and constants", ["constant.language", "constant.other"], c("boolean"), None),
        ("Keywords", ["keyword", "storage.type", "storage.modifier"], c("keyword"), None),
        ("Control keywords", ["keyword.control"], c("keywordControl"), None),
        ("Operators", ["keyword.operator"], c("operator"), None),
        ("Punctuation", ["punctuation", "meta.brace"], c("punctuation"), None),
        ("Functions", ["entity.name.function", "support.function"], c("function"), None),
        ("Methods", ["meta.function-call", "variable.function"], c("method"), None),
        ("Types", ["entity.name.type", "support.type", "storage.type.primitive"], c("type"), None),
        ("Classes", ["entity.name.class", "support.class"], c("class"), None),
        ("Namespaces", ["entity.name.namespace", "entity.name.module"], c("namespace"), None),
        ("Variables", ["variable", "variable.other"], c("variable"), None),
        ("Parameters", ["variable.parameter"], c("parameter"), None),
        ("Properties", ["variable.other.property", "support.variable.property", "meta.object-literal.key"], c("property"), None),
        ("Tags", ["entity.name.tag"], c("tag"), None),
        ("Attributes", ["entity.other.attribute-name"], c("attribute"), None),
        ("Regular expressions", ["string.regexp"], c("regexp"), None),
        ("Invalid", ["invalid"], c("error"), None),
        ("Diff added", ["markup.inserted"], c("added"), None),
        ("Diff removed", ["markup.deleted"], c("removed"), None),
        ("Diff changed", ["markup.changed"], c("modified"), None),
        ("Markdown heading", ["markup.heading"], c("function"), "bold"),
        ("Markdown link", ["markup.underline.link"], c("type"), "underline"),
        ("Markdown emphasis", ["markup.italic"], None, "italic"),
        ("Markdown strong", ["markup.bold"], None, "bold"),
    ]

    token_colors = []
    for name, scope, colour, style in scopes:
        settings: dict[str, str] = {}
        if colour:
            settings["foreground"] = colour
        if style:
            settings["fontStyle"] = style
        token_colors.append({"name": name, "scope": scope, "settings": settings})

    theme = {
        "name": v["name"],
        "type": v["appearance"],
        "semanticHighlighting": True,
        "colors": colors,
        "tokenColors": token_colors,
    }
    return json.dumps(theme, indent=2) + "\n"


def neovim(v: dict, syntax: dict) -> str:
    """A colorscheme that sets highlight groups directly — no plugin, no deps.

    Drop it in `colors/` and `:colorscheme violeeter-dark` works. Treesitter
    groups are included and link to the same colours, so a file looks the same
    whether or not treesitter is attached.
    """
    c = lambda role: resolve(v, syntax, role)
    a, ui = v["ansi"], v["ui"]
    bg, fg = v["background"], v["foreground"]

    groups = [
        ("Normal", fg, bg, None),
        ("NormalFloat", fg, ui["surface"], None),
        ("FloatBorder", ui["border"], ui["surface"], None),
        ("Cursor", bg, v["cursor"], None),
        ("CursorLine", None, ui["lineHighlight"], None),
        ("CursorLineNr", ui["gutterActive"], None, "bold"),
        ("LineNr", ui["gutter"], None, None),
        ("SignColumn", None, bg, None),
        ("Visual", None, v["selection"], None),
        ("Search", bg, c("attribute"), None),
        ("IncSearch", bg, ui["accent"], None),
        ("StatusLine", fg, ui["surface"], None),
        ("VertSplit", ui["border"], None, None),
        ("WinSeparator", ui["border"], None, None),
        ("Pmenu", fg, ui["surface"], None),
        ("PmenuSel", ui["onAccent"], ui["accent"], None),
        ("TabLine", ui["gutter"], ui["surface"], None),
        ("TabLineSel", fg, bg, None),
        ("MatchParen", ui["accent"], None, "bold"),
        ("NonText", ui["border"], None, None),
        ("Whitespace", ui["border"], None, None),
        ("Directory", c("type"), None, None),
        ("Title", c("function"), None, "bold"),
        # Syntax
        ("Comment", c("comment"), None, "italic"),
        ("String", c("string"), None, None),
        ("Character", c("string"), None, None),
        ("Number", c("number"), None, None),
        ("Float", c("number"), None, None),
        ("Boolean", c("boolean"), None, None),
        ("Constant", c("constant"), None, None),
        ("Identifier", c("variable"), None, None),
        ("Function", c("function"), None, None),
        ("Statement", c("keyword"), None, None),
        ("Conditional", c("keywordControl"), None, None),
        ("Repeat", c("keywordControl"), None, None),
        ("Keyword", c("keyword"), None, None),
        ("Operator", c("operator"), None, None),
        ("PreProc", c("namespace"), None, None),
        ("Include", c("keywordControl"), None, None),
        ("Type", c("type"), None, None),
        ("StorageClass", c("keyword"), None, None),
        ("Structure", c("class"), None, None),
        ("Special", c("stringEscape"), None, None),
        ("Delimiter", c("punctuation"), None, None),
        ("Todo", bg, c("attribute"), "bold"),
        ("Error", c("error"), None, None),
        # Diagnostics
        ("DiagnosticError", c("error"), None, None),
        ("DiagnosticWarn", c("warning"), None, None),
        ("DiagnosticInfo", c("info"), None, None),
        ("DiagnosticHint", c("hint"), None, None),
        # Diff
        ("DiffAdd", c("added"), None, None),
        ("DiffDelete", c("removed"), None, None),
        ("DiffChange", c("modified"), None, None),
        ("DiffText", c("modified"), None, "bold"),
        # Treesitter
        ("@comment", c("comment"), None, "italic"),
        ("@string", c("string"), None, None),
        ("@string.escape", c("stringEscape"), None, None),
        ("@string.regexp", c("regexp"), None, None),
        ("@number", c("number"), None, None),
        ("@boolean", c("boolean"), None, None),
        ("@constant", c("constant"), None, None),
        ("@keyword", c("keyword"), None, None),
        ("@keyword.control", c("keywordControl"), None, None),
        ("@operator", c("operator"), None, None),
        ("@punctuation.delimiter", c("punctuation"), None, None),
        ("@punctuation.bracket", c("punctuation"), None, None),
        ("@function", c("function"), None, None),
        ("@function.call", c("method"), None, None),
        ("@function.method", c("method"), None, None),
        ("@type", c("type"), None, None),
        ("@type.builtin", c("type"), None, None),
        ("@module", c("namespace"), None, None),
        ("@variable", c("variable"), None, None),
        ("@variable.parameter", c("parameter"), None, None),
        ("@variable.member", c("property"), None, None),
        ("@property", c("property"), None, None),
        ("@tag", c("tag"), None, None),
        ("@tag.attribute", c("attribute"), None, None),
        ("@markup.heading", c("function"), None, "bold"),
        ("@markup.link", c("type"), None, "underline"),
    ]

    lines = [
        f'-- {v["name"]} — https://github.com/grippado/violeeter',
        "-- Generated by build.py. Do not edit.",
        "",
        "vim.cmd('highlight clear')",
        "if vim.fn.exists('syntax_on') == 1 then vim.cmd('syntax reset') end",
        f"vim.o.background = '{v['appearance']}'",
        f"vim.g.colors_name = 'violeeter-{v['appearance']}'",
        "",
        "local hl = vim.api.nvim_set_hl",
        "",
    ]
    for name, fore, back, style in groups:
        parts = []
        if fore:
            parts.append(f"fg = '{fore}'")
        if back:
            parts.append(f"bg = '{back}'")
        if style == "bold":
            parts.append("bold = true")
        elif style == "italic":
            parts.append("italic = true")
        elif style == "underline":
            parts.append("underline = true")
        lines.append(f"hl(0, '{name}', {{ {', '.join(parts)} }})")

    lines.append("")
    lines.append("-- Terminal colours, so :terminal matches the buffer beside it.")
    for i, name in enumerate(ORDER):
        lines.append(f"vim.g.terminal_color_{i} = '{a[name]}'")
    return "\n".join(lines) + "\n"


def zed(v: dict, syntax: dict) -> str:
    c = lambda role: resolve(v, syntax, role)
    a, ui = v["ansi"], v["ui"]
    style = {
        "background": v["background"],
        "foreground": v["foreground"],
        "editor.background": v["background"],
        "editor.foreground": v["foreground"],
        "editor.line_number": ui["gutter"],
        "editor.active_line_number": ui["gutterActive"],
        "editor.active_line.background": ui["lineHighlight"],
        "border": ui["border"],
        "surface.background": ui["surface"],
        "elevated_surface.background": ui["surfaceRaised"],
        "element.selected": v["selection"],
        "text": v["foreground"],
        "text.muted": ui["gutter"],
        "terminal.background": v["background"],
        "terminal.foreground": v["foreground"],
        "terminal.ansi.black": a["black"], "terminal.ansi.red": a["red"],
        "terminal.ansi.green": a["green"], "terminal.ansi.yellow": a["yellow"],
        "terminal.ansi.blue": a["blue"], "terminal.ansi.magenta": a["magenta"],
        "terminal.ansi.cyan": a["cyan"], "terminal.ansi.white": a["white"],
        "terminal.ansi.bright_black": a["brightBlack"], "terminal.ansi.bright_red": a["brightRed"],
        "terminal.ansi.bright_green": a["brightGreen"], "terminal.ansi.bright_yellow": a["brightYellow"],
        "terminal.ansi.bright_blue": a["brightBlue"], "terminal.ansi.bright_magenta": a["brightMagenta"],
        "terminal.ansi.bright_cyan": a["brightCyan"], "terminal.ansi.bright_white": a["brightWhite"],
        "error": c("error"), "warning": c("warning"), "info": c("info"), "hint": c("hint"),
        "created": c("added"), "deleted": c("removed"), "modified": c("modified"),
        "syntax": {
            "comment": {"color": c("comment"), "font_style": "italic"},
            "string": {"color": c("string")},
            "string.escape": {"color": c("stringEscape")},
            "string.regex": {"color": c("regexp")},
            "number": {"color": c("number")},
            "boolean": {"color": c("boolean")},
            "constant": {"color": c("constant")},
            "keyword": {"color": c("keyword")},
            "operator": {"color": c("operator")},
            "punctuation": {"color": c("punctuation")},
            "function": {"color": c("function")},
            "function.method": {"color": c("method")},
            "type": {"color": c("type")},
            "variable": {"color": c("variable")},
            "variable.parameter": {"color": c("parameter")},
            "property": {"color": c("property")},
            "tag": {"color": c("tag")},
            "attribute": {"color": c("attribute")},
        },
    }
    return json.dumps({
        "$schema": "https://zed.dev/schema/themes/v0.2.0.json",
        "name": "Violeeter",
        "author": "grippado",
        "themes": [{"name": v["name"], "appearance": v["appearance"], "style": style}],
    }, indent=2) + "\n"


def btop(v: dict, syntax: dict) -> str:
    """btop, which draws in truecolor and ignores the ANSI palette entirely.

    Worth spelling out, because it looks like a theme bug and is not: btop ships
    its own themes and uses them verbatim, so a terminal palette has no say in
    what it draws. Running it under a light background with a dark btop theme
    still selected leaves every label at the contrast that theme chose against a
    background it no longer has — the memory labels vanish, and it reads as the
    terminal theme being broken.

    So the theme has to be ported here too. `theme_background = false` in the
    user's config is the setting that lets `main_bg` stay empty and the
    terminal's own background show through; this file sets it anyway, so it is
    right either way.

    The gradients are three stops each. They run from the palette rather than
    from invented colours, which is what keeps a btop under this theme looking
    like the editor beside it.
    """
    a, ui = v["ansi"], v["ui"]
    keys = {
        "main_bg": v["background"],
        "main_fg": v["foreground"],
        "title": v["foreground"],
        "hi_fg": ui["accent"],
        "selected_bg": v["selection"],
        "selected_fg": v["foreground"],
        # The one that carries this whole port: labels and axis figures. It is
        # text, so it clears AA like any other text.
        "inactive_fg": ui["gutter"],
        "graph_text": ui["gutterActive"],
        "meter_bg": ui["border"],
        "proc_misc": a["brightCyan"],
        # Box outlines, one hue per box so they stay tellable apart.
        "cpu_box": a["magenta"],
        "mem_box": a["yellow"],
        "net_box": a["blue"],
        "proc_box": a["cyan"],
        "div_line": ui["border"],
        # Temperature: cool to hot.
        "temp_start": a["cyan"], "temp_mid": a["yellow"], "temp_end": a["red"],
        # Load: quiet to alarming, the same ramp the session card uses.
        "cpu_start": a["green"], "cpu_mid": a["yellow"], "cpu_end": a["red"],
        "free_start": a["brightGreen"], "free_mid": "", "free_end": a["green"],
        "cached_start": a["brightCyan"], "cached_mid": "", "cached_end": a["cyan"],
        "available_start": a["brightYellow"], "available_mid": "", "available_end": a["yellow"],
        "used_start": a["brightRed"], "used_mid": "", "used_end": a["red"],
        "download_start": a["brightBlue"], "download_mid": "", "download_end": a["blue"],
        "upload_start": a["brightMagenta"], "upload_mid": "", "upload_end": a["magenta"],
        "process_start": a["blue"], "process_mid": a["magenta"], "process_end": a["red"],
    }
    lines = [
        f"# {v['name']} for btop — https://github.com/grippado/violeeter",
        "# Generated by build.py. Do not edit.",
        "#",
        "# Install: copy to ~/.config/btop/themes/ and set in btop's options (Esc),",
        "# or  color_theme = \"violeeter-dark\"  in ~/.config/btop/btop.conf",
        "",
    ]
    lines += [f'theme[{k}]="{value}"' for k, value in keys.items()]
    return "\n".join(lines) + "\n"


def tailwind(data: dict) -> str:
    """Both variants as a Tailwind colour scale, for sites built on the theme."""
    def block(v: dict) -> str:
        rows = [f'      background: "{v["background"]}",',
                f'      foreground: "{v["foreground"]}",',
                f'      accent: "{v["ui"]["accent"]}",',
                f'      surface: "{v["ui"]["surface"]}",',
                f'      border: "{v["ui"]["border"]}",']
        rows += [f'      {name.lower()}: "{v["ansi"][name]}",' for name in ORDER]
        return "\n".join(rows)

    return f"""// Violeeter {data['version']} — https://github.com/grippado/violeeter
// Generated by build.py. Do not edit.
module.exports = {{
  theme: {{
    extend: {{
      colors: {{
        violeeter: {{
          dark: {{
{block(data['variants']['dark'])}
          }},
          light: {{
{block(data['variants']['light'])}
          }},
        }},
      }},
    }},
  }},
}};
"""


EXPORTS = {
    "itermcolors": iterm,
    "toml": alacritty,
    "conf": kitty,
    "ghostty": ghostty,
    "json": windows_terminal,
    "wezterm.toml": wezterm,
}

EDITOR_EXPORTS = {
    "btop.theme": btop,
    "vscode.json": vscode,
    "nvim.lua": neovim,
    "zed.json": zed,
}


def check(data: dict) -> int:
    """Every colour used as text must clear WCAG AA against its background."""
    failures = 0
    for key, v in data["variants"].items():
        bg = v["background"]
        fills = LIGHT_FILLS if v["appearance"] == "light" else {"black"}
        worst, worst_name = 99.0, ""
        print(f"\n{v['name']}  (background {bg})")
        for name in ["foreground", "cursor"] + ORDER:
            colour = v[name] if name in v else v["ansi"][name]
            ratio = contrast(colour, bg)
            if name in fills:
                print(f"  {name:14} {colour}  {ratio:5.2f}  surface")
                continue
            ok = ratio >= 4.5
            if ratio < worst:
                worst, worst_name = ratio, name
            if not ok:
                failures += 1
            print(f"  {name:14} {colour}  {ratio:5.2f}  {'ok' if ok else 'FAIL — under AA 4.5'}")

        # The `ui` block was invisible to this loop, which walked the ANSI slots
        # and nothing else. That is how `gutter` shipped at 2.91 — and `gutter`
        # is the line number column, which is text somebody reads while looking
        # for a line. A checker that only measures the colours you remembered to
        # list measures your memory, not the theme.
        for name, colour in v.get("ui", {}).items():
            ratio = contrast(colour, bg)
            if name not in UI_TEXT:
                print(f"  ui.{name:11} {colour}  {ratio:5.2f}  surface")
                continue
            ok = ratio >= 4.5
            if ratio < worst:
                worst, worst_name = ratio, f"ui.{name}"
            if not ok:
                failures += 1
            print(f"  ui.{name:11} {colour}  {ratio:5.2f}  {'ok' if ok else 'FAIL — under AA 4.5'}")

        print(f"  worst text contrast: {worst:.2f} ({worst_name})")
    return failures


def main() -> int:
    data = json.loads(SOURCE.read_text())

    if "--check" in sys.argv:
        failures = check(data)
        print(f"\n{'PASS' if failures == 0 else f'{failures} FAILURES'}")
        return 1 if failures else 0

    DIST.mkdir(exist_ok=True)
    syntax = data["syntax"]
    for key, v in data["variants"].items():
        for ext, render in EXPORTS.items():
            (DIST / f"violeeter-{key}.{ext}").write_text(render(v))
        for ext, render in EDITOR_EXPORTS.items():
            (DIST / f"violeeter-{key}.{ext}").write_text(render(v, syntax))
    (DIST / "violeeter.tailwind.js").write_text(tailwind(data))
    stylesheet = css(data)
    (DIST / "violeeter.css").write_text(stylesheet)
    written = sorted(p.name for p in DIST.iterdir())
    print(f"wrote {len(written)} files to {DIST}/")
    for name in written:
        print(f"  {name}")

    # The project page is served from `docs/`, which cannot reach up into
    # `theme/`. Writing the stylesheet there too is what stops the page that
    # advertises this palette from being painted in a stale copy of it.
    page = ROOT / "docs"
    if page.is_dir():
        (page / "violeeter.css").write_text(stylesheet)
        # The palette itself, so the page can draw its swatches from the source
        # rather than from its own stylesheet. Reading them back out of CSS
        # meant asking the browser to recompute `:root` mid-script, which it
        # does not reliably do — the two variants came out identical.
        (page / "violeeter.json").write_text(SOURCE.read_text())
        print(f"wrote {page}/violeeter.css and violeeter.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
