# Apple-style glass curvature — Flowform implementation standard

**Status:** empirical reconstruction, revision 1.0. Applies to the observed Freeform toolbar/zoom pills and context menus. This is a local design-system contract, not an official Apple specification or recovered Apple source. All dimensions below are logical points (CSS px in a 1:1 logical-coordinate web UI). The references were captured at 2× Retina.

## 1. Mandatory geometry tokens

| Property | Pill family | Menu family |
|---|---|---|
| Height | **36 pt fixed** | Intrinsic content height |
| Width | Intrinsic content width | Intrinsic content width |
| Corner construction | Symmetric continuous end caps, six cubics per quarter | Symmetric two-cubic G2 corner |
| Horizontal transition extent | 21.12588 pt per end (36 × 0.58683) | 18.32659689 pt per corner, fixed |
| Minimum geometric width | 42.25176 pt; actual controls require more | 36.65319378 pt for full-size corners |
| Minimum geometric height | 36 pt | 36.65319378 pt for full-size corners |
| Straight-edge join | Zero curvature at horizontal seam | Zero curvature at both straight seams |
| SVG cubic segments | 24 | 8 |

Pill height is a hard requirement for this component family. Three different-width references agreed at approximately 72 physical pixels in height. The width may change without altering either cap or vertical metrics. Other Apple control families or display settings are not established by these captures. Menus retain their corner extent as their content changes. For menus too small to fit both full corners, use a different component or explicitly authorize the supplied geometric clamp; do not silently treat the clamp as an Apple rule.

## 2. Do / don't — pills

| DO | DON'T |
|---|---|
| Set `height`, `min-height` and `max-height` to 36px; use `box-sizing: border-box`. | Derive height from text, zoom percentage, padding, icon count or container width. |
| Change only width as controls are added or removed. Keep vertical centering stable. | Stretch a static SVG viewBox to fit different aspect ratios. |
| Use the measured end-cap path; maintain the 21.126pt horizontal shoulder on both ends. | Substitute `border-radius: 9999px`, a semicircle, a generic squircle or elliptical border radius. |
| Enforce minimum width before drawing; choose an overflow or alternate layout if content does not fit. | Compress or overlap caps to fit a too-narrow control. |
| Use one primitive for zoom, creation, share and comparable toolbar modules. | Tune each width's corner curvature independently. |
| Keep material highlights, stroke and shadow independent of silhouette. | Compensate for a mismatched curve by increasing blur or outline thickness. |

## 3. Do / don't — menus

| DO | DON'T |
|---|---|
| Preserve the fixed 18.3266pt corner extent and the fitted tangent/midpoint coefficients. | Use a percentage radius that grows with menu width or height. |
| Add/remove rows or change width by extending straight edges only. | Scale an entire static rounded-rectangle SVG to a new aspect ratio. |
| Use the same reflected/rotated corner geometry at all four corners. | Adjust corners independently to match highlights on a particular backdrop. |
| Maintain a smooth tangent and zero curvature at joins to straight edges; use the symmetric cubic pair. | Substitute a circular arc or one cubic without validating its residuals. |
| Separate the clipping shape from padding, separators, typography and content layout. | Allow border width, a pseudo-element or blur to alter the intended outer geometry. |
| Fit on uncontaminated reference edges; reserve complex backdrops for holdout validation. | Trace color bleed, canvas dots, shadows or highlights as if they were geometry. |

## 4. Glass composition and responsive behavior

Use a shadow-bearing outer wrapper, an independently clipped material layer, and an unclipped content layer where appropriate. All layers share the same border box. Apply blur, fill, subtle highlights and any inner border inside the material geometry. If using a shape-following shadow, derive it from the same path and render it outside the clip; a conventional rectangular box-shadow does not follow an arbitrary path. Do not add a rounded CSS border beneath the SVG mask. Avoid clipping focus rings, popovers or overflow controls unintentionally. The material examples in the HTML are illustrative, not measured blur or refraction constants.

Recompute the path using actual border-box width and height when layout changes. Use horizontal writing mode or explicitly map logical axes to physical coordinates. Do not interpolate between arbitrary path strings for animation; animate dimensions and recompute geometry. For a pill, animate width only. Never apply an anisotropic transform to the whole geometry. At 2×, the 36pt box is 72px; do not set CSS height to 72px in a logical-coordinate renderer.

