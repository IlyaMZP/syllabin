console.log('Hello from sw.js');

importScripts('https://storage.googleapis.com/workbox-cdn/releases/6.1.0/workbox-sw.js');

if (workbox) {
  workbox.routing.registerRoute(
    /^.*\.(?!jpg$|png$|js$|gif$|jpeg$|svg$|css$)[^.]+$/,
    new workbox.strategies.NetworkFirst({
      cacheName: 'pages',
      plugins: [
        new workbox.expiration.ExpirationPlugin({
          maxEntries: 60,
          maxAgeSeconds: 24 * 60 * 60, // 1 Day
        }),
      ],
    }),
  );

  workbox.routing.registerRoute(
    /\.(?:js|css)$/,
    new workbox.strategies.NetworkFirst({
      cacheName: 'static-resources',
      plugins: [
        new workbox.expiration.ExpirationPlugin({
          maxEntries: 60,
          maxAgeSeconds: 1, // 1 Day
        }),
      ],
    }),
  );

  workbox.routing.registerRoute(
    /\.(?:png|gif|jpg|jpeg|svg)$/,
    new workbox.strategies.CacheFirst({
      cacheName: 'images',
      plugins: [
        new workbox.expiration.ExpirationPlugin({
          maxEntries: 120,
          maxAgeSeconds: 1, // 14 Days = 14 * 24 * 60 * 60
        }),
      ],
    }),
  );
  self.addEventListener('push', event => {
    console.log('[Service Worker] Push Received.');
    console.log(`[Service Worker] Push had this data: "${event.data.text()}"`);
    const title = "Syllabin Notification";
    var options = {
        body: `${event.data.text()}`,
        icon: "/static/images/icons/icon-192x192.png",
        badge: "/static/images/badge.webp"
    };
    event.waitUntil(self.registration.showNotification(title, options))
  })
  workbox.routing.registerRoute(
    new RegExp('https://fonts.(?:googleapis|gstatic).com/(.*)'),
    new workbox.strategies.CacheFirst({
      cacheName: 'googleapis',
      plugins: [
        new workbox.expiration.ExpirationPlugin({
          maxEntries: 30,
        }),
      ],
    }),
  );

  workbox.core.skipWaiting();
  workbox.core.clientsClaim();
} else {
  console.log(`Error loading Workbox`);
}
