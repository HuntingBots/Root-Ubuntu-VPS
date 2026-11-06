# 🚀 24/7 Root Ubuntu VPS (Universal Docker & Cloudflare Integration)

[![Ubuntu 22.04 LTS](https://img.shields.io/badge/Ubuntu-22.04_LTS-E95420?logo=ubuntu&logoColor=white)](https://ubuntu.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Cloudflare](https://img.shields.io/badge/Cloudflare-Tunnel_%26_Workers-F38020?logo=cloudflare&logoColor=white)](https://cloudflare.com/)
[![Tailscale](https://img.shields.io/badge/Tailscale-Mesh_IPv4-24292E?logo=tailscale&logoColor=white)](https://tailscale.com/)

Ek **Universal 24/7 Root Ubuntu VPS Server** jo **Koyeb**, **Railway**, **Heroku**, **Render**, aur **Docker Hosts** par chal sakta hai, aur **Cloudflare Workers / Cloudflare Zero Trust Tunnel** ke sath connect hokar direct Web Terminal aur Dedicated IPv4 SSH provide karta hai.

---

## 📌 Sachai: Cloudflare Workers & Vercel vs Koyeb & Railway

Bohot se log confuse hote hain ki kya Cloudflare Workers ya Vercel par direct Root VPS ban sakta hai:

| Platform | Real Linux Kernel? | Root (Sudo) Access? | 24/7 Background Process? | Direct IPv4 SSH? | Best Use Case |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Cloudflare Workers** | ❌ No (V8 JS Isolate) | ❌ No | ❌ No (50ms CPU limit) | ❌ No | Edge Reverse Proxy & WebSocket Gateway |
| **Vercel** | ❌ No (AWS Lambda) | ❌ No | ❌ No (10-60s timeout) | ❌ No | Frontend & Edge API Proxy |
| **Koyeb** | ✅ **Yes (Docker)** | ✅ **Yes (Full Root)** | ✅ **Yes (24/7 Active)** | ✅ Yes (Tunnel/Web) | **Best Free 24/7 Root VPS** |
| **Railway** | ✅ **Yes (Docker)** | ✅ **Yes (Full Root)** | ✅ **Yes (24/7 Active)** | ✅ Yes (Tunnel/Web) | **High Performance 24/7 Root VPS** |
| **Heroku / Render** | ✅ **Yes (Docker)** | ✅ **Yes (Full Root)** | ✅ **Yes (Active)** | ✅ Yes (Tunnel/Web) | **Container Hosting** |

> [!IMPORTANT]
> **Cloudflare Workers aur Vercel** serverless hote hain (unme Linux OS nahi hota).
> **Best Solution:** Aapka Root Ubuntu container **Koyeb ya Railway** par 24/7 run hota hai, aur **Cloudflare Workers** ya **Cloudflare Tunnel** uske aage Edge Proxy / Custom Domain ban kar Web Terminal aur IPv4 connectivity provide karta hai!

---

## ✨ Features

- 🐧 **Full Root Ubuntu 22.04 LTS**: `sudo`, `apt`, `systemctl/service`, `bash`, python3, nodejs, git, gcc pre-installed.
- 🌐 **Web Terminal (ttyd)**: Kisi bhi browser me `https://your-app.koyeb.app` open karke direct Root Shell chalao (Password protected).
- 🔒 **Cloudflare Zero Trust Tunnel (`cloudflared`)**: Direct Cloudflare domain aur Web SSH access bina kisi open port ke.
- ⚡ **Free Quick Tunnel (TryCloudflare)**: Ek click me free temporary `.trycloudflare.com` URL.
- 📡 **Dedicated Mesh IPv4 (Tailscale)**: Container ko apna private Tailscale IPv4 (`100.x.y.z`) milta hai jisse direct `ssh root@100.x.y.z` kar sakte ho.
- 🔌 **Public IPv4 SSH (Ngrok & tmate)**: PuTTY ya Terminal se connect karne ke liye instant public IP/host aur port.
- 🛡️ **Cloudflare Worker Gateway**: Pre-built Cloudflare Worker reverse proxy script WebSocket support ke sath.

---

## 🚀 Quick Deployment Guide

### 1. Deploy on Koyeb (Free 24/7)

1. [Koyeb](https://www.koyeb.com/) par account banayein aur **Create App** par click karein.
2. Deployment method select karein: **GitHub**.
3. Apna repository select karein: `Root-Ubuntu-VPS`.
4. Settings check karein:
   - **Builder**: `Dockerfile`
   - **Port**: `7681` (Path: `/`)
5. **Environment Variables** add karein:
   - `ROOT_PASSWORD` = `ApnaStrongPassword123!`
   - *(Optional)* `TUNNEL_TOKEN` = `Cloudflare_Zero_Trust_Token`
   - *(Optional)* `TAILSCALE_AUTHKEY` = `tskey-auth-...`
   - *(Optional)* `NGROK_AUTHTOKEN` = `ngrok_token`
6. **Deploy** par click karein!
7. Deployment complete hone ke baad `https://<your-app>.koyeb.app` open karein aur login karein:
   - **Username**: `root`
   - **Password**: Aapka set kiya hua password.

---

### 2. Deploy on Railway

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/new)

1. [Railway.com](https://railway.com/) dashboard me **New Project** -> **Deploy from GitHub Repo** select karein.
2. `Root-Ubuntu-VPS` repository choose karein.
3. **Variables** tab me `ROOT_PASSWORD` define karein.
4. **Networking** tab me **Generate Domain** par click karein.
5. Domain par open karke root terminal access karein!

---

### 3. Deploy on Heroku

```bash
# Heroku CLI me login karein
heroku login
heroku container:login

# Heroku App banayein
heroku create my-root-vps

# Docker container push aur release karein
heroku container:push web -a my-root-vps
heroku container:release web -a my-root-vps

# Root password set karein
heroku config:set ROOT_PASSWORD=YourPassword123! -a my-root-vps
```

---

### 4. Connect Cloudflare Workers (Edge Gateway)

Agar aap apne Koyeb / Railway VPS ke samne **Cloudflare Workers** ka URL (`*.workers.dev`) lagana chahte hain:

1. `cloudflare-worker/` folder me jayein.
2. `wrangler.toml` file me `BACKEND_URL` apna Koyeb/Railway URL daalein:
   ```toml
   [vars]
   BACKEND_URL = "https://your-app.koyeb.app"
   ```
3. Cloudflare Dashboard me Worker banayein aur `cloudflare-worker/worker.js` ka code paste karke Deploy kar dein.
4. Ab aapka Cloudflare Worker saari traffic aur WebSockets direct VPS terminal par route karega!

---

### 5. Dedicated Mesh IPv4 SSH via Tailscale

Tailscale use karke aapko dedicated static IPv4 milta hai jisse aap Termius ya PuTTY se SSH kar sakte hain:

1. [Tailscale.com](https://tailscale.com/) par account banayein.
2. **Settings** -> **Keys** -> **Generate auth key** (Reusable check karein).
3. Koyeb / Railway me Environment Variable add karein:
   - Key: `TAILSCALE_AUTHKEY`
   - Value: `tskey-auth-kxxxxxxxxxxxx`
4. Container restart hone par aapke Tailscale dashboard me `root-ubuntu-vps` dikhai dega with IPv4 (e.g., `100.85.24.12`).
5. Direct connect karein:
   ```bash
   ssh root@100.85.24.12
   ```

---

### 6. Public IPv4 SSH via Ngrok

Agar aapko normal public IPv4 aur port chahiye bina Tailscale ke:
1. [Ngrok.com](https://ngrok.com/) par sign up karke auth token copy karein.
2. Environment Variable add karein:
   - `NGROK_AUTHTOKEN` = `your_token_here`
3. Koyeb / Railway ke logs me dekhein:
   ```text
   [✓] Ngrok SSH Access: tcp://4.tcp.ngrok.io:12345
   ```
4. Terminal me connect karein:
   ```bash
   ssh root@4.tcp.ngrok.io -p 12345
   ```

---

### 7. Run Locally / On Any Server (Docker Compose)

```bash
# Clone the repository
git clone https://github.com/HuntingBots/Root-Ubuntu-VPS.git
cd Root-Ubuntu-VPS

# Start the container
docker compose up -d

# Check status
python3 Vps-cli.py check http://localhost:7681
```

---

## ⚙️ Environment Variables Reference

| Variable | Description | Default | Required? |
| :--- | :--- | :--- | :---: |
| `ROOT_PASSWORD` | VPS Root aur Web Terminal password | `HuntingBots123!` | Recommended |
| `PORT` | Web Terminal (ttyd) port | `7681` (Auto-detected on Koyeb/Railway) | No |
| `TUNNEL_TOKEN` | Cloudflare Zero Trust Tunnel Token | None | Optional |
| `QUICK_TUNNEL` | Auto-generate free TryCloudflare URL (`true`/`false`) | `false` | Optional |
| `TAILSCALE_AUTHKEY` | Tailscale Auth Key (Dedicated Mesh IPv4) | None | Optional |
| `NGROK_AUTHTOKEN` | Ngrok Auth Token (Public Port 22 SSH) | None | Optional |
| `TMATE_ENABLED` | Instant SSH via tmate (`true`/`false`) | `false` | Optional |
| `SSH_KEY` | Public SSH Key string to auto-inject | None | Optional |

---

## 🛠️ Python CLI Helper (`Vps-cli.py`)

Is repo me ek CLI helper bhi shamil hai:

```bash
# Strong password generate karein
python3 Vps-cli.py gen-pass

# VPS server online status check karein
python3 Vps-cli.py check https://your-app.koyeb.app

# Local Docker run karein
python3 Vps-cli.py docker-run
```

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
