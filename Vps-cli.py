#!/usr/bin/env python3
"""
Root Ubuntu VPS CLI Helper
Author: Hunting Bots
Manage, test, and generate configurations for 24/7 Root Ubuntu VPS on Koyeb, Railway, Heroku, and Cloudflare.
"""

import sys
import os
import secrets
import string
import urllib.request
import urllib.error
import subprocess

BANNER = r"""
============================================================
  ____             _     _   _ _                 _            __     ______  ____  
 |  _ \ ___   ___ | |_  | | | | |__  _   _ _ __ | |_ _   _    \ \   / /  _ \/ ___| 
 | |_) / _ \ / _ \| __| | | | | '_ \| | | | '_ \| __| | | |    \ \ / /| |_) \___ \ 
 |  _ < (_) | (_) | |_  | |_| | |_) | |_| | | | | |_| |_| |     \ V / |  __/ ___) |
 |_| \_\___/ \___/ \__|  \___/|_.__/ \__,_|_| |_|\__|\__,_|      \_/  |_|   |____/ 
                                                                                   
        24/7 Root VPS Generator & Manager (Koyeb / Railway / Docker)
============================================================
"""

VPS_PLANS = {
    1: {"name": "Plan 1", "ram": "4GB", "storage": "80GB NVMe", "cpu": "2 vCore", "web_port": 7682, "ssh_port": 2223, "service": "root-ubuntu-vps-2"},
    2: {"name": "Plan 2", "ram": "8GB", "storage": "200GB NVMe", "cpu": "4 vCore", "web_port": 7681, "ssh_port": 2222, "service": "root-ubuntu-vps-1"},
    3: {"name": "Plan 3", "ram": "16GB", "storage": "300GB NVMe", "cpu": "8 vCore", "web_port": 7683, "ssh_port": 2224, "service": "root-ubuntu-vps-3"},
    4: {"name": "Plan 4", "ram": "24GB", "storage": "400GB NVMe", "cpu": "12 vCore", "web_port": 7684, "ssh_port": 2225, "service": "root-ubuntu-vps-4"},
    5: {"name": "Plan 5", "ram": "32GB", "storage": "500GB NVMe", "cpu": "16 vCore", "web_port": 7685, "ssh_port": 2226, "service": "root-ubuntu-vps-5"},
}

def generate_password(length=16):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(chars) for _ in range(length))

def check_backend_health(url):
    print(f"\n[*] Checking backend health: {url} ...")
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (VPS-CLI-HealthCheck)"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"[✓] Server responded with HTTP status: {response.status}")
            if response.status in (200, 401): # 401 is normal for password-protected ttyd
                print("[✓] VPS Web Terminal / Gateway is ONLINE and reachable!")
            else:
                print(f"[!] Warning: Unexpected status code {response.status}")
    except urllib.error.HTTPError as e:
        if e.code in (200, 401):
            print(f"[✓] Server responded with HTTP status: {e.code}")
            print("[✓] VPS Web Terminal / Gateway is ONLINE and reachable (Auth Active)!")
        else:
            print(f"[!] Warning: HTTP error {e.code}: {e.reason}")
    except Exception as e:
        print(f"[✗] Error connecting to {url}: {e}")

def show_plans():
    print(BANNER)
    print("=" * 70)
    print("                         VPS TIERS & PLANS")
    print("=" * 70)
    for num, plan in VPS_PLANS.items():
        cname = plan["service"]
        ts_ip = "N/A"
        try:
            ts_ip = subprocess.check_output(
                ["docker", "exec", cname, "tailscale", "ip", "-4"],
                text=True, stderr=subprocess.DEVNULL
            ).strip()
        except Exception:
            pass

        print(f"\n[{plan['name']}] -> Container: {cname}")
        print(f"  • RAM:          {plan['ram']}")
        print(f"  • Storage:      {plan['storage']}")
        print(f"  • CPU:          {plan['cpu']}")
        print(f"  • Tailscale IP: {ts_ip if ts_ip else 'Not Connected'}")
        print(f"  • Web Port:     {plan['web_port']} (Web Terminal)")
        print(f"  • SSH Port:     {plan['ssh_port']} (OpenSSH)")
    print("\n" + "=" * 70)

def check_all_vps():
    print(BANNER)
    print("[*] Checking health for all 5 VPS local instances...")
    for num, plan in VPS_PLANS.items():
        url = f"http://localhost:{plan['web_port']}"
        print(f"\n--- {plan['name']} ({plan['service']} - Port {plan['web_port']}) ---")
        check_backend_health(url)

