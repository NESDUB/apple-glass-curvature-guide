"""Build the offline guide from canonical sources. Python standard library only."""
from pathlib import Path
import base64, json
ROOT = Path(__file__).resolve().parent
html = (ROOT/'guide.template.html').read_text(encoding='utf-8')
js = (ROOT/'glass-curvature.js').read_text(encoding='utf-8')
for name in ('pill','menu','dialog','action'):
    marker = name.upper()+'_IMG'
    assert html.count(marker)==1, marker
    html=html.replace(marker,'data:image/png;base64,'+base64.b64encode((ROOT/'evidence'/f'{name}.png').read_bytes()).decode('ascii'))
assert html.count('JS_SOURCE')==1 and html.count('CODE_LITERAL')==1
html=html.replace('JS_SOURCE',js).replace('CODE_LITERAL',json.dumps(js,ensure_ascii=False).replace('</','<\\/'))
(ROOT/'apple-glass-curvature.html').write_text(html,encoding='utf-8')
print('Built offline guide')
