/* Service worker do Tração: guarda o app inteiro para funcionar sem internet. */
const VERSION = '1.0.0-c0e199cf';
const CACHE = 'tracao-' + VERSION;
const ASSETS = [
  "./",
  "./index.html",
  "./fonts/fonts.css",
  "./fonts/ieVn2YZDLWuGJpnzaiwFXS9tYtpT59CjCQ.woff2",
  "./fonts/ieVn2YZDLWuGJpnzaiwFXS9tYtpd59A.woff2",
  "./fonts/k3kQo8UDI-1M0wlSfdfoLnnA.woff2",
  "./fonts/k3kQo8UDI-1M0wlSfdnoLg.woff2",
  "./icons/apple-touch-icon.png",
  "./icons/favicon-32.png",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon.svg",
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
