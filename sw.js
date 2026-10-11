// Service worker: guarda una copia de la app para que abra sin conexión.
// Estrategia "red primero": si hay internet se baja siempre la última versión publicada;
// si no hay, se usa la copia guardada. Los datos del usuario no pasan por acá (están en localStorage o en Firestore).

// La versión estable y la beta comparten dominio y almacenamiento de caché: el nombre incluye
// la carpeta (scope) para que cada una maneje solo el suyo.
// Subir VERSION_CACHE cuando cambien los archivos de ARCHIVOS que no son index.html.
const VERSION_CACHE = 2;
const SCOPE = new URL(self.registration.scope).pathname;
const PREFIJO = `libreta@${SCOPE}#`;
const CACHE = PREFIJO + VERSION_CACHE;
const ARCHIVOS = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './apple-touch-icon.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ARCHIVOS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      // Borra versiones viejas de este mismo scope. El caché de la 1.0 ('libreta-v1') era de la versión
      // estable: lo borra solo ella, así abrir la beta no le quita la copia sin conexión.
      .then(claves => Promise.all(claves
        .filter(k => k !== CACHE && (k.startsWith(PREFIJO) || (k === 'libreta-v1' && !SCOPE.includes('/beta/'))))
        .map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  // Firebase (para sincronizar con Google): la versión va en la URL y ese archivo nunca cambia,
  // así que se guarda la primera vez y después se usa la copia. Así la libreta sincronizada abre sin conexión.
  if (url.origin === 'https://www.gstatic.com' && url.pathname.startsWith('/firebasejs/')) {
    e.respondWith(caches.match(e.request).then(r => r || fetch(e.request).then(resp => {
      if (resp.ok) { const copia = resp.clone(); caches.open(CACHE).then(c => c.put(e.request, copia)); }
      return resp;
    })));
    return;
  }
  // Fuentes y la librería del Excel vienen de otros sitios: van directo a internet.
  if (url.origin !== self.location.origin) return;
  e.respondWith(
    fetch(e.request)
      .then(resp => {
        if (resp.ok) { const copia = resp.clone(); caches.open(CACHE).then(c => c.put(e.request, copia)); }
        return resp;
      })
      .catch(() => caches.match(e.request).then(r => r || caches.match(new URL('./index.html', self.registration.scope))))
  );
});
