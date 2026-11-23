#!/usr/bin/env python3
"""
Root Ubuntu VPS - Multi-Plan Manager & Dynamic Credential Controller
Author: Hunting Bots

Manages unique credentials, ports, and custom hostnames for all VPS instances.
Automatically generates and keeps 'vps_details.md' updated whenever any VPS
is created, modified, or listed.
Compatible with ANY device (Termius, PuTTY, Terminal, Web Browser).
"""

import sys
import os
import subprocess
import socket
import json
import datetime
import urllib.request

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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLANS_FILE = os.path.join(BASE_DIR, "vps_plans.json")
DETAILS_MD_FILE = os.path.join(BASE_DIR, "vps_details.md")
PUBLIC_IP = "85.190.114.54"
HEX_CLUSTER_ID = "55be7236"

DEFAULT_PLANS = {
    "1": {
        "plan": "Plan 1",
        "container": "root-ubuntu-vps-2",
        "ram": "4GB",
        "cpu": "2 vCore",
        "storage": "80GB NVMe",
        "ssh_port": 2223,
        "web_port": 7682,
        "password": "Plan1@RootVps24",
        "public_host": "ghostrootvps1.55be7236.sslip.io",
        "alt_host": "ghostvpsroot1.55be7236.sslip.io",
    },
    "2": {
        "plan": "Plan 2",
        "container": "root-ubuntu-vps-1",
        "ram": "8GB",
        "cpu": "4 vCore",
        "storage": "200GB NVMe",
        "ssh_port": 2222,
        "web_port": 7681,
        "password": "Plan2@RootVps24",
        "public_host": "ghostrootvps2.55be7236.sslip.io",
        "alt_host": "ghostvpsroot2.55be7236.sslip.io",
    },
    "3": {
        "plan": "Plan 3",
        "container": "root-ubuntu-vps-3",
        "ram": "16GB",
        "cpu": "8 vCore",
        "storage": "300GB NVMe",
        "ssh_port": 2224,
        "web_port": 7683,
        "password": "Plan3@RootVps24",
        "public_host": "ghostrootvps3.55be7236.sslip.io",
        "alt_host": "ghostvpsroot3.55be7236.sslip.io",
    },
    "4": {
        "plan": "Plan 4",
        "container": "root-ubuntu-vps-4",
        "ram": "24GB",
        "cpu": "12 vCore",
        "storage": "400GB NVMe",
        "ssh_port": 2225,
        "web_port": 7684,
        "password": "Plan4@RootVps24",
        "public_host": "ghostrootvps4.55be7236.sslip.io",
        "alt_host": "ghostvpsroot4.55be7236.sslip.io",
    },
    "5": {
        "plan": "Plan 5",
        "container": "root-ubuntu-vps-5",
        "ram": "32GB",
        "cpu": "16 vCore",
        "storage": "500GB NVMe",
        "ssh_port": 2226,
        "web_port": 7685,
        "password": "Plan5@RootVps24",
        "public_host": "ghostrootvps5.55be7236.sslip.io",
        "alt_host": "ghostvpsroot5.55be7236.sslip.io",
    },
}

def load_plans():
    if os.path.exists(PLANS_FILE):
        try:
            with open(PLANS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_PLANS.copy()

def save_plans(plans):
    with open(PLANS_FILE, "w") as f:
        json.dump(plans, f, indent=2)

def get_container_status(container):
    try:
        r = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Status}}", container],
            capture_output=True, text=True, timeout=3
        )
        status = r.stdout.strip()
        return status if status else "offline"
    except Exception:
        return "offline"

def get_tailscale_ip(container):
    try:
        ip = subprocess.check_output(
            ["docker", "exec", container, "tailscale", "ip", "-4"],
            text=True, stderr=subprocess.DEVNULL, timeout=4
        ).strip()
        return ip if ip else "Not Connected"
    except Exception:
        return "Offline"

