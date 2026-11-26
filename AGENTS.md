# AGENTS.md — Glass geometry standard

Read `APPLE-GLASS-CURVATURE.md` and `README.md` before editing. This is an empirical local design contract, not Apple source. Treat observed raster data as evidence, not a proof of internal implementation.

## Non-negotiable implementation rules

- Two primitives, four named immutable presets. Use `glassPath(kind,width,height?)` in production. Toolbar height 36pt; action height 28pt; menu extent 18.32659689pt; dialog extent 39.774pt. Never silently compress geometry or stretch a complete path. Keep low-level research clamps separate from strict production use.
- Preserve canonical coefficients unless a new measured comparison supports changes. Keep material, shadows and content independent of the geometry. Do not interpret apparent edge brightness as shape.
- Document uncertainty, display scale, registration, threshold sensitivity, candidate residuals and actual serialized output. Preserve prior evidence. Publish material intermediate work products and actual rendered comparisons through available user-visible routes; if unsupported, provide a durable evidence bundle and disclose the limitation. Do not invent measurements or claim exact Apple recovery.
- The library is authoritative: edit `glass-curvature.js` and `guide.template.html`, then run `python3 build.py`. Never hand-edit the generated HTML. Keep Markdown and preset descriptions consistent.

## Validation and delivery

Run `node --test tests/geometry.test.cjs`, rebuild twice to check determinism, and run `python3 tests/browser_test.py` when Chromium and Playwright are available. Verify actual SVG path bounds, continuity at straight joins, width invariance, strict invalid-size rejection, legacy compatibility, browser controls and absence of runtime errors. New empirical claims need actual reference comparison, not only synthetic regression tests. Report tests run/skipped, limitations, changed files, and verified commit. Respect user scope and preserve unrelated changes; do not force-push.
