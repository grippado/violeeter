# Violeeter

A violet theme for everything. Dark and light, every colour verified against WCAG AA.

Two themes, **Violeeter Dark** and **Violeeter Light**, generated from one
palette file. `Cmd+K Cmd+T` (`Ctrl+K Ctrl+T` on Windows and Linux) to switch.

![Violeeter Dark](https://raw.githubusercontent.com/grippado/violeeter/main/assets/screenshot-dark.png)

![Violeeter Light](https://raw.githubusercontent.com/grippado/violeeter/main/assets/screenshot-light.png)

## Every colour is checked

Every colour that carries text clears WCAG AA (4.5:1) against the background it
is drawn on, in both variants, and the build fails if one does not. That
includes the line number column, which is text somebody reads while looking for
a line, and colour 7 in the light variant, which is the default foreground of a
large share of terminal programs.

## The same theme everywhere else

This extension is one port of a palette that also ships for Neovim, Zed,
Terminal.app, iTerm2, Alacritty, Kitty, Ghostty, WezTerm, Windows Terminal,
btop, CSS and Tailwind.
Every port resolves the same role-to-slot mapping, so a string is the same green
in your editor and in the terminal beside it.

The full set, and the palette itself: <https://grippado.github.io/violeeter/>

## Licence

MIT. Take it, port it, change it.
