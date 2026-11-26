# Apple-style glass curvature — Flowform implementation standard

**Status:** empirical reconstruction, revision 2.0. Applies to the observed Freeform toolbar/zoom pills, context menus, Empty Scene dialog and its action buttons. This is a local design-system contract, not an official Apple specification or recovered Apple source. All dimensions below are logical points (CSS px in a 1:1 logical-coordinate web UI). The references were captured at 2× Retina.

## 1. Mandatory geometry tokens

Two mathematical families, four component presets. All dimensions are logical points (CSS px at 1:1). The fixed-height rule is **per pill class**, not universal.

| Preset | Family | Width | Height | Transition extent per corner/end | Minimum geometry |
|---|---|---|---|---|---|
| `toolbar` | Continuous capsule | Content-sized | **36 pt fixed** | 21.12588 pt | W ≥ 42.25176 pt |
| `actionButton` | Continuous capsule | Layout/content-sized | **28 pt fixed** | 16.43124 pt | W ≥ 32.86248 pt |
| `menu` | Continuous rounded rectangle | Content-sized | Content-sized | 18.32659689 pt | W,H ≥ 36.65319378 pt |
| `dialog` | Continuous rounded rectangle | Layout/content-sized | Layout/content-sized | 39.774 pt | W,H ≥ 79.548 pt |

The dialog is an empirical scale-only transfer of the menu profile (about 2.17×). It uses the same normalized double-cubic coefficients. A specialized fit improves RMS by only about 0.02 physical px for the tested capture, so revision 2.0 favors reuse. Constant dialog extent across other sizes is a local implementation policy, not yet a cross-dialog empirical finding. The observed dialog is 260×172 pt; its action buttons are 228×28 pt. Do not infer a universal dialog size or a universal pill height. The cap extent is 1.17366 × half-height, with six cubic segments per quarter. Menus/dialogs use two cubics per corner. The low-level generators retain their research clamps, but the strict `glassPath` entry point rejects undersized production geometry rather than silently compressing corners.

## 2. Do / don't — toolbar and action pills

| DO | DON'T |
|---|---|
| Select toolbar (36pt) or actionButton (28pt), then lock height/min-height/max-height. | Apply 36pt to all Apple pills, or derive height from text, width, or icon count. |
| Change width only; maintain the class-specific end-cap extent and vertical centering. | Stretch a static SVG or change height during width animation. |
| Use measured cap geometry and enforce minimum width. | Substitute `border-radius:9999px`, compress caps, or overlap end caps. |
| Keep shape, fill, inner stroke, blur and shadow independently controlled. | Compensate for mismatched geometry with an outward border or stronger glow. |
| Reuse the same normalized cap profile for both classes. | Introduce a new curve merely because a button has a different fixed height. |

## 3. Do / don't — menus and dialogs

| DO | DON'T |
|---|---|
| Choose fixed extent by class: menu 18.327pt; dialog 39.774pt. | Use the menu extent on the dialog, double it blindly, or derive radius from dimensions. |
| Extend straight edges independently as width/height change. | Stretch a complete static SVG to a new aspect ratio. |
| Reflect/rotate the symmetric two-cubic corner. | Tune each corner independently based on highlights or backdrop. |
| Keep the tangent and zero-curvature joins; fit uncontaminated reference boundaries. | Use circular corners, trace shadows or translucent color bleed as geometry. |
| Use the 260×172pt dialog only as a reference; validate new size classes before declaring equivalence. | Claim the exact proprietary Apple geometry or universal dialog size from one capture. |

## 4. Glass composition and responsive behavior

Use a shadow-bearing outer wrapper, an independently clipped material layer, and an unclipped content layer where appropriate. All layers share the same border box. Apply blur, fill, subtle highlights and any inner border inside the material geometry. If using a shape-following shadow, derive it from the same path and render it outside the clip; a conventional rectangular box-shadow does not follow an arbitrary path. Do not add a rounded CSS border beneath the SVG mask. Avoid clipping focus rings, popovers or overflow controls unintentionally. The material examples in the HTML are illustrative, not measured blur or refraction constants.

Recompute the path using actual border-box width and height when layout changes. Use horizontal writing mode or explicitly map logical axes to physical coordinates. Do not interpolate between arbitrary path strings for animation; animate dimensions and recompute geometry. For a pill, animate width only within its chosen height class. Never apply an anisotropic transform to the whole geometry. At 2×, the 36pt box is 72px; do not set CSS height to 72px in a logical-coordinate renderer.

