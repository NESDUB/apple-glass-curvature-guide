const {test}=require('node:test');
const assert=require('node:assert/strict');
const g=require('../glass-curvature.js');
const {glassPath,getGlassPreset,GLASS_PRESETS,menuPath,applePillPath}=g;
function parse(d){
 const tokens=d.match(/[MCHVZ]|-?(?:\d+(?:\.\d*)?|\.\d+)/g); let i=0,p,first; const segments=[];
 while(i<tokens.length){const op=tokens[i++];let q;const num=()=>Number(tokens[i++]);
 if(op==='M'){p=[num(),num()];first=p;continue;}
 if(op==='C'){const pts=[p,[num(),num()],[num(),num()],[num(),num()]];segments.push({op,pts});p=pts[3];continue;}
 if(op==='H')q=[num(),p[1]];else if(op==='V')q=[p[0],num()];else if(op==='Z')q=first;else throw Error(op);
 segments.push({op,pts:[p,q]});p=q;
 }return segments;
}
function near(a,b,tol=2e-5){assert.ok(Math.abs(a-b)<=tol,`${a} vs ${b}`)}
function bounds(d,w,h,n){const s=parse(d);let points=s.flatMap(z=>z.pts);for(let i=0;i<2;i++){near(Math.min(...points.map(p=>p[i])),0);near(Math.max(...points.map(p=>p[i])),[w,h][i]);}assert.equal(s.filter(x=>x.op==='C').length,n);}
function cap(d){return parse(d).filter(z=>z.op==='C').slice(0,6).map(z=>z.pts);}
function corner(d){return parse(d).filter(z=>z.op==='C').slice(0,2).map(z=>z.pts);}
test('four immutable component presets and legacy alias',()=>{assert.equal(Object.keys(GLASS_PRESETS).length,4);assert.ok(Object.isFrozen(GLASS_PRESETS));for(const p of Object.values(GLASS_PRESETS))assert.ok(Object.isFrozen(p));assert.equal(getGlassPreset('pill'),GLASS_PRESETS.toolbar);assert.equal(GLASS_PRESETS.toolbar.height,36);assert.equal(GLASS_PRESETS.actionButton.height,28);near(GLASS_PRESETS.toolbar.extent,21.12588);near(GLASS_PRESETS.actionButton.extent,16.43124);near(GLASS_PRESETS.dialog.extent,39.774);});
for(const [k,h,widths] of [['toolbar',36,[74,258,288,400]],['actionButton',28,[80,228,300]]]){
 test(`${k}: fixed height and invariant cap coordinates`,()=>{const baseline=cap(glassPath(k,widths[0]));for(const w of widths){const p=glassPath(k,w);bounds(p,w,h,24);assert.deepEqual(cap(p),baseline);assert.equal(p,applePillPath(w,h));assert.equal(p,glassPath(k,w,h));}});
 test(`${k}: reject wrong height, nonfinite and compressed caps`,()=>{for(const [w,H] of [[0,h],[Infinity,h],[2*GLASS_PRESETS[k].extent-.001,h],[100,h+1],[100,NaN],[100,null]])assert.throws(()=>glassPath(k,w,H),RangeError);});
}
for(const [k,sizes] of [['menu',[[160,224],[185,519],[240,160]]],['dialog',[[260,172],[320,180],[200,300]]]]){
 test(`${k}: fixed corner extent and bounds`,()=>{const baseline=corner(glassPath(k,...sizes[0]));for(const [w,h] of sizes){const p=glassPath(k,w,h);bounds(p,w,h,8);assert.deepEqual(corner(p),baseline);assert.equal(p,menuPath(w,h,GLASS_PRESETS[k].extent));}});
 test(`${k}: reject undersized dimensions`,()=>{for(const [w,h] of [[20,200],[200,20],[NaN,200],[200,Infinity],[200,undefined]])assert.throws(()=>glassPath(k,w,h),RangeError);});
}
test('legacy functions and new convenience entry points',()=>{assert.equal(g.fixedPillPath(288),glassPath('toolbar',288));assert.equal(g.actionButtonPath(228),glassPath('actionButton',228));assert.equal(g.dialogPath(260,172),glassPath('dialog',260,172));assert.equal(glassPath('pill',74),glassPath('toolbar',74));assert.throws(()=>glassPath('unknown',100,100),RangeError);assert.throws(()=>getGlassPreset('__proto__'),RangeError);});
test('zero curvature at straight seams (collinear endpoint and two controls)',()=>{for(const [kind,w,h] of [['toolbar',288,36],['actionButton',228,28],['menu',160,224],['dialog',260,172]]){const s=parse(glassPath(kind,w,h));for(let i=0;i<s.length;i++){if(s[i].op!=='C')continue;const pts=s[i].pts;const prev=s[(i+s.length-1)%s.length],next=s[(i+1)%s.length];for(const [adj,endpoint,ctrl1,ctrl2] of [[prev,pts[0],pts[1],pts[2]],[next,pts[3],pts[2],pts[1]]]){if(!['H','V'].includes(adj.op))continue;const axis=adj.op==='H'?1:0;near(endpoint[axis],ctrl1[axis]);near(endpoint[axis],ctrl2[axis]);}}}});
test('observer rejects bad layout and recovers; disconnect works',()=>{let callback,disconnected=false;global.ResizeObserver=class{constructor(fn){callback=fn;}observe(){}disconnect(){disconnected=true;}};const el={offsetWidth:228,offsetHeight:28,style:{},dataset:{}};const stop=g.attachGlassShape(el,'actionButton');assert.match(el.style.clipPath,/^path\(/);callback([{borderBoxSize:[{inlineSize:228,blockSize:36}]}]);assert.ok(el.dataset.geometryError);assert.equal(el.style.clipPath,'inset(50%)');callback([{borderBoxSize:[{inlineSize:250.5,blockSize:28}]}]);assert.equal(el.dataset.geometryError,undefined);assert.equal(el.style.clipPath,`path("${glassPath('actionButton',250.5)}")`);stop();assert.ok(disconnected);delete global.ResizeObserver;});