```css
.glass-shell { position: relative; isolation: isolate; box-sizing: border-box; }
.glass-shell.pill { height: 36px; min-height: 36px; max-height: 36px;
  min-width: 42.25176px; flex-shrink: 0; }
.glass-material { position: absolute; inset: 0; box-sizing: border-box;
  background: rgba(64,64,64,.78); backdrop-filter: blur(16px); /* illustrative material */ }
.glass-content { position: relative; z-index: 1; }
.pill .glass-content { height: 100%; display: flex; align-items: center; }
```

## 5. Canonical implementation

The following code uses the previously validated path coefficients. `fixedPillPath` is the production entry point for pills; `applePillPath` is a lower-level mathematical function retained for research and counterexamples. `menuPath` defaults to the fixed menu extent. Its clamp prevents self-intersection when explicitly used with undersized dimensions, but the recommended layout policy is to keep full-size corners. Use `attachGlassShape(materialElement, "pill" | "menu")`; invoke the returned cleanup on unmount. The helper flags invalid pill dimensions with `data-geometry-error`; treat that as a layout failure, not a reason to ship a rectangular fallback.

```javascript
// Freeform menu corner — empirical fit to two 2x screenshots.
// All dimensions are CSS pixels / logical points.
const MENU_CORNER = Object.freeze({
  extent: 18.32659689,
  tangent: 0.59666659,
  midpoint: 0.19124066
});

function menuPath(width, height, extent = MENU_CORNER.extent) {
  if (![width,height,extent].every(Number.isFinite) ||
      width <= 0 || height <= 0 || extent < 0) {
    throw new RangeError("Invalid menu dimensions");
  }
  const e = Math.min(extent, width/2, height/2);
  const a = MENU_CORNER.tangent, d = MENU_CORNER.midpoint;
  const f = n => String(Number(n.toFixed(5)));
  // One canonical corner, traveling from the left edge to the top edge.
  const corner = [
    [[0,a],[0,2*d],[d,d]],
    [[2*d,0],[a,0],[1,0]]
  ];
  function turn(transform) {
    return corner.map(segment =>
      "C" + segment.map(([x,y]) =>
        transform(x*e,y*e).map(f).join(" ")
      ).join(" ")
    ).join(" ");
  }
  return [
    `M0 ${f(e)}`,
    turn((x,y)=>[x,y]),
    `H${f(width-e)}`,
    turn((x,y)=>[width-y,x]),
    `V${f(height-e)}`,
    turn((x,y)=>[width-x,height-y]),
    `H${f(e)}`,
    turn((x,y)=>[y,height-x]),
    "Z"
  ].join(" ");
}


// Apple-style continuous pill, fitted to the supplied screenshot.
// Dimensions are CSS pixels. The result is an SVG path in the same units.
const CAP = [
  [
    [
      0.0,
      0.899515
    ],
    [
      0.01816,
      0.797615
    ],
    [
      0.048609,
      0.700336
    ]
  ],
  [
    [
      0.079059,
      0.603057
    ],
    [
      0.122071,
      0.510473
    ],
    [
      0.176368,
      0.427743
    ]
  ],
  [
    [
      0.230664,
      0.345013
    ],
    [
      0.296517,
      0.272211
    ],
    [
      0.373145,
      0.212544
    ]
  ],
  [
    [
      0.449773,
      0.152878
    ],
    [
      0.537448,
      0.106419
    ],
    [
      0.631793,
      0.073346
    ]
  ],
  [
    [
      0.726138,
      0.040273
    ],
    [
      0.827425,
      0.020659
    ],
    [
      0.923586,
      0.010572
    ]
  ],
  [
    [
      1.02438,
      0.0
    ],
    [
      1.111056,
      0.0
    ],
    [
      1.17366,
      0.0
    ]
  ]
];
const EXTENT = 1.173660;

function applePillPath(width, height) {
  if (!(Number.isFinite(width) && Number.isFinite(height) &&
        width > 0 && height > 0)) throw new RangeError("Positive finite dimensions required");
  const r = height / 2;
  const sx = Math.min(r, width / (2 * EXTENT));
  const segments = CAP.map((c, i) => [
    i ? CAP[i-1][2] : [0, 1], ...c
  ]);
  const f = n => String(Number(n.toFixed(5)));
  function quarter(flipX, flipY, reverse) {
    const cs = reverse ? [...segments].reverse() : segments;
    return cs.map(c => {
      const pts = reverse ? [c[2],c[1],c[0]] : c.slice(1);
      return 'C' + pts.map(([x,y]) => {
        x *= sx; y *= r;
        return f(flipX ? width-x : x) + ' ' + f(flipY ? height-y : y);
      }).join(' ');
    }).join(' ');
  }
  return `M0 ${f(r)} ` + quarter(false,false,false)
    + ` H${f(width-EXTENT*sx)} ` + quarter(true,false,true)
    + ' ' + quarter(true,true,false)
    + ` H${f(EXTENT*sx)} ` + quarter(false,true,true) + ' Z';
}


// Flowform production contract: width adapts, pill height never does.
const PILL_HEIGHT = 36;
const PILL_MIN_WIDTH = PILL_HEIGHT * EXTENT;
function fixedPillPath(width) {
  if (!Number.isFinite(width) || width < PILL_MIN_WIDTH)
    throw new RangeError("Pill is too narrow for its uncompressed end caps");
  return applePillPath(width, PILL_HEIGHT);
}
// Observe an isolated material layer, in horizontal writing mode.
function attachGlassShape(element, kind) {
  if (!['menu','pill'].includes(kind)) throw new RangeError('Unknown shape');
  const update = (entries) => {
    const box = entries?.[0]?.borderBoxSize;
    const size = Array.isArray(box) ? box[0] : box;
    const w = size?.inlineSize ?? element.offsetWidth;
    const h = size?.blockSize ?? element.offsetHeight;
    if (w <= 0 || h <= 0) return;
    if (kind === 'pill' && (Math.abs(h-PILL_HEIGHT)>0.01 || w<PILL_MIN_WIDTH)) {
      element.dataset.geometryError = 'Invalid fixed-height pill dimensions';
      element.style.clipPath = '';
      return;
    }
    delete element.dataset.geometryError;
    element.style.clipPath = `path("${kind==='pill'?fixedPillPath(w):menuPath(w,h)}")`;
  };
  const observer = new ResizeObserver(update);
  observer.observe(element,{box:'border-box'});
  update();
  return () => observer.disconnect();
}

```

