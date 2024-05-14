// Service worker installation and activation
self.addEventListener('install', event => {
    console.log('Service worker installed');
    self.skipWaiting(); // Activate service worker immediately
  });
  
  self.addEventListener('activate', event => {
    console.log('Service worker activated');
  });
  
  // Push notification event handling
  self.addEventListener('push', event => {
    const payload = event.data ? event.data.text() : 'Default notification';
    event.waitUntil(
      self.registration.showNotification('Web Push Notification', {
        body: payload,
        icon: '/static/notification-icon.png' // Path to your notification icon
      })
    );
  });
  
  // Fetch event handling for caching static assets
  self.addEventListener('fetch', event => {
    event.respondWith(
      caches.match(event.request)
        .then(response => {
          // Cache hit - return response from cache
          if (response) {
            return response;
          }
          // Clone the request because it's a one-time use
          const fetchRequest = event.request.clone();
          return fetch(fetchRequest).then(response => {
            // Check if we received a valid response
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }
            // Clone the response because we need to put it in the cache
            const responseToCache = response.clone();
            caches.open('static-cache-v1').then(cache => {
              cache.put(event.request, responseToCache);
            });
            return response;
          });
        })
    );
  });
  