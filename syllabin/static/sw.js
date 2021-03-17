'use strict';
importScripts('/static/js/sw-toolbox.js');

toolbox.precache(["/","/static/open-iconic/font/fonts/open-iconic.woff","/static/css/bootstrap.min.css", "/static/js/app.js", "/static/js/bootstrap.bundle.min.js", "/static/js/jquery-3.5.1.min.js", "/static/open-iconic/font/css/open-iconic-bootstrap.css"]);
toolbox.router.get('/static/*', toolbox.cacheFirst);
toolbox.router.get('/*', toolbox.networkFirst, { networkTimeoutSeconds: 4});

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
});
self.addEventListener('install', function(event) {
  self.skipWaiting();
});
