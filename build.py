from pathlib import Path
import base64, re, json
root=Path('/mnt/data'); out=root/'apple-glass-curvature-guide'
menu=(root/'menu-curvature-analysis/menu-curvature.js').read_text().split('// Clip a material layer')[0]
pill=(root/'pill-curvature-model/apple-pill.js').read_text().split('if (typeof module')[0]
# Keep the validated coefficients, but enforce the fixed-height design-system contract.
js=menu+'\n'+pill+'''
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
'''
(out/'glass-curvature.js').write_text(js+'\nif(typeof module !== "undefined") module.exports={menuPath,applePillPath,fixedPillPath,attachGlassShape,MENU_CORNER,PILL_HEIGHT,PILL_MIN_WIDTH};\n')
md='''# Apple-style glass curvature — Flowform implementation standard

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
'''+js+'''
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
'''
(out/'APPLE-GLASS-CURVATURE.md').write_text(md)
# embed original analysis images as portable evidence
imgs={k:'data:image/png;base64,'+base64.b64encode((root/v).read_bytes()).decode() for k,v in {'pill':'pill-family-analysis/02-shared-model-validation.png','menu':'menu-curvature-analysis/04-export-validation.png'}.items()}
html='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Flowform | Glass geometry standard</title><style>
:root{color-scheme:dark;--bg:#171719;--panel:#202023;--line:#38383c;--fg:#ededf0;--muted:#a6a6ad;--ok:#80cbb0;--bad:#e6aa85;--guide:#70bbeb}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.6 -apple-system,BlinkMacSystemFont,system-ui,sans-serif}main{max-width:1150px;margin:auto;padding:44px 28px 80px}h1{font-size:clamp(32px,5vw,54px);letter-spacing:-.055em;line-height:1.06;margin:10px 0 16px;font-weight:650}h2{font-size:23px;letter-spacing:-.035em;margin:0 0 10px}h3{font-size:15px;margin:0 0 8px}p{margin:0 0 12px;color:var(--muted)}.eyebrow,.mono{font:11px/1.5 ui-monospace,SFMono-Regular,monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}header{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--line);padding-bottom:16px;margin-bottom:36px}header b{letter-spacing:.15em;font-size:12px}nav{display:flex;gap:20px;flex-wrap:wrap}a{color:var(--muted);text-decoration:none}a:hover{color:white}.intro{max-width:740px;font-size:16px}.tokens{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:24px 0 40px}.token{padding:18px;border:1px solid var(--line);border-radius:12px;background:var(--panel)}.token strong{display:block;font-size:28px;letter-spacing:-.045em;font-weight:600}.token small{color:var(--muted)}section{margin:44px 0;scroll-margin-top:20px}.lab{border:1px solid var(--line);border-radius:15px;overflow:hidden;background:var(--panel)}.controls{padding:16px 20px;display:flex;gap:22px;flex-wrap:wrap;align-items:center;border-bottom:1px solid var(--line)}label{display:flex;align-items:center;gap:10px;font-size:12px}input[type=range]{width:130px;accent-color:#b4c9d8}input[type=checkbox]{accent-color:#b4c9d8}output{font:12px ui-monospace,monospace;min-width:43px}select,button{font:inherit;color:var(--fg);background:#2b2b30;border:1px solid #49494f;border-radius:6px;padding:6px 10px}button{cursor:pointer}button:hover{background:#39393f}.pair{display:grid;grid-template-columns:1fr 1fr}.example{min-width:0;padding:20px}.example+.example{border-left:1px solid var(--line)}.good{color:var(--ok)}.bad{color:var(--bad)}.stage{height:160px;background:#1e1e1e;display:flex;align-items:center;justify-content:center;overflow:hidden;border:1px solid #2c2c30;border-radius:8px;margin:14px 0}.menu-stage{height:370px;align-items:center}.stage svg{max-width:100%;height:100%;width:100%;display:block}.note{font-size:12px;min-height:40px}.rules{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:14px}.rules>div{border:1px solid var(--line);border-radius:10px;padding:18px}.rules ul{margin:0;padding-left:18px;color:#d0d0d5}.rules li{margin:7px 0}.comparison{padding:14px 20px;border-top:1px solid var(--line);display:flex;gap:20px;align-items:center;flex-wrap:wrap}.comparison p{margin:0;font-size:12px}.zoom{border-top:1px solid var(--line);padding:20px}.zoom svg{height:220px;width:100%;background:#1b1b1d;border-radius:8px}.evidence{width:100%;display:block;border-radius:8px;background:white}.evidence-wrap{border:1px solid var(--line);padding:16px;border-radius:12px;margin:12px 0}.code{white-space:pre;overflow:auto;background:#121214;padding:18px;border:1px solid var(--line);border-radius:8px;font:12px/1.6 ui-monospace,monospace}.layer{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.layer>div{padding:16px;border:1px solid var(--line);border-radius:10px}.layer svg{width:100%;height:80px}.checklist label{display:flex;padding:10px 0;border-bottom:1px solid var(--line);font-size:14px}footer{border-top:1px solid var(--line);padding-top:20px;color:var(--muted);font-size:12px}@media(max-width:720px){main{padding:24px 16px}header{display:block}nav{margin-top:10px}.tokens,.pair,.rules,.layer{grid-template-columns:1fr}.example+.example{border-left:0;border-top:1px solid var(--line)}.stage{height:145px}.menu-stage{height:320px}}
</style></head><body><main><header><b>FLOWFORM / DESIGN SYSTEM</b><nav><a href="#pills">Pills</a><a href="#menus">Menus</a><a href="#material">Material</a><a href="#evidence">Evidence</a><a href="#integration">Code</a></nav></header><div class="eyebrow">Geometry standard · empirical reconstruction · 01</div><h1>Glass curvature.<br>Do it by geometry.</h1><p class="intro">Two distinct vessel primitives. Fixed-height toolbars with invariant end caps, and content-sized menus with invariant continuous corners. Compare the measured construction with common implementation mistakes.</p><div class="tokens"><div class="token"><span class="eyebrow">Pill height · locked</span><strong>36 pt</strong><small>72 physical px at 2×</small></div><div class="token"><span class="eyebrow">Pill shoulder</span><strong>21.126 pt</strong><small>Each end, independent of width</small></div><div class="token"><span class="eyebrow">Menu corner extent</span><strong>18.327 pt</strong><small>Each corner, independent of content</small></div></div>
<section id="pills"><div class="eyebrow">01 / fixed-height vessel</div><h2>Pills: width changes, height does not.</h2><p>Change the width to see how the two measured caps stay identical. The incorrect example is intentionally generated using a different rule.</p><div class="lab"><div class="controls"><label>Width <input id="pw" type="range" min="74" max="360" value="288"><output id="pwo"></output></label><label>Incorrect method <select id="pm"><option value="circle">Circular border-radius</option><option value="height">Content-driven height</option><option value="stretch">Stretch entire SVG</option></select></label><label><input id="pg" type="checkbox" checked> Guides</label></div><div class="pair"><div class="example"><h3 class="good">DO · fixed 36pt, measured caps</h3><div class="stage"><svg id="pd" role="img" aria-label="Correct fixed-height pill"></svg></div><p class="note" id="pdt"></p></div><div class="example"><h3 class="bad">DON'T · <span id="pbad"></span></h3><div class="stage"><svg id="px" role="img" aria-label="Incorrect pill example"></svg></div><p class="note" id="pxt"></p></div></div><div class="zoom"><h3>Magnified cap overlay</h3><p>Blue: fitted geometry. Orange: selected incorrect geometry. Equal coordinate scale, not independently stretched.</p><svg id="pz" aria-label="Overlay of pill end cap geometries"></svg></div></div><div class="rules"><div><h3 class="good">DO</h3><ul><li>Lock the border-box height at 36pt.</li><li>Use the same 21.126pt end-cap extent at every width.</li><li>Center contents vertically; increase width for added controls.</li><li>Prevent cap compression with a minimum width and overflow policy.</li></ul></div><div><h3 class="bad">DON'T</h3><ul><li>Let content, padding or zoom text dictate height.</li><li>Use a semicircle or generic rounded capsule as a substitute.</li><li>Stretch an already-drawn SVG to different aspect ratios.</li><li>Adjust curvature by adding shadows or outside strokes.</li></ul></div></div></section>
<section id="menus"><div class="eyebrow">02 / intrinsic-size vessel</div><h2>Menus: extend straight edges, not corners.</h2><p>The same eight-cubic path covers compact and tall menus. Change dimensions while retaining the fitted corner extent.</p><div class="lab"><div class="controls"><label>Width <input id="mw" type="range" min="100" max="280" value="160"><output id="mwo"></output></label><label>Height <input id="mh" type="range" min="100" max="519" value="224"><output id="mho"></output></label><label>Incorrect method <select id="mm"><option value="circle">Circular radius</option><option value="scale">Size-dependent corner</option><option value="stretch">Stretch entire SVG</option></select></label><label><input id="mg" type="checkbox" checked> Guides</label><button id="preset">Tall menu preset</button></div><div class="pair"><div class="example"><h3 class="good">DO · constant corner extent</h3><div class="stage menu-stage"><svg id="md" aria-label="Correct menu geometry"></svg></div><p class="note" id="mdt"></p></div><div class="example"><h3 class="bad">DON'T · <span id="mbad"></span></h3><div class="stage menu-stage"><svg id="mx" aria-label="Incorrect menu geometry"></svg></div><p class="note" id="mxt"></p></div></div><div class="zoom"><h3>Magnified corner overlay</h3><p>Compare the actual path segments at the same logical scale.</p><svg id="mz" aria-label="Overlay of menu corner geometries"></svg></div></div><div class="rules"><div><h3 class="good">DO</h3><ul><li>Keep the 18.327pt transition extent fixed.</li><li>Reflect one symmetric double-cubic corner to all four corners.</li><li>Allow menu width and height to follow content independently.</li><li>Preserve zero-curvature joins into straight sides.</li></ul></div><div><h3 class="bad">DON'T</h3><ul><li>Use percentage-based radii or proportional corner scaling.</li><li>Replace continuous corners with simple circular arcs.</li><li>Stretch the complete menu artwork to fit more rows.</li><li>Trace translucent color bleed or shadow as part of the shape.</li></ul></div></div></section>
<section id="material"><div class="eyebrow">03 / compositing</div><h2>Geometry first. Material second.</h2><p>Illustrative layers, not calibrated optical values. Keep the material clipped to the path and any shape-following shadow outside it.</p><div class="layer"><div><h3>01 · Geometry</h3><svg viewBox="0 0 160 50"><path id="lg" fill="none" stroke="#70bbeb" stroke-width="1"/></svg><p>Measured vessel boundary.</p></div><div><h3>02 · Material</h3><svg viewBox="0 0 160 50"><defs><linearGradient id="glass" x2="0" y2="1"><stop stop-color="#595959"/><stop offset=".15" stop-color="#404040"/><stop offset=".85" stop-color="#3a3a3a"/><stop offset="1" stop-color="#505050"/></linearGradient></defs><path id="lm" fill="url(#glass)"/></svg><p>Fill and edge treatment within the boundary.</p></div><div><h3>03 · Content</h3><svg viewBox="0 0 160 50"><path id="lc" fill="url(#glass)"/><g fill="#ddd" font-size="13" text-anchor="middle"><text x="30" y="29">−</text><text x="80" y="29">222%</text><text x="130" y="29">+</text></g></svg><p>Independent alignment and layout.</p></div></div></section>
<section id="evidence"><div class="eyebrow">04 / measured evidence</div><h2>What the measurements support.</h2><div class="evidence-wrap"><h3>Pill family: unchanged coefficients tested against two widths</h3><img class="evidence" src="PILL_IMG" alt="Actual long and short toolbar corner overlay and RMS residuals"><p>Previous model: 0.0839px / 0.0846px RMS. Circular caps: 0.1765px / 0.1779px RMS.</p></div><div class="evidence-wrap"><h3>Menu family: rasterized SVG against actual reference corners</h3><img class="evidence" src="MENU_IMG" alt="Actual Apple menu corners and exported SVG raster comparison"><p>Refined analytical fit: 0.0429px RMS. Exported SVG: 0.0739px / 0.0801px RMS.</p></div><p>These are capture-pixel results at 2×. The models reproduce observed silhouettes, not confirmed Apple source code. Optical effects and other component heights are outside the validated scope.</p></section>
<section id="integration"><div class="eyebrow">05 / implementation</div><h2>Production contract.</h2><p>Copy the dependency-free path generator and observer helper. The fixed pill entry point rejects too-small widths. Use an explicit layout fallback rather than compressing the caps.</p><button id="copy">Copy JavaScript</button> <output id="copyStatus" aria-live="polite"></output><pre class="code" id="code"></pre><h3>Acceptance checklist</h3><div class="checklist" id="checklist"></div><p id="checkStatus" aria-live="polite"></p></section><footer>Flowform · empirical curvature standard · no external dependencies. Geometry defines the vessel; material defines its appearance.</footer></main><script>
JS_SOURCE
const $=id=>document.getElementById(id);
const NS='http://www.w3.org/2000/svg';
function el(n,a){const e=document.createElementNS(NS,n);for(const [k,v] of Object.entries(a))e.setAttribute(k,v);return e}
function shape(svg,d,attrs={}){svg.append(el('path',{d,fill:'#414144',stroke:'#646469','stroke-width':.5,...attrs}))}
function rectPath(w,h,r){r=Math.min(r,w/2,h/2);return `M${r} 0H${w-r}A${r} ${r} 0 0 1 ${w} ${r}V${h-r}A${r} ${r} 0 0 1 ${w-r} ${h}H${r}A${r} ${r} 0 0 1 0 ${h-r}V${r}A${r} ${r} 0 0 1 ${r} 0Z`}
function draw(id,W,H,d,guide,extent,transform='',viewW=380,viewH=100){let s=$(id);s.replaceChildren();s.setAttribute('viewBox',`${(W-viewW)/2} ${(H-viewH)/2} ${viewW} ${viewH}`);shape(s,d,transform?{transform}:{});if(guide){for(const x of [extent,W-extent])s.append(el('path',{d:`M${x} -8V${H+8}`,stroke:'#70bbeb','stroke-width':.65,'stroke-dasharray':'2 2',fill:'none'}));}}
function overlay(id,good,bad,transform,view){let s=$(id);s.replaceChildren();s.setAttribute('viewBox',view);shape(s,good,{fill:'none',stroke:'#70bbeb','stroke-width':.24});shape(s,bad,{fill:'none',stroke:'#e6aa85','stroke-width':.24,'stroke-dasharray':'.65 .4',...(transform?{transform}:{})})}
function pill(){let w=+$('pw').value,m=$('pm').value,h=36,e=21.12588,bad,trans='',eh=36;const good=fixedPillPath(w);$('pwo').value=w+' pt';$('pdt').textContent=`${w} × 36 pt · fixed shoulders ${e.toFixed(3)} pt`;if(m==='circle'){bad=rectPath(w,h,18);$('pbad').textContent='semicircular ends';$('pxt').textContent='18pt circular radius; abrupt curvature transition.'}else if(m==='height'){eh=48;bad=applePillPath(w,eh);$('pbad').textContent='variable height';$('pxt').textContent='48pt instead of 36pt; vertical metrics and cap extent change.'}else{bad=fixedPillPath(288);trans=`scale(${w/288} 1)`;$('pbad').textContent='anisotropic scaling';$('pxt').textContent=`Shoulder becomes ${(e*w/288).toFixed(2)}pt instead of 21.126pt.`}draw('pd',w,h,good,$('pg').checked,e);draw('px',w,eh,bad,false,e,trans);overlay('pz',good,bad,trans,'-3 -3 37 54')}
function menu(){let w=+$('mw').value,h=+$('mh').value,m=$('mm').value,e=MENU_CORNER.extent,bad,trans='';const good=menuPath(w,h);$('mwo').value=w+' pt';$('mho').value=h+' pt';$('mdt').textContent=`${w} × ${h} pt · extent ${e.toFixed(3)} pt`;if(m==='circle'){bad=rectPath(w,h,12.1148);$('mbad').textContent='best-fitting circle';$('mxt').textContent='12.115pt radius from the circular fit; curvature jumps at straight joins.'}else if(m==='scale'){const ee=Math.min(w,h)*e/160;bad=menuPath(w,h,ee);$('mbad').textContent='proportional corner';$('mxt').textContent=`Extent changes to ${ee.toFixed(3)}pt with size.`}else{bad=menuPath(160,224);trans=`scale(${w/160} ${h/224})`;$('mbad').textContent='stretched corners';$('mxt').textContent='Horizontal and vertical corner geometry are scaled independently.'}draw('md',w,h,good,$('mg').checked,e,'',300,550);draw('mx',w,h,bad,false,e,trans,300,550);overlay('mz',good,bad,trans,'-3 -3 35 35')}
for(const k of ['pw','pm','pg'])$(k).addEventListener('input',pill);for(const k of ['mw','mh','mm','mg'])$(k).addEventListener('input',menu);$('preset').onclick=()=>{$('mw').value=185;$('mh').value=519;menu()};for(const k of ['lg','lm','lc']){$(k).setAttribute('d',fixedPillPath(160));$(k).setAttribute('transform','translate(0 7)')}
const code=CODE_LITERAL;$('code').textContent=code;$('copy').onclick=async()=>{try{await navigator.clipboard.writeText(code);$('copyStatus').textContent='Copied'}catch{$('copyStatus').textContent='Select and copy the code below.'}};
const checks=['Correct family selected','Pill border-box height fixed at 36pt','Invariant corner or end-cap extent','No anisotropic scaling or cap compression','Material and shadow separated from geometry','Actual exported shape and runtime inspected','Empirical scope and limitations disclosed'];for(const c of checks){const l=document.createElement('label'),i=document.createElement('input');i.type='checkbox';l.append(i,document.createTextNode(c));$('checklist').append(l);i.onchange=check}function check(){const n=$('checklist').querySelectorAll(':checked').length;$('checkStatus').textContent=`${n} of ${checks.length} checks complete`};check();pill();menu();</script></body></html>'''
html=html.replace('PILL_IMG',imgs['pill']).replace('MENU_IMG',imgs['menu']).replace('JS_SOURCE',js).replace('CODE_LITERAL',json.dumps(js))
(out/'apple-glass-curvature.html').write_text(html)
print('Created HTML, Markdown, JS:',[(p.name,p.stat().st_size) for p in out.iterdir() if p.suffix in ['.html','.md','.js']])
