/* Beachvolleyball Stats – minimaler Service Worker für Offline-Nutzung.
   Strategie: offline-first – gecachte Antworten sofort, ansonsten Netz, dann cachen. */
var CACHE = 'bv-stats-v1';
var ASSETS = ['./', './index.html', './manifest.json', './icon.svg'];

self.addEventListener('install', function (e) {
  e.waitUntil(
    caches.open(CACHE).then(function (c) {
      return Promise.all(ASSETS.map(function (u) {
        return c.add(new Request(u, { cache: 'no-store' })).catch(function () { return null; });
      }));
    })
  );
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(
        keys.filter(function (k) { return k !== CACHE; })
            .map(function (k) { return caches.delete(k); })
      );
    })
  );
});

self.addEventListener('fetch', function (e) {
  if (e.request.method !== 'GET') { return; }
  e.respondWith(
    caches.match(e.request, { ignoreSearch: true }).then(function (hit) {
      if (hit) { return hit; }
      return fetch(e.request).then(function (net) {
        if (net && net.ok) {
          var copy = net.clone();
          caches.open(CACHE).then(function (c) { c.put(e.request, copy); });
        }
        return net;
      });
    })
  );
});