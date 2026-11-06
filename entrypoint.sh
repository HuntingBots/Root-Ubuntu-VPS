#!/usr/bin/env bash
set -e

# ==============================================================================
# Root Ubuntu VPS - Universal Container Entrypoint
# Compatible with: Koyeb, Railway, Heroku, Docker, Cloudflare Tunnel, Tailscale
# ==============================================================================

PORT="${PORT:-7681}"
ROOT_PASSWORD="${ROOT_PASSWORD:-${PASSWORD:-huntingbots123}}"
WEB_USER="${WEB_USER:-root}"
WEB_PASSWORD="${WEB_PASSWORD:-$ROOT_PASSWORD}"

echo "=================================================================="
echo "          🚀 Starting Root Ubuntu VPS (24/7 Container)            "
echo "=================================================================="

# 1. Set root password
echo "root:${ROOT_PASSWORD}" | chpasswd
echo "[✓] Root password configured successfully."

# 2. Add public SSH key if provided
if [ -n "${SSH_KEY}" ]; then
    mkdir -p /root/.ssh
    echo "${SSH_KEY}" >> /root/.ssh/authorized_keys
    chmod 600 /root/.ssh/authorized_keys
    chmod 700 /root/.ssh
    echo "[✓] Public SSH key added to /root/.ssh/authorized_keys"
fi

# 3. Setup OpenSSH Server
mkdir -p /var/run/sshd
ssh-keygen -A >/dev/null 2>&1 || true
/usr/sbin/sshd
echo "[✓] OpenSSH Server listening on port 22."

# 4. Tailscale Integration (Dedicated Mesh IPv4)
if [ -n "${TAILSCALE_AUTHKEY}" ]; then
    echo "[*] Connecting to Tailscale Mesh Network..."
    tailscaled --tun=userspace-networking --socks5-server=localhost:1055 --outbound-http-proxy-listen=localhost:1055 >/dev/null 2>&1 &
    sleep 3
    tailscale up --authkey="${TAILSCALE_AUTHKEY}" --hostname="${TAILSCALE_HOSTNAME:-root-ubuntu-vps}" --ssh >/dev/null 2>&1 &
    echo "[✓] Tailscale service started with SSH enabled."
fi

# 5. Cloudflare Tunnel Integration
if [ -n "${TUNNEL_TOKEN}" ]; then
    echo "[*] Starting Cloudflare Zero Trust Tunnel..."
    cloudflared tunnel --no-autoupdate run --token "${TUNNEL_TOKEN}" >/tmp/cloudflared.log 2>&1 &
    echo "[✓] Cloudflare Tunnel connected."
elif [ "${QUICK_TUNNEL}" = "true" ]; then
    echo "[*] Starting Free Cloudflare Quick Tunnel (trycloudflare.com)..."
    cloudflared tunnel --url "http://127.0.0.1:${PORT}" >/tmp/cloudflared.log 2>&1 &
    sleep 4
    CF_URL=$(grep -o 'https://[-a-zA-Z0-9@:%._\+~#=]*\.trycloudflare\.com' /tmp/cloudflared.log | head -n 1 || true)
    if [ -n "${CF_URL}" ]; then
        echo "=================================================================="
        echo " [✓] Free Cloudflare Quick Tunnel URL:"
        echo "     ${CF_URL}"
        echo "=================================================================="
    fi
fi

# 6. Ngrok TCP Tunnel Integration (Direct IPv4 / Port 22 SSH)
if [ -n "${NGROK_AUTHTOKEN}" ]; then
    echo "[*] Starting Ngrok TCP Tunnel for SSH (Port 22)..."
    ngrok config add-authtoken "${NGROK_AUTHTOKEN}" >/dev/null 2>&1 || true
    ngrok tcp 22 --log=stdout >/tmp/ngrok.log 2>&1 &
    sleep 3
    NGROK_TCP=$(grep -o 'tcp://[-a-zA-Z0-9.:]*' /tmp/ngrok.log | head -n 1 || true)
    if [ -n "${NGROK_TCP}" ]; then
        echo "=================================================================="
        echo " [✓] Ngrok SSH Access:"
        echo "     ${NGROK_TCP}"
        echo "     Example: ssh root@${NGROK_TCP#tcp://}"
        echo "=================================================================="
    fi
fi

# 7. tmate Integration (Instant Public SSH)
if [ "${TMATE_ENABLED}" = "true" ]; then
    echo "[*] Starting tmate SSH session..."
    [ ! -f /root/.ssh/id_rsa ] && ssh-keygen -t rsa -N "" -f /root/.ssh/id_rsa >/dev/null 2>&1 || true
    tmate -S /tmp/tmate.sock new-session -d >/dev/null 2>&1 || true
    sleep 3
    TMATE_SSH=$(tmate -S /tmp/tmate.sock display -p '#{tmate_ssh}' 2>/dev/null || true)
    TMATE_WEB=$(tmate -S /tmp/tmate.sock display -p '#{tmate_web}' 2>/dev/null || true)
    echo "=================================================================="
    echo " [✓] tmate SSH Connection:"
    echo "     SSH: ${TMATE_SSH}"
    echo "     Web: ${TMATE_WEB}"
    echo "=================================================================="
fi

# 8. Start Web Terminal (ttyd) on $PORT
echo "=================================================================="
echo "          🌐 Web Terminal (ttyd) Ready                            "
echo "  - Port:      ${PORT}"
echo "  - Username:  ${WEB_USER}"
echo "  - Password:  ${WEB_PASSWORD}"
echo "=================================================================="

# Run ttyd in foreground to keep container running 24/7
if [ "${NO_AUTH}" = "true" ]; then
    exec ttyd -p "${PORT}" -W -t fontSize=14 -t fontFamily="monospace" bash
else
    exec ttyd -p "${PORT}" -c "${WEB_USER}:${WEB_PASSWORD}" -W -t fontSize=14 -t fontFamily="monospace" bash
fi