def show_vps_status():
    print(BANNER)
    print("[*] Inspecting running Docker containers, Tailscale IPs & Cloudflare Tunnels...")
    try:
        out = subprocess.check_output(
            ["docker", "ps", "--filter", "name=root-ubuntu-vps", "--format", "{{.Names}}\t{{.Status}}\t{{.Ports}}"],
            text=True
        )
        print("\nRunning Containers:")
        print(out if out.strip() else "No active root-ubuntu-vps containers found.")
    except Exception as e:
        print(f"[✗] Could not query docker: {e}")

    print("\nTailscale Dedicated IPs & Cloudflare Quick Tunnels:")
    for num, plan in sorted(VPS_PLANS.items()):
        cname = plan["service"]
        ts_ip = "N/A"
        cf = "Not active"
        try:
            ts_ip = subprocess.check_output(
                ["docker", "exec", cname, "tailscale", "ip", "-4"],
                text=True, stderr=subprocess.DEVNULL
            ).strip()
        except Exception:
            pass
        try:
            cf = subprocess.check_output(
                ["docker", "exec", cname, "sh", "-c", "grep -o 'https://[-a-zA-Z0-9@:%._\\+~#=]*\\.trycloudflare\\.com' /tmp/cloudflared.log 2>/dev/null | head -n 1"],
                text=True
            ).strip()
        except Exception:
            pass

        print(f"  [{plan['name']}] ({cname}):")
        print(f"      • Tailscale Dedicated IPv4: {ts_ip if ts_ip else 'N/A'}")
        print(f"      • Cloudflare Tunnel:        {cf if cf else 'Offline'}")

def run_local_docker():
    print("\n[*] Starting local Docker container for Root Ubuntu VPS...")
    cmd = [
        "docker", "run", "-d",
        "--name", "root-ubuntu-vps",
        "--restart", "unless-stopped",
        "-p", "7681:7681",
        "-p", "2222:22",
        "-e", f"ROOT_PASSWORD={generate_password()}",
        "-e", "PORT=7681",
        "root-ubuntu-vps"
    ]
    try:
        subprocess.run(["docker", "build", "-t", "root-ubuntu-vps", "."], check=True)
        subprocess.run(cmd, check=True)
        print("[✓] Container started successfully!")
        print("    Web Terminal: http://localhost:7681")
        print("    SSH Port:     localhost:2222")
    except Exception as e:
        print(f"[✗] Docker execution failed: {e}")

def print_help():
    print(BANNER)
    print("Available Commands:")
    print("  1. plans                 Show all 5 VPS Plans with specs and Tailscale IPs")
    print("  2. status                Show status, Tailscale IPs & Cloudflare URLs for all 5 VPS")
    print("  3. check-all             Health-check all 5 VPS web terminals")
    print("  4. check <URL>           Check if a specific VPS URL is online")
    print("  5. gen-pass              Generate a strong random root password")
    print("  6. docker-run            Build and run a single container locally with Docker")
    print("  7. help                  Show this help menu")
    print("\nEnvironment Variables Supported:")
    print("  - ROOT_PASSWORD          Root & Web Terminal password (default: HuntingBots123!)")
    print("  - PORT                   Port for Web Terminal (default: 7681 or assigned by host)")
    print("  - TUNNEL_TOKEN           Cloudflare Zero Trust Tunnel token")
    print("  - QUICK_TUNNEL=true      Auto-generate free TryCloudflare tunnel URL")
    print("  - TAILSCALE_AUTHKEY      Tailscale Auth Key for dedicated mesh IPv4")
    print("  - NGROK_AUTHTOKEN        Ngrok Auth Token for public SSH port 22 IPv4")
    print("  - TMATE_ENABLED=true     Instant SSH session via tmate")
    print("=" * 60)

def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    action = sys.argv[1].lower()

    if action == "plans":
        show_plans()
    elif action == "status":
        show_vps_status()
    elif action == "check-all":
        check_all_vps()
    elif action in ("gen-pass", "password"):
        pwd = generate_password()
        print(f"\nGenerated Strong Password: {pwd}\n")
    elif action == "check":
        if len(sys.argv) < 3:
            print("Usage: python3 Vps-cli.py check <URL>")
            sys.exit(1)
        check_backend_health(sys.argv[2])
    elif action == "docker-run":
        run_local_docker()
    else:
        print_help()

if __name__ == "__main__":
    main()
