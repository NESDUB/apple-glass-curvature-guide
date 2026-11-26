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


// Revision 2.0: two mathematical families, four immutable component presets.
const PILL_HEIGHT = 36;
const PILL_MIN_WIDTH = PILL_HEIGHT * EXTENT;
const GLASS_PRESETS = Object.freeze({
  toolbar: Object.freeze({family:'pill', height:36, extent:36*EXTENT/2}),
  actionButton: Object.freeze({family:'pill', height:28, extent:28*EXTENT/2}),
  menu: Object.freeze({family:'roundedRectangle', extent:MENU_CORNER.extent}),
  dialog: Object.freeze({family:'roundedRectangle', extent:39.774})
});
// Legacy "pill" refers only to the toolbar class.
function getGlassPreset(kind) {
  const key = kind === 'pill' ? 'toolbar' : kind;
  if (!Object.prototype.hasOwnProperty.call(GLASS_PRESETS,key))
    throw new RangeError('Unknown glass component: '+kind);
  return GLASS_PRESETS[key];
}
function glassPath(kind, width, height) {
  const p = getGlassPreset(kind);
  if (!Number.isFinite(width) || width <= 0) throw new RangeError('Invalid width');
  if (p.family === 'pill') {
    if (height !== undefined && (!Number.isFinite(height) || Math.abs(height-p.height)>0.01))
      throw new RangeError('Invalid fixed-height pill dimensions');
    if (width < 2*p.extent) throw new RangeError('Pill too narrow for full end caps');
    return applePillPath(width,p.height);
  }
  if (!Number.isFinite(height) || Math.min(width,height) < 2*p.extent)
    throw new RangeError('Rectangle too small for full corners');
  return menuPath(width,height,p.extent);
}
function fixedPillPath(width) { return glassPath('toolbar',width); }
function actionButtonPath(width) { return glassPath('actionButton',width); }
function dialogPath(width,height) { return glassPath('dialog',width,height); }
// Observe an isolated, horizontal-writing-mode material layer. Invalid geometry
// is hidden by an empty clip rather than falling back to a rectangular vessel.
function attachGlassShape(element, kind) {
  getGlassPreset(kind);
  const update = (entries) => {
    const box = entries?.[0]?.borderBoxSize;
    const size = Array.isArray(box) ? box[0] : box;
    const w = size?.inlineSize ?? element.offsetWidth;
    const h = size?.blockSize ?? element.offsetHeight;
    try {
      const d = glassPath(kind,w,h);
      delete element.dataset.geometryError;
      element.style.clipPath = `path("${d}")`;
    } catch(error) {
      element.dataset.geometryError = error.message;
      element.style.clipPath = 'inset(50%)';
    }
  };
  const observer = new ResizeObserver(update);
  observer.observe(element,{box:'border-box'});
  update();
  return () => observer.disconnect();
}
if(typeof module !== "undefined") module.exports={menuPath,applePillPath,fixedPillPath,actionButtonPath,dialogPath,glassPath,getGlassPreset,attachGlassShape,MENU_CORNER,GLASS_PRESETS,PILL_HEIGHT,PILL_MIN_WIDTH};
