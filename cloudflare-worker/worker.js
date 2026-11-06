/**
 * Cloudflare Worker - VPS Edge Gateway & WebSocket Proxy
 * 
 * Proxies HTTP & WebSocket (ttyd web terminal) traffic between Cloudflare Workers
 * and your 24/7 Root VPS running on Koyeb, Railway, Heroku, or a Docker host.
 */

export default {
  async fetch(request, env, ctx) {
    // 1. Target VPS Backend URL (Set in wrangler.toml or Cloudflare Dashboard Variables)
    const BACKEND_URL = env.BACKEND_URL || "https://your-app.koyeb.app";
    
    // 2. Parse Incoming Request
    const url = new URL(request.url);
    const targetUrl = new URL(url.pathname + url.search, BACKEND_URL);

    // 3. Optional: Access Token Protection (if ACCESS_KEY is configured)
    if (env.ACCESS_KEY) {
      const authHeader = request.headers.get("Authorization");
      const queryKey = url.searchParams.get("key");
      if (queryKey !== env.ACCESS_KEY && authHeader !== `Bearer ${env.ACCESS_KEY}`) {
        return new Response("Unauthorized: Invalid or missing ACCESS_KEY", { status: 401 });
      }
    }

    // 4. Handle WebSocket Upgrade (Critical for ttyd / terminal session)
    const upgradeHeader = request.headers.get("Upgrade");
    if (upgradeHeader && upgradeHeader.toLowerCase() === "websocket") {
      // Proxy WebSocket request directly to backend
      const newHeaders = new Headers(request.headers);
      newHeaders.set("Host", targetUrl.host);

      return fetch(targetUrl.toString(), {
        method: request.method,
        headers: newHeaders,
      });
    }

    // 5. Standard HTTP Request Proxying
    const modifiedHeaders = new Headers(request.headers);
    modifiedHeaders.set("Host", targetUrl.host);
    modifiedHeaders.set("X-Forwarded-Host", url.host);
    modifiedHeaders.set("X-Forwarded-Proto", url.protocol.replace(":", ""));

    try {
      const response = await fetch(targetUrl.toString(), {
        method: request.method,
        headers: modifiedHeaders,
        body: ["GET", "HEAD"].includes(request.method) ? null : request.body,
        redirect: "manual",
      });

      // Preserve response headers and stream body
      const newResponseHeaders = new Headers(response.headers);
      return new Response(response.body, {
        status: response.status,
        statusText: response.statusText,
        headers: newResponseHeaders,
      });
    } catch (err) {
      return new Response(`Error connecting to VPS backend: ${err.message}`, {
        status: 502,
        headers: { "Content-Type": "text/plain" },
      });
    }
  },
};
