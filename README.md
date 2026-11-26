# Apple Glass Curvature Guide · revision 2.0

An empirical, independent geometry reconstruction for Flowform and other logical-coordinate UI renderers. Not Apple source or an official specification.

- [Interactive offline guide](apple-glass-curvature.html): open locally in a browser.
- [Instructional standard](APPLE-GLASS-CURVATURE.md)
- [Geometry library](glass-curvature.js)
- [Agent instructions](AGENTS.md)

Two curve families, four presets: toolbar (36pt), actionButton (28pt), menu (18.32659689pt extent), dialog (39.774pt extent). The dialog preset is derived from a single capture; other dialog sizes need validation.

```sh
python3 build.py
node --test tests/geometry.test.cjs
```

Optional actual browser checks: `python3 -m pip install playwright`, install Chromium (or set `CHROMIUM_PATH` to a compatible executable), then `python3 tests/browser_test.py`. The build uses no absolute paths and needs no network or external Python packages. `evidence/` contains prior measurement plots (dialog/action images reduced for display), not fresh measurements or full source screenshots.
