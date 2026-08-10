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


def vscode_extension(data: dict, syntax: dict) -> dict[str, str]:
    """The whole publishable extension, as a path -> contents map.

    A theme extension is metadata plus the two files `vscode()` already writes,
    so the only thing worth guarding is that it stays *only* that. Hand-writing
    the `package.json` would create a second place a colour, a version or a name
    can live — and a `package.json` claiming 2.0.0 beside a palette at 2.1.0 is
    exactly the drift this generator exists to prevent. So the manifest is
    derived from `violeeter.json` too, and the themes are the same bytes as
    `dist/violeeter-{dark,light}.vscode.json`.

    `icon.png` is not written here: it is a raster of the mark, versioned under
    `assets/`, and `main()` copies it in. The Marketplace requires a 128x128 PNG
    and the mark is not derivable from the palette.
    """
    repo = "https://github.com/grippado/violeeter"
    dark, light = data["variants"]["dark"], data["variants"]["light"]

    manifest = {
        "name": "violeeter",
        "displayName": data["name"],
        "description": data["description"],
        "version": data["version"],
        "publisher": "grippado",
        "license": data["license"],
        "icon": "icon.png",
        "homepage": data["homepage"],
        "repository": {"type": "git", "url": f"{repo}.git"},
        "bugs": {"url": f"{repo}/issues"},
        "engines": {"vscode": "^1.70.0"},
        "categories": ["Themes"],
        "keywords": ["theme", "colour theme", "color theme", "violet",
                     "purple", "dark theme", "light theme", "accessibility",
                     "wcag"],
        # The banner sits behind the icon on the Marketplace page. `theme` tells
        # it which way to colour its own text; getting it wrong is how a listing
        # ends up with dark text on the dark background.
        "galleryBanner": {"color": dark["background"], "theme": "dark"},
        "contributes": {
            "themes": [
                {
                    "label": dark["name"],
                    "uiTheme": "vs-dark",
                    "path": "./themes/violeeter-dark.json",
                },
                {
                    "label": light["name"],
                    "uiTheme": "vs",
                    "path": "./themes/violeeter-light.json",
                },
            ]
        },
    }

    # Marketplace README images are fetched by their absolute URL — a relative
    # path resolves against marketplace.visualstudio.com and 404s.
    #
    # They are screenshots of the editor and not the logo. A listing has one
    # job, which is to show a reader what their code will look like, and the
    # mark answers a different question. The two are the same file at the same
    # scroll position under each variant, so the pair is a comparison rather
    # than two separate advertisements.
    raw = "https://raw.githubusercontent.com/grippado/violeeter/main"
    readme = f"""# {data['name']}

{data['description']}

Two themes, **{dark['name']}** and **{light['name']}**, generated from one
palette file. `Cmd+K Cmd+T` (`Ctrl+K Ctrl+T` on Windows and Linux) to switch.

![{dark['name']}]({raw}/assets/screenshot-dark.png)

![{light['name']}]({raw}/assets/screenshot-light.png)

## Every colour is checked

Every colour that carries text clears WCAG AA (4.5:1) against the background it
is drawn on, in both variants, and the build fails if one does not. That
includes the line number column, which is text somebody reads while looking for
a line, and colour 7 in the light variant, which is the default foreground of a
large share of terminal programs.

## The same theme everywhere else

This extension is one port of a palette that also ships for Neovim, Zed, iTerm2,
Alacritty, Kitty, Ghostty, WezTerm, Windows Terminal, btop, CSS and Tailwind.
Every port resolves the same role-to-slot mapping, so a string is the same green
in your editor and in the terminal beside it.

The full set, and the palette itself: <{data['homepage']}>

## Licence

{data['license']}. Take it, port it, change it.
"""

    # Everything the package does not need at runtime. The generated tree is
    # already minimal, so this is a guard against a future file rather than a
    # cleanup of a present one.
    vscodeignore = ".vscode/**\n**/*.map\n.gitignore\n"

    return {
        "package.json": json.dumps(manifest, indent=2) + "\n",
        "themes/violeeter-dark.json": vscode(dark, syntax),
        "themes/violeeter-light.json": vscode(light, syntax),
        "README.md": readme,
        ".vscodeignore": vscodeignore,
    }


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


