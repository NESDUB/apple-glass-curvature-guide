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

if(typeof module !== "undefined") module.exports={menuPath,applePillPath,fixedPillPath,attachGlassShape,MENU_CORNER,PILL_HEIGHT,PILL_MIN_WIDTH};
