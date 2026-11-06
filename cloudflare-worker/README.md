# Cloudflare Worker Edge Proxy for Root VPS

Yeh Cloudflare Worker aapke Koyeb, Railway, ya Docker VPS ke samne ek fast, secure Edge Proxy aur WebSocket Gateway ka kaam karta hai.

---

### Kyun Use Karein?
1. **Custom Domain ya `*.workers.dev` URL**: Cloudflare ke global network se access milega.
2. **WebSocket Support**: `ttyd` web terminal bina kisi delay ke fast chalta hai.
3. **DDoS Protection**: Cloudflare ka automatic security layer milta hai.
4. **Extra Password / Token Protection**: Edge level par hi unauthorized users block ho jate hain.

---

### Deploy Kaise Karein:

#### Option 1: Cloudflare Dashboard se (Bina CLI ke)
1. [Cloudflare Dashboard](https://dash.cloudflare.com/) me login karein.
2. **Workers & Pages** -> **Create Application** -> **Create Worker** par click karein.
3. Code editor me `worker.js` ka code paste karein.
4. **Settings** -> **Variables and Secrets** me jayein aur Add Variable:
   - Variable Name: `BACKEND_URL`
   - Value: `https://your-app.koyeb.app` (Apka Koyeb ya Railway URL)
5. **Deploy** par click karein!

#### Option 2: Wrangler CLI se
```bash
cd cloudflare-worker
npm install -g wrangler
wrangler login
# wrangler.toml me BACKEND_URL update karein
wrangler deploy
```
