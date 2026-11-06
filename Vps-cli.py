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
    except Exception as e:
        print(f"[✗] Error connecting to {url}: {e}")

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
    print("  1. gen-pass              Generate a strong random root password")
    print("  2. check <URL>           Check if your Koyeb/Railway/Cloudflare VPS is online")
    print("  3. docker-run            Build and run container locally with Docker")
    print("  4. help                  Show this help menu")
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

    if action in ("gen-pass", "password"):
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
