/* Beachvolleyball Stats – Service Worker für Offline-Nutzung.
   Strategie: App-Shell (index.html) network-first → bei Internet immer die
   frische Version (Updates werden automatisch übernommen), offline Cache-Fallback.
   Übrige Assets (Icons, Manifest …): cache-first. */
var CACHE = 'bv-stats-v7';
var ASSETS = ['./', './index.html', './manifest.json', './icon.svg', './icon-192.png', './icon-512.png'];

self.addEventListener('install', function (e) {
  self.skipWaiting(); // neue Version sofort aktivieren statt auf den nächsten Start zu warten
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
    }).then(function () {
      return self.clients.claim(); // offene Tabs sofort von der neuen Version übernehmen
    })
  );
});

self.addEventListener('fetch', function (e) {
  if (e.request.method !== 'GET') { return; }

  // Navigations-Requests (index.html / start_url): network-first – bei Internet
  // immer die frische Version laden und den Cache aktualisieren, offline aus dem Cache.
  if (e.request.mode === 'navigate') {
    e.respondWith(
      fetch(e.request).then(function (net) {
        if (net && net.ok) {
          var copy = net.clone();
          caches.open(CACHE).then(function (c) { c.put(e.request, copy); });
          return net;
        }
        return caches.match(e.request, { ignoreSearch: true });
      }).catch(function () {
        return caches.match(e.request, { ignoreSearch: true });
      })
    );
    return;
  }

  // Übrige Assets (Icons, Manifest …): cache-first, sonst Netz.
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