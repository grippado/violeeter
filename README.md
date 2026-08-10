<div align="center">

# Violeeter

**A violet theme for everything.**

Dark and light, for your editor and your terminal.
Every colour that can carry text is verified against WCAG AA: measured, not guessed.

**[grippado.github.io/violeeter →](https://grippado.github.io/violeeter/)**

[![VS Code Marketplace](https://img.shields.io/visual-studio-marketplace/v/grippado.violeeter?label=VS%20Code%20Marketplace&color=6E56CF)](https://marketplace.visualstudio.com/items?itemName=grippado.violeeter)

The shared visual system, logo usage and typography are documented in
[`docs/BRAND_IDENTITY.md`](docs/BRAND_IDENTITY.md). The logo wordmark uses
[Akaya Telivigala](https://fonts.google.com/specimen/Akaya+Telivigala?preview.lang=shu_Latn); the theme itself uses system sans and monospace fonts for readability.

</div>

---

## Install

Grab one file from [`dist/`](dist/), or clone and take what you need:

```sh
git clone https://github.com/grippado/violeeter
cd violeeter/dist
```

| Where | File | How |
|---|---|---|
| **VS Code** | [Marketplace](https://marketplace.visualstudio.com/items?itemName=grippado.violeeter) | install `grippado.violeeter`, or build the `.vsix` from `dist/vscode-extension/` |
| **Neovim** | `violeeter-{dark,light}.nvim.lua` | drop in `~/.config/nvim/colors/violeeter-dark.lua`, then `:colorscheme violeeter-dark` |
| **Zed** | `violeeter-{dark,light}.zed.json` | copy into `~/.config/zed/themes/` |
| **iTerm2** | `violeeter-{dark,light}.itermcolors` | double-click, then Settings → Profiles → Colors → Presets |
| **Alacritty** | `violeeter-{dark,light}.toml` | `import` it from `alacritty.toml` |
| **Kitty** | `violeeter-{dark,light}.conf` | `include violeeter-dark.conf` in `kitty.conf` |
| **Ghostty** | `violeeter-{dark,light}.ghostty` | paste into your config |
| **WezTerm** | `violeeter-{dark,light}.wezterm.toml` | drop in `~/.config/wezterm/colors/` |
| **Windows Terminal** | `violeeter-{dark,light}.json` | add to `schemes` in `settings.json` |
| **Web** | `violeeter.css` | custom properties, light and dark |
| **Tailwind** | `violeeter.tailwind.js` | merge into `tailwind.config.js` |

The VS Code entry is a whole publishable extension — manifest, both themes,
icon and readme — generated into `dist/vscode-extension/` by the same build.
Its `package.json` takes the version, name, description and banner colour from
`violeeter.json`, so there is no second place for any of them to drift, and its
`themes/` are byte-identical to the `.vscode.json` exports beside them.

The Neovim colorscheme sets highlight groups directly (no plugin manager, no
dependency, treesitter groups included) and sets `terminal_color_*` so
`:terminal` matches the buffer beside it.

## The palette

| | Background | Worst text contrast | WCAG AA |
|---|---|---|---|
| **Violeeter Dark** | `#24203F` | 4.53 | pass |
| **Violeeter Light** | `#FAF8FE` | 4.84 | pass |

The dark variant is built from one base. Two things follow from a violet ground
rather than a black one, and neither is optional: **blue has to move**, because
the default terminal blue sits a few degrees away and the two stop separating;
and **neutral grey reads yellow** against a cold ground, so the foreground
carries a trace of the same hue instead of being a true grey.

The light variant is **not** the dark one flipped. Inverting lightness gives
colours that are correct in theory and pastels on white in practice. Each one
was re-picked at a luminance that reads on a pale ground, with the hue kept.

## Contrast is checked, not claimed

```sh
python3 build.py --check
```

Measures all thirty-six values against their own background and exits non-zero
if any colour that can carry text drops under 4.5:1.

Nothing is exempt, and two colours were changed to keep it that way.

`white` and `brightWhite` in the light variant used to be exempt, on the
reasoning that they mean "the palest thing here" and so are surfaces. That is
right about the name and wrong about the use: colour 7 is the default foreground
of a large share of terminal programs. Under btop they measured 1.61:1 and the
memory labels were not dim, they were absent.

`brightBlack` measured **2.07** in the terminal this palette grew up in, and that
slot is where nearly every syntax highlighter puts *comments*. Shipping it meant
shipping unreadable comments.

The checker also walks the `ui` block now. It used to stop at the ANSI slots, so
`gutter`, which is the line number column and therefore text, shipped at 2.91
while the summary said PASS. A checker that measures the colours you remembered
to list measures your memory.

## Porting it somewhere else

Nothing in `dist/` is written by hand. A port is a function that takes the
palette and returns a string:

```python
def my_editor(v, syntax):
    return f"background = {v['background']}"
```

Add it to `EXPORTS` (or `EDITOR_EXPORTS`, which also receives the syntax
mapping), run `python3 build.py`, open a pull request.

`violeeter.json` is the only file anyone edits. Two things live in it:

- **the palette**, per variant
- **`syntax`**, the mapping from semantic role to palette slot: `comment →
  brightBlack`, `string → green`, `keyword → magenta`

That mapping is why a string is the same green in VS Code, Neovim and Zed. A
port that re-picks colours locally is how a theme ends up subtly different in
every editor, and it is the one thing a pull request here will be asked to
change.

## Publishing the VS Code extension

`python3 build.py` writes the package; publishing only uploads it. Bump
`version` in `violeeter.json` and rebuild — the manifest follows, and there is
no second version to remember.

[Open VSX](https://open-vsx.org) (VSCodium, Cursor, Windsurf, Gitpod). The
token comes from open-vsx.org → Log in with GitHub → Settings → Access Tokens,
and the namespace has to match `publisher` in the generated manifest:

```sh
python3 build.py
cd dist/vscode-extension
npx ovsx create-namespace grippado -p "$OVSX_PAT"   # once, ever
npx ovsx publish -p "$OVSX_PAT"
```

The Visual Studio Marketplace, which needs an Azure DevOps organisation and a
personal access token scoped to *Marketplace → Manage*, issued for **all
accessible organisations**:

```sh
cd dist/vscode-extension
npx @vscode/vsce publish -p "$VSCE_PAT"
```

`npx @vscode/vsce package` writes a `.vsix` without publishing anything, which
is also how you install the theme on a machine without either registry:
`code --install-extension violeeter-<version>.vsix`.

## Licence

MIT. Take it, port it, change it.

It is the palette [Violeet](https://github.com/grippado/violeet) ships with.
