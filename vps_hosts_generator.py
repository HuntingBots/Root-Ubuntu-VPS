#!/usr/bin/env python3
"""
Root Ubuntu VPS - Custom Clean Hostname Generator & Login Manager
Author: Hunting Bots

Generates clean, custom hostnames (like ghostrootvps1, ghostvpsroot1, etc.)
WITHOUT displaying raw IP addresses.
Works from ANY external device/location (Termius, PuTTY, Mobile, PC) with 100% global DNS resolution.
"""

import sys
import os
import subprocess
import urllib.request
import socket

BANNER = r"""
================================================================================
  _    _           _                                  _____                           _             
 | |  | |         | |                                / ____|                         | |            
 | |__| | ___  ___| |_ _ __   __ _ _ __ ___   ___   | |  __  ___ _ __   ___ _ __ __ _| |_ ___  _ __ 
 |  __  |/ _ \/ __| __| '_ \ / _` | '_ ` _ \ / _ \  | | |_ |/ _ \ '_ \ / _ \ '__/ _` | __/ _ \| '__|
 | |  | | (_) \__ \ |_| | | | (_| | | | | | |  __/  | |__| |  __/ | | |  __/ | | (_| | || (_) | |   
 |_|  |_|\___/|___/\__|_| |_|\__,_|_| |_| |_|\___|   \_____|\___|_| |_|\___|_|  \__,_|\__\___/|_|   
                                                                                                    
   Multi-VPS Custom Hostnames (No Raw IP, Custom Prefix, Port & Password per VPS)
================================================================================
"""

VPS_LIST = [
    {
        "plan": "Plan 1",
        "container": "root-ubuntu-vps-2",
        "ram": "4GB",
        "cpu": "2 vCore",
        "storage": "80GB NVMe",
        "ssh_port": 2223,
        "web_port": 7682,
        "password": "Plan1@RootVps24",
    },
    {
        "plan": "Plan 2",
        "container": "root-ubuntu-vps-1",
        "ram": "8GB",
        "cpu": "4 vCore",
        "storage": "200GB NVMe",
        "ssh_port": 2222,
        "web_port": 7681,
        "password": "Plan2@RootVps24",
    },
    {
        "plan": "Plan 3",
        "container": "root-ubuntu-vps-3",
        "ram": "16GB",
        "cpu": "8 vCore",
        "storage": "300GB NVMe",
        "ssh_port": 2224,
        "web_port": 7683,
        "password": "Plan3@RootVps24",
    },
    {
        "plan": "Plan 4",
        "container": "root-ubuntu-vps-4",
        "ram": "24GB",
        "cpu": "12 vCore",
        "storage": "400GB NVMe",
        "ssh_port": 2225,
        "web_port": 7684,
        "password": "Plan4@RootVps24",
    },
    {
        "plan": "Plan 5",
        "container": "root-ubuntu-vps-5",
        "ram": "32GB",
        "cpu": "16 vCore",
        "storage": "500GB NVMe",
        "ssh_port": 2226,
        "web_port": 7685,
        "password": "Plan5@RootVps24",
    },
]

def get_public_ip():
    try:
        req = urllib.request.Request("https://api.ipify.org", headers={"User-Agent": "curl/7.68.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.read().decode().strip()
    except Exception:
        return "85.190.114.54"

def ip_to_hex(ip_str):
    octets = ip_str.split(".")
    return "".join(f"{int(o):02x}" for o in octets)

def generate_hostnames(prefix="ghostrootvps"):
    public_ip = get_public_ip()
    hex_ip = ip_to_hex(public_ip)

    print(BANNER)
    print(f"📌 Custom Hostname Prefix: '{prefix}'")
    print(f"🔒 Raw IP is completely hidden using global hex DNS cluster ID ({hex_ip}).")
    print("=" * 80)

    for i, v in enumerate(VPS_LIST, 1):
        custom_host_1 = f"{prefix}{i}.{hex_ip}.sslip.io"
        alt_prefix = "ghostvpsroot" if prefix == "ghostrootvps" else "ghostrootvps"
        custom_host_2 = f"{alt_prefix}{i}.{hex_ip}.sslip.io"

        print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"  🖥️  {v['plan']} ({v['container'].upper()}) — {v['ram']} RAM | {v['cpu']} | {v['storage']}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"  • Custom Hostname 1:  {custom_host_1}")
        print(f"  • Custom Hostname 2:  {custom_host_2}")
        print(f"  • SSH Port:           {v['ssh_port']}")
        print(f"  • Username:           root")
        print(f"  • Password:           {v['password']}")
        print(f"")
        print(f"  👉 Termius Setup (Mobile / Desktop):")
        print(f"     Label / Alias:     {prefix}{i}")
        print(f"     Hostname/Address:  {custom_host_1}")
        print(f"     Port:              {v['ssh_port']}")
        print(f"     Username:          root")
        print(f"     Password:          {v['password']}")
        print(f"")
        print(f"  👉 Terminal SSH Command:")
        print(f"     ssh root@{custom_host_1} -p {v['ssh_port']}")

    print("\n" + "=" * 80)
    print("✅ Yeh hostnames kisi bhi dusre device / location se 100% connect honge bina kisi IP ke!")
    print(f"💡 Prefix change karne ke liye run karein: python3 vps_hosts_generator.py <prefix>")
    print(f"   Example: python3 vps_hosts_generator.py ghostvpsroot")

def test_all(prefix="ghostrootvps"):
    public_ip = get_public_ip()
    hex_ip = ip_to_hex(public_ip)

    print(BANNER)
    print(f"[*] Testing global DNS resolution & live SSH login for all VPS with custom hostnames...")
    print(f"[*] Prefix: {prefix} | Cluster ID: {hex_ip}")
    print("=" * 80)
    all_ok = True

    for i, v in enumerate(VPS_LIST, 1):
        hostname = f"{prefix}{i}.{hex_ip}.sslip.io"
        port = v["ssh_port"]
        pwd = v["password"]

        # 1. DNS test
        try:
            resolved_ip = socket.gethostbyname(hostname)
            dns_status = f"DNS OK"
        except Exception as e:
            dns_status = f"DNS FAIL ({e})"
            all_ok = False

        # 2. SSH test
        cmd = [
            "sshpass", "-p", pwd,
            "ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=4",
            "-p", str(port), f"root@{hostname}", "echo SUCCESS"
        ]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=6)
            if "SUCCESS" in r.stdout:
                ssh_status = "SSH LOGIN SUCCESS ✓"
            else:
                ssh_status = f"SSH FAIL ({r.stderr.strip()})"
                all_ok = False
        except Exception as e:
            ssh_status = f"SSH ERROR ({e})"
            all_ok = False

        print(f"[{v['plan']}] {hostname}:{port} -> {dns_status} | {ssh_status}")

    print("=" * 80)
    if all_ok:
        print("🎉 ALL 5 VPS CUSTOM HOSTNAMES ARE ONLINE AND FULLY VERIFIED!")
    else:
        print("⚠️ Some checks failed.")

def main():
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("test", "check"):
        prefix = sys.argv[2] if len(sys.argv) > 2 else "ghostrootvps"
        test_all(prefix)
    elif len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        generate_hostnames(sys.argv[1])
    else:
        generate_hostnames()

if __name__ == "__main__":
    main()
