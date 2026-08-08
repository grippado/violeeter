<div align="center">

# Violeeter

**A violet theme for everything.**

Dark and light, for your editor and your terminal.
Every colour that can carry text is verified against WCAG AA — measured, not guessed.

**[grippado.github.io/violeeter →](https://grippado.github.io/violeeter/)**

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
| **VS Code** | `violeeter-{dark,light}.vscode.json` | copy into your extension's `themes/`, or `.vscode/` for a workspace |
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

The Neovim colorscheme sets highlight groups directly — no plugin manager, no
dependency, treesitter groups included — and sets `terminal_color_*` so
`:terminal` matches the buffer beside it.

## The palette

| | Background | Worst text contrast | WCAG AA |
|---|---|---|---|
| **Violeeter Dark** | `#24203F` | 4.53 | pass |
| **Violeeter Light** | `#FAF8FE` | 5.06 | pass |

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

Two slots are exempt, and only in the light variant: `white` and `brightWhite`
mean "the palest thing here", which on a pale ground is a surface you fill with
rather than something you write with. Holding them to a text ratio would mean
darkening white until it stopped being white.

One colour was changed rather than inherited. `brightBlack` measured **2.07** in
the terminal this palette grew up in, and that slot is where nearly every
syntax highlighter puts *comments*. Shipping it meant shipping unreadable
comments. It is `#8B84BC`, the smallest step that clears the floor with the hue
intact.

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
- **`syntax`**, the mapping from semantic role to palette slot — `comment →
  brightBlack`, `string → green`, `keyword → magenta`

That mapping is why a string is the same green in VS Code, Neovim and Zed. A
port that re-picks colours locally is how a theme ends up subtly different in
every editor, and it is the one thing a pull request here will be asked to
change.

## Licence

MIT. Take it, port it, change it.

It is the palette [Violeet](https://github.com/grippado/violeet) ships with.
