/* Service worker do Magni: guarda o app inteiro para funcionar sem internet. */
const VERSION = '1.2.1-4c0ca44a';
const CACHE = 'tracao-' + VERSION;
const ASSETS = [
  "./",
  "./index.html",
  "./fonts/cIflMapbsEk7TDLdtEz1BwkeJI91R5_F.woff2",
  "./fonts/cIflMapbsEk7TDLdtEz1BwkeJI91SZ_F7AY.woff2",
  "./fonts/cIflMapbsEk7TDLdtEz1BwkeQI51R5_F.woff2",
  "./fonts/cIflMapbsEk7TDLdtEz1BwkeQI51SZ_F7AY.woff2",
  "./fonts/cIflMapbsEk7TDLdtEz1BwkebIl1R5_F.woff2",
  "./fonts/cIflMapbsEk7TDLdtEz1BwkebIl1SZ_F7AY.woff2",
  "./fonts/fonts.css",
  "./fonts/xn7gYHE41ni1AdIRggexSg.woff2",
  "./fonts/xn7gYHE41ni1AdIRggmxSuXd.woff2",
  "./icons/apple-touch-icon.png",
  "./icons/favicon-32.png",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/maskable-192.png",
  "./icons/maskable-512.png",
  "./manifest.webmanifest"
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k.startsWith('tracao-') && k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('message', e => {
  if (e.data === 'SKIP_WAITING') self.skipWaiting();
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  if (req.mode === 'navigate') {
    e.respondWith(caches.match('./index.html').then(hit => hit || fetch(req)));
    return;
  }
  e.respondWith(caches.match(req).then(hit => hit || fetch(req)));
});
