#!/usr/bin/env python3
"""Gera a versão instalável (PWA) do Magni em docs/, pronta para o GitHub Pages.

Uso: python3 build.py
- index.html é a fonte única do app (também publicada como prévia no Claude).
- As fontes do Google são baixadas uma vez para pwa/fonts/ e servidas localmente,
  para o app funcionar sem internet.
"""
import hashlib, json, re, shutil, urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
PWA = ROOT / 'pwa'
OUT = ROOT / 'docs'
VERSION = (ROOT / 'VERSION').read_text().strip()
FONTS_URL = ('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700'
             '&family=Manrope:wght@400;500;600;700&display=swap')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA})).read()


def ensure_fonts():
    fdir = PWA / 'fonts'
    css_path = fdir / 'fonts.css'
    if css_path.exists():
        return
    fdir.mkdir(parents=True, exist_ok=True)
    css = get(FONTS_URL).decode()
    blocks = re.findall(r'/\* ([\w-]+) \*/\s*(@font-face \{.*?\})', css, re.S)
    keep = []
    for subset, block in blocks:
        if subset not in ('latin', 'latin-ext'):
            continue
        url = re.search(r'url\((https://[^)]+\.woff2)\)', block).group(1)
        name = url.rsplit('/', 1)[1]
        if not (fdir / name).exists():
            (fdir / name).write_bytes(get(url))
        keep.append(f'/* {subset} */\n' + block.replace(url, name))
    css_path.write_text('\n'.join(keep) + '\n')


HEAD = '''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Força do próprio corpo. Treinos de calistenia com programas, escadas de progressão e cronômetro, sem conta e com os dados no seu aparelho.">
<meta name="theme-color" content="#0E1A17">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Magni">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<link rel="stylesheet" href="fonts/fonts.css">
<style>
html,body{margin:0}
:root{padding-top:env(safe-area-inset-top,0px)}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:40;background:var(--bg)}
.update-bar{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(var(--nav-h) + 14px + env(safe-area-inset-bottom,0px));z-index:70;display:flex;align-items:center;gap:12px;padding:8px 8px 8px 16px;border-radius:99px;background:var(--fg);color:var(--bg);font-weight:600;font-size:14px;white-space:nowrap}
.update-bar button{padding:8px 14px;border-radius:99px;background:var(--accent);color:var(--on-accent);font-weight:700}
</style>
<script>window.TRACAO_PWA = {version: "__VERSION__"};</script>
'''

TAIL = '''<script>
(() => {
  try { navigator.storage && navigator.storage.persist && navigator.storage.persist(); } catch (e) {}
  if (!('serviceWorker' in navigator)) return;
  let reloading = false;
  navigator.serviceWorker.addEventListener('controllerchange', () => { if (!reloading) { reloading = true; location.reload(); } });
  function offer(worker) {
    if (document.querySelector('.update-bar')) return;
    const bar = document.createElement('div');
    bar.className = 'update-bar';
    bar.innerHTML = '<span>Nova versão disponível</span><button type="button">Atualizar</button>';
    bar.querySelector('button').onclick = () => worker.postMessage('SKIP_WAITING');
    document.body.appendChild(bar);
  }
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('sw.js').then(reg => {
      if (reg.waiting && navigator.serviceWorker.controller) offer(reg.waiting);
      reg.addEventListener('updatefound', () => {
        const w = reg.installing;
        w && w.addEventListener('statechange', () => { if (w.state === 'installed' && navigator.serviceWorker.controller) offer(w); });
      });
      document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') reg.update(); });
    }).catch(() => {});
  });
})();
</script>
</body>
</html>
'''


def build():
    ensure_fonts()
    src = (ROOT / 'index.html').read_text()
    # Tira o que só serve à prévia no Claude: links do Google Fonts e a meta do visualizador.
    src = re.sub(r'<link rel="(preconnect|stylesheet)" href="https://fonts\.(googleapis|gstatic)\.com[^>]*>\n?', '', src)
    src = re.sub(r'<meta name="(claude:viewport-fit-sides|theme-color)"[^>]*>\n?', '', src)
    title = re.search(r'<title>.*?</title>\n?', src).group(0)
    src = src.replace(title, '', 1)
    style_end = src.index('</style>') + len('</style>')
    head_css, body = src[:style_end], src[style_end:]

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(PWA / 'icons', OUT / 'icons')
    shutil.copytree(PWA / 'fonts', OUT / 'fonts')
    shutil.copy(PWA / 'manifest.webmanifest', OUT / 'manifest.webmanifest')
    (OUT / '.nojekyll').write_text('')

    html_draft = HEAD + title + head_css.strip() + '\n</head>\n<body>\n' + body.strip() + '\n' + TAIL
    # Lista sem repetições: cache.addAll recusa a instalação inteira se um item aparecer duas vezes.
    files = {'./' + p.relative_to(OUT).as_posix() for p in OUT.rglob('*') if p.is_file() and p.name != '.nojekyll'}
    assets = ['./', './index.html'] + sorted(files - {'./index.html'})

    # A versão do cache muda sempre que qualquer arquivo muda, para o app avisar da atualização.
    h = hashlib.sha256(html_draft.encode())
    for p in sorted(OUT.rglob('*')):
        if p.is_file():
            h.update(p.read_bytes())
    build_id = f'{VERSION}-{h.hexdigest()[:8]}'

    (OUT / 'index.html').write_text(html_draft.replace('__VERSION__', VERSION))
    sw = (PWA / 'sw.js').read_text().replace('__VERSION__', build_id).replace('__ASSETS__', json.dumps(assets, indent=2))
    (OUT / 'sw.js').write_text(sw)

    total = sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
    print(f'Magni {VERSION} ({build_id}) gerado em docs/: {len(assets)} arquivos em cache, {total/1024:.0f} KB no total')


if __name__ == '__main__':
    build()
