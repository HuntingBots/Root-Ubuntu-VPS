#!/usr/bin/env python3
"""
Root Ubuntu VPS - Multi-Plan Manager & Credential Controller
Author: Hunting Bots
Manage different IPs, ports, and unique passwords for all 5 VPS instances.
Compatible with ANY device (Termius, PuTTY, Terminal, Web Browser).
"""

import sys
import os
import subprocess
import socket

BANNER = r"""
================================================================================
  ____             _     _   _ _                 _            __     ______  ____  
 |  _ \ ___   ___ | |_  | | | | |__  _   _ _ __ | |_ _   _    \ \   / /  _ \/ ___| 
 | |_) / _ \ / _ \| __| | | | | '_ \| | | | '_ \| __| | | |    \ \ / /| |_) \___ \ 
 |  _ < (_) | (_) | |_  | |_| | |_) | |_| | | | | |_| |_| |     \ V / |  __/ ___) |
 |_| \_\___/ \___/ \__|  \___/|_.__/ \__,_|_| |_|\__|\__,_|      \_/  |_|   |____/ 
                                                                                   
        Multi-VPS Plans Controller (Unique IP / Hostname, Port & Password)
================================================================================
"""

VPS_CONFIG = {
    1: {
        "plan": "Plan 1",
        "container": "root-ubuntu-vps-2",
        "ram": "4GB",
        "cpu": "2 vCore",
        "storage": "80GB NVMe",
        "ssh_port": 2223,
        "web_port": 7682,
        "password": "Plan1@RootVps24",
        "public_host": "vps1.85-190-114-54.sslip.io",
    },
    2: {
        "plan": "Plan 2",
        "container": "root-ubuntu-vps-1",
        "ram": "8GB",
        "cpu": "4 vCore",
        "storage": "200GB NVMe",
        "ssh_port": 2222,
        "web_port": 7681,
        "password": "Plan2@RootVps24",
        "public_host": "vps2.85-190-114-54.sslip.io",
    },
    3: {
        "plan": "Plan 3",
        "container": "root-ubuntu-vps-3",
        "ram": "16GB",
        "cpu": "8 vCore",
        "storage": "300GB NVMe",
        "ssh_port": 2224,
        "web_port": 7683,
        "password": "Plan3@RootVps24",
        "public_host": "vps3.85-190-114-54.sslip.io",
    },
    4: {
        "plan": "Plan 4",
        "container": "root-ubuntu-vps-4",
        "ram": "24GB",
        "cpu": "12 vCore",
        "storage": "400GB NVMe",
        "ssh_port": 2225,
        "web_port": 7684,
        "password": "Plan4@RootVps24",
        "public_host": "vps4.85-190-114-54.sslip.io",
    },
    5: {
        "plan": "Plan 5",
        "container": "root-ubuntu-vps-5",
        "ram": "32GB",
        "cpu": "16 vCore",
        "storage": "500GB NVMe",
        "ssh_port": 2226,
        "web_port": 7685,
        "password": "Plan5@RootVps24",
        "public_host": "vps5.85-190-114-54.sslip.io",
    },
}

PUBLIC_IP = "85.190.114.54"