def get_cloudflare_url(container):
    try:
        cmd = "grep -o 'https://[-a-zA-Z0-9@:%._\\+~#=]*\\.trycloudflare\\.com' /tmp/cloudflared.log 2>/dev/null | head -n 1"
        url = subprocess.check_output(
            ["docker", "exec", container, "sh", "-c", cmd],
            text=True, stderr=subprocess.DEVNULL, timeout=4
        ).strip()
        return url if url else "Not active"
    except Exception:
        return "Offline"

def update_vps_details_md():
    """Generates / updates vps_details.md with all available VPS specs and credentials."""
    plans = load_plans()
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = []
    lines.append("# 🌐 Root Ubuntu VPS - Active VPS Details & Connection Guide\n")
    lines.append(f"> **Last Auto-Updated:** `{now_str}`  \n")
    lines.append(f"> **Cluster ID:** `{HEX_CLUSTER_ID}` (Raw IP hidden in global DNS)  \n")
    lines.append(f"> **Total Configured VPS:** `{len(plans)}`\n")
    lines.append("\n---\n")

    lines.append("## ⚡ Quick Reference Table (All Active VPS)\n\n")
    lines.append("| Plan | Container | RAM | CPU | Storage | Custom Hostname | Port | Username | Password | Status |\n")
    lines.append("| :--- | :--- | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: |\n")

    cards = []
    termius_entries = []

    for num in sorted(plans.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        v = plans[num]
        cname = v.get("container", f"root-ubuntu-vps-{num}")
        ram = v.get("ram", "N/A")
        cpu = v.get("cpu", "N/A")
        storage = v.get("storage", "N/A")
        host = v.get("public_host", f"ghostrootvps{num}.{HEX_CLUSTER_ID}.sslip.io")
        alt_host = v.get("alt_host", f"ghostvpsroot{num}.{HEX_CLUSTER_ID}.sslip.io")
        port = v.get("ssh_port", 2222)
        web_port = v.get("web_port", 7681)
        pwd = v.get("password", "root")
        status = get_container_status(cname)
        ts_ip = get_tailscale_ip(cname)
        cf_url = get_cloudflare_url(cname)

        status_badge = "🟢 Running" if status == "running" else f"🔴 {status.title()}"

        lines.append(
            f"| **{v.get('plan', f'Plan {num}')}** | `{cname}` | {ram} | {cpu} | {storage} | `{host}` | **`{port}`** | `root` | `{pwd}` | {status_badge} |\n"
        )

        termius_entries.append(
            f"| `{v.get('plan', f'Plan {num}')}` | `ghostrootvps{num}` | `{host}` | **`{port}`** | `root` | `{pwd}` |\n"
        )

        # Build detailed card
        card = f"""### 🖥️ {v.get('plan', f'Plan {num}')} (`{cname}`) - {ram} RAM | {cpu} | {storage}
- **Status**: {status_badge}
- **Username**: `root`
- **Password**: `{pwd}`
- **SSH Port**: `{port}`
- **Primary Hostname (Global DNS)**: `{host}`
- **Alternate Hostname**: `{alt_host}`
- **Dedicated Tailscale IPv4**: `{ts_ip}` (SSH Port `22`)
- **Web Terminal (ttyd)**: `{cf_url}` (or `http://{host}:{web_port}`)

**Direct SSH Commands**:
```bash
# Via Custom Global Hostname (Any device / location, No VPN required):
ssh root@{host} -p {port}

# Via Tailscale Mesh Network (if device is on Tailscale):
ssh root@{ts_ip}
```
"""
        cards.append(card)

    lines.append("\n---\n")
    lines.append("## 📱 Termius Setup Guide (One-Click Copy Table)\n\n")
    lines.append("Har VPS ko Termius (Android / iOS / Windows / Mac) me direct add karne ke liye ye parameters use karein:\n\n")
    lines.append("| Plan | Label / Alias | Hostname / Address | Port | Username | Password |\n")
    lines.append("| :--- | :--- | :--- | :---: | :---: | :--- |\n")
    lines.extend(termius_entries)

    lines.append("\n---\n")
    lines.append("## 🔍 Detailed VPS Specifications & Access Profiles\n\n")
    lines.append("\n".join(cards))

    lines.append("\n---\n")
    lines.append("## 🔄 Automatic Update Guarantee\n\n")
    lines.append("Yeh file (`vps_details.md`) automatically update hoti hai jab bhi:\n")
    lines.append("1. Naya VPS add kiya jata hai (`python3 manage_vps_plans.py add-vps ...`).\n")
    lines.append("2. Kisi VPS ka password change hota hai (`python3 manage_vps_plans.py set-pass ...`).\n")
    lines.append("3. Status check kiya jata hai (`python3 manage_vps_plans.py show` ya `update-md`).\n")

    content = "".join(lines)
    with open(DETAILS_MD_FILE, "w") as f:
        f.write(content)

    return len(plans)

def show_all_plans():
    update_vps_details_md()
    plans = load_plans()

    print(BANNER)
    print(f"Server Primary IPv4: {PUBLIC_IP} (Hidden via Hex Cluster: {HEX_CLUSTER_ID})")
    print(f"📄 Auto-generated documentation: vps_details.md (UPDATED)")
    print("=" * 80)

    for num in sorted(plans.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        v = plans[num]
        cname = v["container"]
        ts_ip = get_tailscale_ip(cname)
        cf_url = get_cloudflare_url(cname)
        status = get_container_status(cname)

        print(f"\n🔹 【 {v['plan']} 】 — {cname.upper()} [{status.upper()}]")
        print(f"   ├─ Hardware:       {v['ram']} RAM | {v['cpu']} | {v['storage']}")
        print(f"   ├─ Root Password:  {v['password']}")
        print(f"   ├─ Custom Host:    {v['public_host']}")
        print(f"   ├─ SSH Port:       {v['ssh_port']}")
        print(f"   ├─ Web Port:       {v['web_port']}")
        print(f"   ├─ Tailscale IP:   {ts_ip} (Port: 22)")
        print(f"   ├─ Web Terminal:   {cf_url}")
        print(f"   └─ SSH Command:    ssh root@{v['public_host']} -p {v['ssh_port']}")
    print("\n" + "=" * 80)
    print("💡 Yeh details kisi bhi phone/laptop/Termius/PuTTY me direct kaam karengi!")

def test_ssh_all():
    update_vps_details_md()
    plans = load_plans()
    print(BANNER)
    print("[*] Testing live SSH authentication for all configured VPS...")
    all_ok = True
    for num in sorted(plans.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        v = plans[num]
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
    plans = load_plans()
    print(BANNER)
    print("[*] Updating passwords in running containers...")
    for num, v in plans.items():
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
    update_vps_details_md()
    print("[✓] vps_details.md automatically refreshed!")

def set_custom_password(plan_num, new_password):
    plans = load_plans()
    key = str(plan_num)
    if key not in plans:
        print(f"[✗] Invalid plan number: {plan_num}. Choose from {list(plans.keys())}.")
        return
    v = plans[key]
    cname = v["container"]
    try:
        subprocess.run(
            ["docker", "exec", cname, "sh", "-c", f"echo 'root:{new_password}' | chpasswd"],
            check=True
        )
        v["password"] = new_password
        save_plans(plans)
        update_vps_details_md()
        print(f"[✓] {v['plan']} ({cname}): Root password successfully changed to '{new_password}'")
        print(f"[✓] vps_details.md automatically updated with new password!")
    except Exception as e:
        print(f"[✗] Error setting password: {e}")

def add_new_vps(plan_num, ram, cpu, storage, ssh_port, web_port, password):
    """
    Creates and starts a new VPS docker container, assigns resources,
    sets password, and auto-updates vps_details.md.
    """
    plans = load_plans()
    key = str(plan_num)
    cname = f"root-ubuntu-vps-{plan_num}"
    host = f"ghostrootvps{plan_num}.{HEX_CLUSTER_ID}.sslip.io"
    alt_host = f"ghostvpsroot{plan_num}.{HEX_CLUSTER_ID}.sslip.io"

    print(f"[*] Creating new VPS Plan {plan_num} ({cname})...")

    # Docker run command
    cmd = [
        "docker", "run", "-d",
        "--name", cname,
        "--hostname", f"ubuntu-vps-{plan_num}",
        "--restart", "unless-stopped",
        "-p", f"{ssh_port}:22",
        "-p", f"{web_port}:{web_port}",
        "-e", f"ROOT_PASSWORD={password}",
        "-e", f"PORT={web_port}",
        "-e", "QUICK_TUNNEL=true",
        f"--memory={ram.lower()}",
        f"--cpus={cpu}",
        "--cap-add=NET_ADMIN",
        "--device=/dev/net/tun:/dev/net/tun",
        "root-ubuntu-vps:latest"
    ]

    try:
        subprocess.run(cmd, check=True)
        # Apply password directly inside container
        subprocess.run(
            ["docker", "exec", cname, "sh", "-c", f"echo 'root:{password}' | chpasswd"],
            check=True
        )
        print(f"[✓] Container {cname} successfully started!")
    except Exception as e:
        print(f"[!] Warning during docker run: {e}. Registering plan configuration anyway.")

    plans[key] = {
        "plan": f"Plan {plan_num}",
        "container": cname,
        "ram": ram,
        "cpu": f"{cpu} vCore" if "vCore" not in str(cpu) else str(cpu),
        "storage": storage,
        "ssh_port": int(ssh_port),
        "web_port": int(web_port),
        "password": password,
        "public_host": host,
        "alt_host": alt_host,
    }

    save_plans(plans)
    count = update_vps_details_md()
    print(f"[🎉] Successfully added Plan {plan_num}!")
    print(f"[✓] vps_details.md auto-updated with all {count} VPS plans!")

def print_help():
    print(BANNER)
    print("Usage:")
    print("  python3 manage_vps_plans.py show                 Display all VPS details & refresh vps_details.md")
    print("  python3 manage_vps_plans.py update-md            Regenerate & update vps_details.md immediately")
    print("  python3 manage_vps_plans.py test                 Test live SSH authentication for all VPS")
    print("  python3 manage_vps_plans.py apply                Apply all predefined passwords to containers")
    print("  python3 manage_vps_plans.py set-pass <num> <pwd> Set custom password for VPS & auto-update md")
    print("  python3 manage_vps_plans.py add-vps <num> <ram> <cpu> <storage> <ssh_port> <web_port> <pwd>")
    print("=" * 80)

def main():
    if len(sys.argv) < 2:
        show_all_plans()
        sys.exit(0)

    cmd = sys.argv[1].lower()
    if cmd in ("show", "list", "plans"):
        show_all_plans()
    elif cmd in ("update-md", "md", "generate-md"):
        count = update_vps_details_md()
        print(f"[✓] vps_details.md successfully updated with {count} VPS plans!")
    elif cmd in ("test", "check"):
        test_ssh_all()
    elif cmd == "apply":
        apply_passwords()
    elif cmd == "set-pass":
        if len(sys.argv) < 4:
            print("Usage: python3 manage_vps_plans.py set-pass <plan_num> <new_password>")
            sys.exit(1)
        set_custom_password(sys.argv[2], sys.argv[3])
    elif cmd == "add-vps":
        if len(sys.argv) < 9:
            print("Usage: python3 manage_vps_plans.py add-vps <plan_num> <ram> <cpu> <storage> <ssh_port> <web_port> <password>")
            print("Example: python3 manage_vps_plans.py add-vps 6 8g 4 100GB 2227 7686 MySecretPass123")
            sys.exit(1)
        add_new_vps(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8])
    else:
        print_help()

if __name__ == "__main__":
    main()
