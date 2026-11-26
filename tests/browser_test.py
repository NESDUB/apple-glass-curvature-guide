"""Optional actual Chromium integration checks. No external requests permitted."""
import os, shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    exe=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('chromium-browser')
    browser=p.chromium.launch(executable_path=exe,headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1280,'height':1000},device_scale_factor=2)
    errors=[]; requests=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.route('http*',lambda route:(requests.append(route.request.url),route.abort()))
    page.set_content((ROOT/'apple-glass-curvature.html').read_text(encoding='utf-8'),wait_until='load')
    assert page.locator('#pd path').count()>0
    assert '288 × 36 pt' in page.locator('#pdt').inner_text()
    page.select_option('#pc','actionButton')
    assert '288 × 28 pt' in page.locator('#pdt').inner_text()
    page.locator('#pw').evaluate("e=>{e.value=228;e.dispatchEvent(new Event('input'))}")
    assert '228 × 28 pt' in page.locator('#pdt').inner_text()
    for mode in ['circle','height','stretch']: page.select_option('#pm',mode);assert page.locator('#px path').count()>0
    page.click('#preset');assert '185 × 519 pt' in page.locator('#mdt').inner_text()
    for mode in ['circle','scale','stretch']:page.select_option('#mm',mode);assert page.locator('#mx path').count()>0
    assert '260 × 172 pt' in page.locator('#ddt').inner_text()
    assert page.locator('#dd path').count()==4 # shell, two actions, guide
    for mode in ['menu','double','circle','scale']:
        page.select_option('#dm',mode);assert page.locator('#dx path').count()==3
    page.locator('#dw').evaluate("e=>{e.value=320;e.dispatchEvent(new Event('input'))}")
    page.locator('#dh').evaluate("e=>{e.value=220;e.dispatchEvent(new Event('input'))}")
    assert '320 × 220 pt' in page.locator('#ddt').inner_text()
    # Check actual path bounding boxes via Chromium's SVG geometry API.
    result=page.locator('#dd path').evaluate_all('(els)=>els.slice(0,3).map(e=>{const b=e.getBBox();return [b.width,b.height]})')
    assert result==[[320,220],[288,28],[288,28]],result
    assert page.locator('#evidence img').count()==4
    assert page.locator('#evidence img').evaluate_all('(els)=>els.every(e=>e.complete&&e.naturalWidth>0)')
    assert page.locator('#code').inner_text().strip()==(ROOT/'glass-curvature.js').read_text().strip()
    # Directly exercise the real ResizeObserver in Chromium, not just its stub.
    page.evaluate('''()=>{const e=document.createElement('div');e.id='observer-test';e.style.cssText='width:228px;height:28px;position:absolute';document.body.append(e);window.cleanup=attachGlassShape(e,'actionButton')}''')
    page.wait_for_function("document.querySelector('#observer-test').style.clipPath.startsWith('path(')")
    page.evaluate("document.querySelector('#observer-test').style.height='36px'")
    page.wait_for_function("document.querySelector('#observer-test').dataset.geometryError")
    page.evaluate("document.querySelector('#observer-test').style.height='28px'")
    page.wait_for_function("!document.querySelector('#observer-test').dataset.geometryError")
    page.evaluate("cleanup();document.querySelector('#observer-test').remove()")
    assert not errors,errors
    assert not requests,requests
    print('Chromium: preset switching, all comparison modes, SVG dimensions, embedded evidence, canonical code, ResizeObserver recovery, no page errors or external requests: PASS')
    if os.environ.get('PREVIEW_DIR'):
        dest=Path(os.environ['PREVIEW_DIR']);dest.mkdir(exist_ok=True,parents=True)
        page.locator('#dw').evaluate("e=>{e.value=260;e.dispatchEvent(new Event('input'))}")
        page.locator('#dh').evaluate("e=>{e.value=172;e.dispatchEvent(new Event('input'))}")
        page.select_option('#dm','menu')
        page.locator('#dialog').screenshot(path=str(dest/'dialog-lab.png'))
        page.screenshot(path=str(dest/'guide-preview.png'))
    browser.close()
