// Gera os PNGs dos ícones a partir dos SVGs: node pwa/icons.js
const path = require('path'), fs = require('fs');
const { chromium } = require(process.env.PW || 'playwright');
const dir = __dirname, out = path.join(dir, 'icons');
fs.mkdirSync(out, { recursive: true });
const jobs = [['icon.svg','icon-192.png',192],['icon.svg','icon-512.png',512],['icon-maskable.svg','maskable-192.png',192],['icon-maskable.svg','maskable-512.png',512],['icon-maskable.svg','apple-touch-icon.png',180],['icon.svg','favicon-32.png',32]];
(async () => {
  const b = await chromium.launch();
  for (const [src, name, size] of jobs) {
    const p = await b.newPage({ viewport: { width: size, height: size } });
    const svg = fs.readFileSync(path.join(dir, src), 'utf8');
    await p.setContent(`<style>html,body{margin:0;background:transparent}svg{width:${size}px;height:${size}px;display:block}</style>${svg}`);
    await p.screenshot({ path: path.join(out, name), omitBackground: true });
    await p.close();
  }
  fs.copyFileSync(path.join(dir, 'icon.svg'), path.join(out, 'icon.svg'));
  await b.close();
  console.log('ícones gerados em', out);
})();