```css
.glass-shell { position: relative; isolation: isolate; box-sizing: border-box; }
.glass-shell.pill { height: 36px; min-height: 36px; max-height: 36px;
  min-width: 42.25176px; flex-shrink: 0; }
.glass-material { position: absolute; inset: 0; box-sizing: border-box;
  background: rgba(64,64,64,.78); backdrop-filter: blur(16px); /* illustrative material */ }
.glass-content { position: relative; z-index: 1; }
.glass-shell.actionButton { height: 28px; min-height: 28px; max-height: 28px; min-width: 32.86248px; flex-shrink: 0; }
.pill .glass-content, .actionButton .glass-content { height: 100%; display: flex; align-items: center; }
```

## 5. Canonical implementation

Use the dependency-free [glass-curvature.js](glass-curvature.js) as the single source of truth. The production API is `glassPath(kind, width, height?)`; legacy `fixedPillPath` and `attachGlassShape(element, "pill")` still select the toolbar. `menuPath` and `applePillPath` are lower-level research primitives and retain their original coefficients and clamp behavior. `attachGlassShape` observes a border box, requires the selected geometry to fit, marks failures via `data-geometry-error`, and hides invalid material instead of rendering a rectangular fallback. Invoke the cleanup on unmount. Use `box-sizing:border-box` and horizontal writing mode.

```javascript
const toolbar = glassPath('toolbar', 288);        // 36pt
const action = glassPath('actionButton', 228);     // 28pt
const menu = glassPath('menu', 160, 224);
const dialog = glassPath('dialog', 260, 172);
const detach = attachGlassShape(materialElement, 'dialog');
// detach() on unmount
```

The standalone HTML includes this exact library, not a separately maintained approximation. Rebuild it with `python3 build.py`; run `node --test tests/geometry.test.cjs` for dependency-free regression checks. Optional Chromium interaction tests are in `tests/browser_test.py`.

## 6. Acceptance and evidence

- Inspect at native 2× resolution on dark gray and black backgrounds; compare registered silhouettes, not just bounding boxes.
- For pills, test at the observed nominal widths of 74, 258 and 288pt, all at 36pt height; action buttons at 228×28pt; menus at 160×224 and 185×519pt; dialog at 260×172pt.
- Overlay clean corner profiles at identical physical scale; vary segmentation thresholds and report residuals. Avoid morphological smoothing that changes the corner shape.
- Use the actual serialized path and rasterize it; inspect continuity, bounds, clipping and content alignment. Check width changes preserve cap geometry and menu corner extent.
- Regression targets for these particular captures: prior pill model RMS 0.0839/0.0846 physical px on the long/short toolbar holdouts, versus 0.1765/0.1779 for circular caps. Refined menu fit RMS 0.0429 physical px on seven clean corners; exported SVG raster RMS 0.0739/0.0801 px for compact/tall menus. These are empirical results at the recorded thresholds, not universal acceptance tolerances. For new captures establish their own baseline and uncertainty.
- Dialog capture: scale-only menu profile RMS 0.0904 physical px versus circular 0.3878 and independent refit 0.0705 (raw intensity threshold 40). Action buttons at 50% contrast: shared continuous profile 0.1255 / 0.1393 px versus circular 0.1725 / 0.1828 px. These are earlier analytical fits, not fresh exported-path raster measurements. See the embedded historical plots in the HTML.
- Do not claim exact native source recovery. The apparent boundary depends on contrast, antialiasing, material and measurement convention. The pill's cubic approximation preserves the zero-curvature horizontal join but does not assert exact G2 at every internal subdivision. Menu coefficients are one empirically supported fit; exact endpoint extent is weakly identifiable from raster evidence.

## 7. Agent review gate

Before accepting a glass component, verify: correct family selected; fixed class-specific pill height (36pt toolbar or 28pt action); invariant cap or menu extent; no anisotropic scaling; no accidental outer border expansion; material separated from geometry; actual runtime/rendered output inspected; limitations disclosed. If the design departs from these rules, document the reason and obtain a new reference instead of silently changing the shared primitive.

**Geometry defines the vessel. Material defines its appearance. Content defines width or rectangular vessel dimensions, never a pill’s class height or a rectangular vessel’s corner extent.**
