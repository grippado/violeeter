# Violeeter / Violeet brand identity

This document is the shared reference for the visual identity of **Violeeter**
and **Violeet**. Violeeter is the portable colour system; Violeet is the native
macOS terminal that ships with it. They are two expressions of the same idea:
make complex agent work feel visible, calm and unmistakably violet.

## Brand architecture

| Name | Role | Short description |
|---|---|---|
| **Violeet** | Product | A native macOS terminal for running several AI coding agents in tabs, with session state and permission requests visible in one board. |
| **Violeeter** | Visual system | A dark and light violet theme for terminals, editors and other developer tools. |
| **Violeet mark** | Shared symbol | The abstract violet ribbon used by both projects. |

Use **Violeet** when talking about the application. Use **Violeeter** when
talking about the palette, its ports, or the theme as a standalone artifact.
When the two appear together, say: “Violeet ships with Violeeter.”

## Personality

The identity should feel:

- **Focused** — it gives a busy technical surface a clear centre.
- **Warm** — violet is expressive, not the cold blue-black default of developer tooling.
- **Precise** — contrast is measured, semantic roles are mapped once, and exports do not drift.
- **Alive** — the gradient and the flowing mark suggest activity without becoming noisy.

Avoid language or visuals that make the brand feel corporate, aggressive,
cyberpunk, or excessively ornamental. The product is serious about the work,
not solemn about itself.

## Logo and mark

The mark is a flowing, abstract **V** rendered as a single ribbon. It is
available in theme-aware light and dark cuts:

- `violeeter-dark.svg` / `violeet-dark.svg`: pale mark on the violet gradient.
- `violeeter-light.svg` / `violeet-light.svg`: dark mark on the violet gradient.

The gradient runs from `#C78BF7` (violet) to `#7FAEFF` (blue-violet). The SVG
artwork is the source of truth; do not redraw it with CSS, crop it, or apply a
second border radius. When it is placed in a UI, use `object-fit: contain` and
let the artwork retain its own frame.

The symbol is a logo mark, not a font glyph. The wordmark is set separately.

## Wordmark typography

The official wordmark typeface is **[Akaya Telivigala](https://fonts.google.com/specimen/Akaya+Telivigala?preview.lang=shu_Latn)**, from Google Fonts.

- Use it for the names `Violeet` and `Violeeter` when they function as a logo or brand signature.
- Use the regular face as supplied; do not simulate a heavier weight or distort the letters.
- Keep the spelling and casing exactly as `Violeet` and `Violeeter`.
- Do not use Akaya Telivigala for long passages, interface labels, or code.

Supporting typography remains deliberately quiet:

- **Interface and prose:** the system sans stack (`ui-sans-serif`, `-apple-system`, `Segoe UI`, `system-ui`).
- **Code, paths and configuration:** the system monospace stack (`ui-monospace`, `SF Mono`, Menlo, Consolas, monospace).

On the project pages, load the font from Google Fonts only for the `.wordmark`
or `.brand-name` element. If remote fonts are unavailable, the wordmark may
fall back to a cursive or system fallback; the mark must remain usable on its
own.

## Colour

Violeeter is built around a violet ground rather than pure black or white.
The two primary surfaces are:

| Variant | Background | Foreground | Accent |
|---|---|---|---|
| Dark | `#24203F` | `#D9D6EC` | `#C78BF7` |
| Light | `#FAF8FE` | `#2A2440` | `#7C3AED` |

The complete palette lives in [`violeeter.json`](../violeeter.json), the only
file that should be edited by hand. `dist/` is generated from it. Use semantic
roles (`background`, `foreground`, `accent`, `selection`, `error`, `warning`)
instead of picking a new violet for a one-off component.

Every colour that carries text is checked against WCAG AA by `python3 build.py
--check`. Preserve that check when adding a new export or surface.

## Composition and use

- Prefer the mark with generous space around it; never squeeze it into a busy panel.
- Keep the mark and wordmark aligned as one lockup, with the mark optically leading the name.
- Use the dark or light cut that creates the clearest relationship with its background.
- Do not recolour the mark, add effects, rotate it, stretch it, or place it on a competing gradient.
- For small UI sizes, the mark may stand alone; do not force the wordmark below a size where Akaya loses clarity.
- In text, link the complete lockup as one target when it acts as home navigation.

## Repository map

| Asset or source | Purpose |
|---|---|
| `violeeter.json` | Palette, variants and semantic syntax mapping. |
| `build.py` | Contrast checker and generators for every port. |
| `docs/violeeter-*.svg` | Violeeter logo cuts. |
| `docs/violeet-*.svg` | Violeet product logo cuts. |
| `dist/` | Generated editor and terminal exports. |
| `www/personal/violeet` | Product repository and consumer of the theme. |

When a visual decision changes, update this document and the relevant source
asset or generator in the same change. A theme export is not complete if it
has a different interpretation of the brand.
