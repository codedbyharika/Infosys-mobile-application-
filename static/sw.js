/**
 * AirSense AI — Service Worker (PWA)
 * Milestone 3: Offline support, asset caching, background sync, and push notifications.
 */

const CACHE_NAME = 'airsense-v1.0.0';
const API_CACHE_NAME = 'airsense-api-v1';

// Static assets to pre-cache
const PRECACHE_URLS = [
  '/static/css/style.css',
  '/static/js/app.js',
  '/static/js/map.js',
  '/static/js/charts.js',
  '/static/js/api.js',
  '/static/manifest.json',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap',
  'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
];

// Offline fallback HTML
const OFFLINE_HTML = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AirSense AI — Offline</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Inter', system-ui, sans-serif;
      background: #0f172a;
      color: #e2e8f0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      text-align: center;
      padding: 24px;
    }
    .icon {
      width: 80px; height: 80px;
      background: rgba(56,189,248,0.12);
      border: 2px solid rgba(56,189,248,0.3);
      border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      margin: 0 auto 24px;
      font-size: 2rem;
    }
    h1 { font-size: 1.5rem; font-weight: 700; margin-bottom: 8px; }
    p { color: #94a3b8; font-size: 0.9rem; line-height: 1.6; max-width: 320px; }
    .retry-btn {
      margin-top: 24px;
      padding: 12px 28px;
      background: linear-gradient(135deg, #0ea5e9, #2563eb);
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
    }
    .cached-note {
      margin-top: 16px;
      font-size: 0.78rem;
      color: #475569;
    }
  </style>
</head>
<body>
  <div class="icon">📡</div>
  <h1>You're Offline</h1>
  <p>AirSense AI requires a network connection to load live AQI data. Your cached data and settings are still available.</p>
  <button class="retry-btn" onclick="window.location.reload()">Retry Connection</button>
  <p class="cached-note">Last sync: check localStorage for cached readings</p>
</body>
</html>`;

// ── Install: Pre-cache static assets ────────────────────────────────────────
self.addEventListener('install', (event) => {
  console.log('[SW] Installing AirSense Service Worker v1.0.0');
  event.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      // Cache only local static assets (skip CDN failures silently)
      const localAssets = PRECACHE_URLS.filter(url => url.startsWith('/'));
      try {
        await cache.addAll(localAssets);
      } catch (err) {
        console.warn('[SW] Some assets failed to pre-cache:', err);
      }
      // Store offline fallback
      await cache.put('/__offline', new Response(OFFLINE_HTML, {
        headers: { 'Content-Type': 'text/html' }
      }));
    })
  );
  self.skipWaiting();
});

// ── Activate: Clean old caches ───────────────────────────────────────────────
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating AirSense Service Worker');
  event.waitUntil(
    caches.keys().then((cacheNames) =>
      Promise.all(
        cacheNames
          .filter(name => name !== CACHE_NAME && name !== API_CACHE_NAME)
          .map(name => {
            console.log('[SW] Deleting old cache:', name);
            return caches.delete(name);
          })
      )
    )
  );
  self.clients.claim();
});

// ── Fetch: Routing strategy ──────────────────────────────────────────────────
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') return;

  // Skip chrome-extension and non-http(s)
  if (!url.protocol.startsWith('http')) return;

  // API calls: Network-first with API cache fallback
  if (url.pathname.startsWith('/api/') || url.pathname === '/stations') {
    event.respondWith(networkFirstWithApiCache(request));
    return;
  }

  // Static assets: Cache-first
  if (
    url.pathname.startsWith('/static/') ||
    url.hostname.includes('fonts.googleapis.com') ||
    url.hostname.includes('fonts.gstatic.com') ||
    url.hostname.includes('unpkg.com') ||
    url.hostname.includes('cdn.jsdelivr.net')
  ) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // HTML pages: Network-first with offline fallback
  if (request.headers.get('Accept')?.includes('text/html')) {
    event.respondWith(networkFirstWithOfflineFallback(request));
    return;
  }

  // Default: stale-while-revalidate
  event.respondWith(staleWhileRevalidate(request));
});

// Strategy: Cache-first (for static assets)
async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return new Response('Asset unavailable offline', { status: 503 });
  }
}

// Strategy: Network-first with API cache
async function networkFirstWithApiCache(request) {
  try {
    const response = await fetch(request, { signal: AbortSignal.timeout(8000) });
    if (response.ok) {
      const cache = await caches.open(API_CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request, { cacheName: API_CACHE_NAME });
    if (cached) {
      // Add stale header for UI to show "using cached data"
      const headers = new Headers(cached.headers);
      headers.set('X-AirSense-Cache', 'stale');
      const body = await cached.json().catch(() => ({}));
      return new Response(JSON.stringify(body), { headers, status: 200 });
    }
    return new Response(JSON.stringify({ error: 'Offline — no cached data available', cached: false }), {
      status: 503, headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Strategy: Network-first with offline HTML fallback
async function networkFirstWithOfflineFallback(request) {
  try {
    return await fetch(request);
  } catch {
    const cached = await caches.match(request);
    if (cached) return cached;
    return caches.match('/__offline');
  }
}

// Strategy: Stale-while-revalidate
async function staleWhileRevalidate(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);
  const networkFetch = fetch(request).then(response => {
    if (response.ok) cache.put(request, response.clone());
    return response;
  });
  return cached || networkFetch;
}

// ── Push Notifications ───────────────────────────────────────────────────────
self.addEventListener('push', (event) => {
  let data = { title: 'AirSense Alert', body: 'Check your local AQI levels.', icon: '/static/manifest.json' };
  if (event.data) {
    try { data = { ...data, ...event.data.json() }; } catch {}
  }

  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: data.icon || '',
      badge: '',
      tag: 'airsense-aqi-alert',
      requireInteraction: false,
      data: { url: data.url || '/' },
      actions: [
        { action: 'view', title: 'View Dashboard' },
        { action: 'dismiss', title: 'Dismiss' }
      ]
    })
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  if (event.action === 'dismiss') return;
  const url = event.notification.data?.url || '/';
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(clientList => {
      const existing = clientList.find(c => c.url === url);
      if (existing) return existing.focus();
      return clients.openWindow(url);
    })
  );
});

// ── Background AQI threshold check (triggered by app.js via SW message) ──────
self.addEventListener('message', (event) => {
  if (event.data?.type === 'AQI_THRESHOLD_CHECK') {
    const { aqi, threshold, station } = event.data;
    if (aqi >= threshold) {
      self.registration.showNotification('⚠️ AQI Alert — AirSense', {
        body: `${station}: AQI is ${Math.round(aqi)} — exceeds your threshold of ${threshold}. Limit outdoor exposure.`,
        tag: 'airsense-threshold',
        requireInteraction: false
      });
    }
  }
});