def slack(v: dict) -> str:
    """The sidebar palette Slack imports, as a comma-separated theme string.

    Slack's slots are named for states rather than for surfaces, and the two
    that do not map cleanly are worth saying out loud. `menu bg hover` is not a
    hover at all — it is the background of the menus that open out of the
    sidebar — so it takes `surface`. `hover item` is the real hover, and takes
    `selection`, because hovering and selecting are the same gesture of picking
    a row out of a column, and `surfaceRaised` in the light variant is white:
    lighter than the sidebar, which makes a hover that vanishes.

    Comment lines are `//` and not `#` so that a line starting `#RRGGBB` reads
    as a colour and not as a comment — in the viewer on the project page, and
    in any editor you open the file in.
    """
    a, u = v["ansi"], v["ui"]
    # Legacy order, the one Slack's importer parses: column bg, menu bg hover,
    # active item, active item text, hover item, text, active presence,
    # mention badge — then the two top-bar slots some clients take.
    sidebar = [v["background"], u["surface"], u["accent"], u["onAccent"],
               v["selection"], v["foreground"], a["green"], a["red"]]
    top_nav = [u["surface"], v["foreground"]]
    return "\n".join([
        f"// {v['name']} for Slack — https://github.com/grippado/violeeter",
        "// Generated by build.py. Do not edit.",
        "//",
        "// Preferences → Appearance → Custom theme → Import theme, then paste",
        "// one of the lines below. Slack remaps an imported string onto the",
        "// slots of its current design and adjusts it for contrast, so this is",
        "// the palette as near as Slack allows, not to the hex.",
        "",
        "// Eight slots: column bg, menu bg hover, active item, active item",
        "// text, hover item, text, active presence, mention badge.",
        ",".join(sidebar),
        "",
        "// The same, plus top bar background and top bar text, for the clients",
        "// that take ten.",
        ",".join(sidebar + top_nav),
        "",
        "// The redesigned picker also exposes four fields you can fill by hand",
        "// instead of importing:",
        f"//   window background     {v['background']}",
        f"//   selected items        {u['accent']}",
        f"//   presence indication   {a['green']}",
        f"//   notifications         {a['red']}",
        "",
        "// The notification badge is the one colour Slack paints text on top",
        "// of, in a white it picks itself. Kept at `red` so the badge reads as",
        "// a badge against the sidebar; the count on it is Slack's contrast",
        "// adapter to sort out, and there is no slot in this palette that wins",
        "// both readings.",
    ]) + "\n"


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