def get_tailscale_ip(container):
    try:
        ip = subprocess.check_output(
            ["docker", "exec", container, "tailscale", "ip", "-4"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        return ip if ip else "Not Connected"
    except Exception:
        return "Offline"

def get_cloudflare_url(container):
    try:
        url = subprocess.check_output(
            ["docker", "exec", container, "sh", "-c", "grep -o 'https://[-a-zA-Z0-9@:%._\\+~#=]*\\.trycloudflare\\.com' /tmp/cloudflared.log 2>/dev/null | head -n 1"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        return url if url else "Not active"
    except Exception:
        return "Offline"

def show_all_plans():
    print(BANNER)
    print(f"Server Primary IPv4: {PUBLIC_IP}")
    print("=" * 80)
    for num, v in sorted(VPS_CONFIG.items()):
        cname = v["container"]
        ts_ip = get_tailscale_ip(cname)
        cf_url = get_cloudflare_url(cname)

        print(f"\n🔹 【 {v['plan']} 】 — {cname.upper()}")
        print(f"   ├─ Hardware:       {v['ram']} RAM | {v['cpu']} | {v['storage']}")
        print(f"   ├─ Root Password:  {v['password']}")
        print(f"   ├─ Unique Host:    {v['public_host']}  (or {PUBLIC_IP})")
        print(f"   ├─ SSH Port:       {v['ssh_port']}")
        print(f"   ├─ Web Port:       {v['web_port']}")
        print(f"   ├─ Tailscale IP:   {ts_ip} (SSH Port: 22)")
        print(f"   ├─ Web Terminal:   {cf_url}")
        print(f"   └─ SSH Command:    ssh root@{PUBLIC_IP} -p {v['ssh_port']}")
    print("\n" + "=" * 80)
    print("💡 Yeh details kisi bhi phone/laptop/Termius/PuTTY me direct kaam karengi!")

def test_ssh_all():
    print(BANNER)
    print("[*] Testing live SSH authentication for all 5 VPS...")
    all_ok = True
    for num, v in sorted(VPS_CONFIG.items()):
        cmd = [
            "sshpass", "-p", v["password"],
            "ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=4",
            "-p", str(v["ssh_port"]), f"root@127.0.0.1", "echo SUCCESS"
        ]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=6)
            if "SUCCESS" in r.stdout:
                print(f"[✓] {v['plan']} ({v['container']}) Port {v['ssh_port']} -> AUTH OK! (Password Verified)")
            else:
                print(f"[✗] {v['plan']} ({v['container']}) Port {v['ssh_port']} -> FAILED ({r.stderr.strip()})")
                all_ok = False
        except Exception as e:
            print(f"[✗] {v['plan']} ({v['container']}) Port {v['ssh_port']} -> ERROR ({e})")
            all_ok = False

    print("\n[✓] All VPS SSH Tests Passed!" if all_ok else "\n[!] Some tests failed.")

def apply_passwords():
    print(BANNER)
    print("[*] Updating passwords in running containers...")
    for num, v in sorted(VPS_CONFIG.items()):
        cname = v["container"]
        pwd = v["password"]
        try:
            subprocess.run(
                ["docker", "exec", cname, "sh", "-c", f"echo 'root:{pwd}' | chpasswd"],
                check=True
            )
            print(f"[✓] {v['plan']} ({cname}): Password updated to '{pwd}'")
        except Exception as e:
            print(f"[✗] {v['plan']} ({cname}): Failed to update password: {e}")

def set_custom_password(plan_num, new_password):
    if plan_num not in VPS_CONFIG:
        print(f"[✗] Invalid plan number: {plan_num}. Choose 1 to 5.")
        return
    v = VPS_CONFIG[plan_num]
    cname = v["container"]
    try:
        subprocess.run(
            ["docker", "exec", cname, "sh", "-c", f"echo 'root:{new_password}' | chpasswd"],
            check=True
        )
        print(f"[✓] {v['plan']} ({cname}): Root password successfully changed to '{new_password}'")
    except Exception as e:
        print(f"[✗] Error setting password: {e}")

def print_help():
    print(BANNER)
    print("Usage:")
    print("  python3 manage_vps_plans.py show                 Display all VPS connection details")
    print("  python3 manage_vps_plans.py test                 Test live SSH login for all VPS")
    print("  python3 manage_vps_plans.py apply                Apply all predefined passwords")
    print("  python3 manage_vps_plans.py set-pass <1-5> <pwd> Set a new custom password for a VPS")
    print("=" * 80)

def main():
    if len(sys.argv) < 2:
        show_all_plans()
        sys.exit(0)

    cmd = sys.argv[1].lower()
    if cmd in ("show", "list", "plans"):
        show_all_plans()
    elif cmd in ("test", "check"):
        test_ssh_all()
    elif cmd == "apply":
        apply_passwords()
    elif cmd == "set-pass":
        if len(sys.argv) < 4:
            print("Usage: python3 manage_vps_plans.py set-pass <plan_num 1-5> <new_password>")
            sys.exit(1)
        set_custom_password(int(sys.argv[2]), sys.argv[3])
    else:
        print_help()

if __name__ == "__main__":
    main()