## 6. Acceptance and evidence

- Inspect at native 2× resolution on dark gray and black backgrounds; compare registered silhouettes, not just bounding boxes.
- For pills, test at the observed nominal widths of 74, 258 and 288pt, all at 36pt height; for menus, test 160×224 and 185×519pt.
- Overlay clean corner profiles at identical physical scale; vary segmentation thresholds and report residuals. Avoid morphological smoothing that changes the corner shape.
- Use the actual serialized path and rasterize it; inspect continuity, bounds, clipping and content alignment. Check width changes preserve cap geometry and menu corner extent.
- Regression targets for these particular captures: prior pill model RMS 0.0839/0.0846 physical px on the long/short toolbar holdouts, versus 0.1765/0.1779 for circular caps. Refined menu fit RMS 0.0429 physical px on seven clean corners; exported SVG raster RMS 0.0739/0.0801 px for compact/tall menus. These are empirical results at the recorded thresholds, not universal acceptance tolerances. For new captures establish their own baseline and uncertainty.
- Do not claim exact native source recovery. The apparent boundary depends on contrast, antialiasing, material and measurement convention. The pill's cubic approximation preserves the zero-curvature horizontal join but does not assert exact G2 at every internal subdivision. Menu coefficients are one empirically supported fit; exact endpoint extent is weakly identifiable from raster evidence.

## 7. Agent review gate

Before accepting a glass component, verify: correct family selected; fixed 36pt pill height; invariant cap or menu extent; no anisotropic scaling; no accidental outer border expansion; material separated from geometry; actual runtime/rendered output inspected; limitations disclosed. If the design departs from these rules, document the reason and obtain a new reference instead of silently changing the shared primitive.

**Geometry defines the vessel. Material defines its appearance. Content defines width or menu height, never pill height or corner curvature.**