def obsidian(data: dict, syntax: dict) -> str:
    """Obsidian, as one CSS snippet holding both variants.

    # Why this is not in EXPORTS or EDITOR_EXPORTS

    Both registries emit one file per variant, and that shape is wrong here.
    Obsidian switches theme at runtime by swapping `.theme-dark` for
    `.theme-light` on `body`, and a snippet is enabled or disabled as a whole in
    the settings pane — there is no per-variant hook to hang two files on. Ship
    them separately and a reader who flips to light gets a light chrome painted
    with dark-variant text, which is not a theme, it is a bug. So this follows
    the `css()` and `tailwind()` precedent instead: a function over the whole
    dataset, one file in `dist/`, both variants inside it.

    # Why variables and not selectors

    Obsidian's `--background-primary`, `--text-normal` and the rest are the
    documented surface a theme is built against; the class names underneath them
    are not, and they are renamed between releases. Overriding the variables
    means this snippet keeps working on top of whatever theme the reader already
    likes, and keeps working after an update. Specificity is not a fight: these
    rules are `.theme-dark`, the same weight as Obsidian's own declarations, and
    snippets are appended after the theme stylesheet, so later wins.

    The editor is the exception. Live Preview is CodeMirror 6, and its markdown
    and code decorations (`.cm-comment`, `.cm-string`, `.cm-header-1`) carry no
    variables at all — the only way to reach them is the class. Those rules are
    scoped under `.cm-s-obsidian` and kept to colour alone, so the blast radius
    of a future rename is a token that goes back to the theme's default rather
    than a broken layout.

    # The choices worth defending

    Headings run accent → brightMagenta → blue → cyan → brightCyan → brightBlack.
    The house colour is the top of the outline and the slot whose whole job is to
    recede is the bottom, because an h6 in a real note is a label and not a
    heading. Rejected: six colours from around the wheel, which makes an outline
    look like a legend for something.

    `surfaceRaised` is white in the light variant — lighter than the note
    background — so it can only be used where being lighter than the note is
    the point. That splits its uses in two. Chrome that sits *outside* the note
    (`--background-secondary-alt`, `--titlebar-background-focused`) keeps it:
    there the slot reads as a raised panel, and a panel that goes white on a
    near-white app frame is still a panel. Anything painted *inside* or *over*
    the note — tag pills, hover feedback, highlight backgrounds — must not use
    it, because it disappears against the note it is supposed to sit on. Those
    take `surface` and `selection` instead. `--interactive-hover` was the one
    that got this wrong: at `surfaceRaised` it measured 1.05 against
    `--background-primary` in the light variant, an invisible hover, and it now
    takes `selection`, the same slot `--background-modifier-hover` already
    used. Same trap the Slack port fell into and the same way out.

    Links take `type` (cyan), which is the slot the VS Code port already gives
    `markup.underline.link`. A link is the same thing in a note and in a
    markdown file open in the editor beside it, so it is the same colour.
    """
    c = lambda v, role: resolve(v, syntax, role)

    def variables(v: dict) -> list[tuple[str, str]]:
        a, ui = v["ansi"], v["ui"]
        bg, fg = v["background"], v["foreground"]
        return [
            # Surfaces
            ("--background-primary", bg),
            ("--background-primary-alt", ui["lineHighlight"]),
            ("--background-secondary", ui["surface"]),
            ("--background-secondary-alt", ui["surfaceRaised"]),
            ("--background-modifier-border", ui["border"]),
            ("--background-modifier-border-hover", ui["gutter"]),
            ("--background-modifier-border-focus", ui["accent"]),
            ("--background-modifier-hover", v["selection"]),
            ("--background-modifier-active-hover", v["selection"]),
            ("--titlebar-background", ui["surface"]),
            ("--titlebar-background-focused", ui["surfaceRaised"]),
            ("--titlebar-text-color", fg),
            ("--ribbon-background", ui["surface"]),
            ("--divider-color", ui["border"]),
            ("--scrollbar-thumb-bg", ui["border"]),
            ("--scrollbar-active-thumb-bg", ui["gutter"]),
            # Text. `gutter` and `gutterActive` are the two `ui` entries held to
            # AA as text, which is exactly what muted and faint body copy are —
            # so the muted tiers come from there rather than from a surface.
            ("--text-normal", fg),
            ("--text-muted", ui["gutterActive"]),
            ("--text-faint", ui["gutter"]),
            ("--text-on-accent", ui["onAccent"]),
            ("--text-error", c(v, "error")),
            ("--text-success", c(v, "added")),
            ("--text-warning", c(v, "warning")),
            ("--text-selection", v["selection"]),
            ("--text-highlight-bg", v["selection"]),
            ("--caret-color", v["cursor"]),
            ("--icon-color", ui["gutterActive"]),
            ("--icon-color-hover", fg),
            ("--icon-color-active", ui["accent"]),
            # Accent and links
            ("--interactive-accent", ui["accent"]),
            ("--interactive-accent-hover", a["brightMagenta"]),
            ("--interactive-normal", ui["surface"]),
            ("--interactive-hover", v["selection"]),
            ("--text-accent", ui["accent"]),
            ("--text-accent-hover", a["brightMagenta"]),
            ("--link-color", c(v, "type")),
            ("--link-color-hover", c(v, "namespace")),
            ("--link-external-color", c(v, "type")),
            ("--link-external-color-hover", c(v, "namespace")),
            ("--link-unresolved-color", c(v, "error")),
            # Blockquote. The bar is the accent so it reads as a quote at a
            # glance; the text is a muted tier because a quote is somebody
            # else's voice and should sit behind yours.
            ("--blockquote-border-color", ui["accent"]),
            ("--blockquote-color", ui["gutterActive"]),
            ("--hr-color", ui["border"]),
            # Code. `--code-*` are the Prism slots reading view paints with.
            #
            # The block keeps the note background instead of `surface`, which
            # costs a code block its outline against the note. Measured, not
            # guessed: `comment` and `punctuation` both resolve to `brightBlack`,
            # the slot that recedes and therefore already sits on the AA line at
            # 4.53 against `background` in the dark variant. Painting it on
            # `surface` instead spends that margin and lands at 4.15, under the
            # 4.5 floor the README promises. `lineHighlight` does not save it
            # either (4.21). The other way out would be a slot that clears 4.5
            # on `surface` in both variants, and the two that do — `gutter`
            # (4.35/4.47, so it does not) and `gutterActive` (7.11/10.04) —
            # fail for a different reason: `gutterActive` is the muted *body*
            # tier this file already spends on `--text-muted`, so comments
            # would come out louder than in every other port and `syntax`
            # would stop being one mapping across ports, which is the whole
            # reason that map exists. A block that reads is worth more than a
            # block that frames.
            ("--code-background", bg),
            ("--code-normal", fg),
            ("--code-comment", c(v, "comment")),
            ("--code-string", c(v, "string")),
            ("--code-keyword", c(v, "keyword")),
            ("--code-operator", c(v, "operator")),
            ("--code-punctuation", c(v, "punctuation")),
            ("--code-function", c(v, "function")),
            ("--code-property", c(v, "property")),
            ("--code-value", c(v, "number")),
            ("--code-tag", c(v, "tag")),
            ("--code-important", c(v, "keyword")),
            # Headings
            ("--h1-color", ui["accent"]),
            ("--h2-color", a["brightMagenta"]),
            # The ramp is a ramp of slots, not of code roles: an outline level
            # is not a diagnostic severity, and reading `info`/`type`/
            # `namespace` here would let a future remap of the `syntax` map
            # silently repaint a note's headings. h6 is the exception and takes
            # the role, because the reason it is last is exactly the reason
            # comments take that slot: it is the one whose job is to recede.
            ("--h3-color", a["blue"]),
            ("--h4-color", a["cyan"]),
            ("--h5-color", a["brightCyan"]),
            ("--h6-color", c(v, "comment")),
            # Tags
            ("--tag-color", ui["accent"]),
            ("--tag-background", ui["surface"]),
            ("--tag-color-hover", ui["onAccent"]),
            ("--tag-background-hover", ui["accent"]),
            # Checkboxes. A done item goes to a muted tier rather than staying
            # full-strength, so a list reads as what is left to do.
            ("--checkbox-color", ui["accent"]),
            ("--checkbox-color-hover", a["brightMagenta"]),
            ("--checkbox-border-color", ui["gutter"]),
            ("--checkbox-marker-color", ui["onAccent"]),
            ("--checklist-done-color", ui["gutter"]),
            # Tables
            ("--table-header-background", ui["surface"]),
            ("--table-row-alt-background", ui["lineHighlight"]),
            ("--table-border-color", ui["border"]),
        ]

    # Leaf classes only, one list per rule. The theme and `.cm-s-obsidian`
    # prefixes are attached to *every* selector when the rule is written out —
    # spelling a comma-separated group here instead would leave the second
    # selector unscoped, and a `.theme-light` colour applying under
    # `.theme-dark` is worse than no rule at all.
    def editor_rules(v: dict) -> list[tuple[list[str], str]]:
        ui = v["ui"]
        return [
            ([".cm-comment"], c(v, "comment")),
            ([".cm-string", ".cm-string-2"], c(v, "string")),
            ([".cm-keyword"], c(v, "keyword")),
            ([".cm-atom"], c(v, "boolean")),
            ([".cm-number"], c(v, "number")),
            # `.cm-def` marks a definition, and CodeMirror 5's stream modes put
            # it on `let x` as readily as on a function. It still takes
            # `function` rather than `variable`, because in this palette
            # `variable` resolves to `foreground`: mapping it there would paint
            # every definition as plain body text and erase the "something is
            # declared here" signal for functions too, to spare a variable a
            # colour it arguably should not have. Keeping `function` is the
            # cheaper error — a declaration reads as a declaration either way.
            ([".cm-def"], c(v, "function")),
            ([".cm-variable"], c(v, "variable")),
            ([".cm-variable-2", ".cm-property"], c(v, "property")),
            ([".cm-type"], c(v, "type")),
            ([".cm-tag"], c(v, "tag")),
            ([".cm-attribute"], c(v, "attribute")),
            ([".cm-operator"], c(v, "operator")),
            ([".cm-meta"], c(v, "namespace")),
            ([".cm-error"], c(v, "error")),
            # Markdown's own decorations, which live in the same tree.
            ([".cm-inline-code"], c(v, "property")),
            ([".cm-hashtag", ".cm-hashtag-begin", ".cm-hashtag-end"], ui["accent"]),
            ([".cm-quote"], ui["gutterActive"]),
            ([".cm-link", ".cm-hmd-internal-link"], c(v, "type")),
            ([".cm-url"], ui["gutter"]),
            # The `#` and `*` glyphs that stay visible while the cursor is in
            # the line. They are scaffolding, so they take the slot that
            # recedes.
            ([".cm-formatting"], c(v, "punctuation")),
            ([".cm-header-1"], ui["accent"]),
            ([".cm-header-2"], v["ansi"]["brightMagenta"]),
            ([".cm-header-3"], v["ansi"]["blue"]),
            ([".cm-header-4"], v["ansi"]["cyan"]),
            ([".cm-header-5"], v["ansi"]["brightCyan"]),
            ([".cm-header-6"], c(v, "comment")),
        ]

    def block(v: dict, theme: str) -> str:
        rows = "\n".join(f"  {name}: {value};" for name, value in variables(v))
        rules = "\n".join(
            "{} {{ color: {}; }}".format(
                ", ".join(f".{theme} .cm-s-obsidian {leaf}" for leaf in leaves),
                colour,
            )
            for leaves, colour in editor_rules(v)
        )
        return f"/* {v['name']} */\n.{theme} {{\n{rows}\n}}\n\n{rules}\n"

    dark, light = data["variants"]["dark"], data["variants"]["light"]
    return f"""/* Violeeter {data['version']} for Obsidian — {data['homepage']}
   Generated by build.py. Do not edit.

   Install: copy this file into `vault/.obsidian/snippets/`, then switch it on
   under Settings → Appearance → CSS snippets. Both variants are in here, so it
   follows Obsidian's own dark/light toggle without touching anything else. */

{block(dark, "theme-dark")}
{block(light, "theme-light")}"""


# Not every port is in here: both registries emit one file per variant, so a
# port that has to hold both variants in one file (`css`, `tailwind`,
# `obsidian`) is a function over the whole dataset called directly from
# `main()` instead.
EXPORTS = {
    "itermcolors": iterm,
    "toml": alacritty,
    "conf": kitty,
    "ghostty": ghostty,
    "json": windows_terminal,
    "wezterm.toml": wezterm,
    "slack.txt": slack,
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
    # Both variants in one file, like the stylesheet above and unlike the
    # per-variant exports — see `obsidian()` for why the registries do not fit.
    (DIST / "violeeter.obsidian.css").write_text(obsidian(data, syntax))
    stylesheet = css(data)
    (DIST / "violeeter.css").write_text(stylesheet)

    # The VS Code extension: a directory rather than a file, because that is the
    # unit `vsce package` takes. Publishing is `cd dist/vscode-extension &&
    # npx @vscode/vsce publish` — nothing in it is edited by hand.
    ext = DIST / "vscode-extension"
    for name, contents in vscode_extension(data, syntax).items():
        target = ext / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(contents)
    for asset, dest in ((ROOT / "assets/icon.png", "icon.png"),
                        (ROOT / "LICENSE", "LICENSE")):
        if not asset.is_file():
            raise SystemExit(f"missing {asset}, which the extension package needs")
        (ext / dest).write_bytes(asset.read_bytes())
    print(f"wrote {len(list(ext.rglob('*')))} paths to {ext}/")

    written = sorted(p.name for p in DIST.iterdir() if p.is_file())
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

        # The exports themselves, so the page can show what is in a file rather
        # than only naming it. Served from `docs/` because that is the only
        # directory GitHub Pages publishes; fetching them from raw.github
        # instead would put a second host between a reader and a colour they
        # can already see rendered above.
        page_dist = page / "dist"
        page_dist.mkdir(exist_ok=True)
        # Files only. The one directory in `dist/` is the VS Code extension,
        # which is a package to publish rather than a file to read, and the page
        # links it to the Marketplace instead of serving its parts.
        for item in DIST.iterdir():
            if item.is_file():
                (page_dist / item.name).write_bytes(item.read_bytes())
        print(f"wrote {page}/violeeter.css, violeeter.json and dist/ ({len(list(page_dist.iterdir()))} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
