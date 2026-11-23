#!/usr/bin/env python3
"""
Root Ubuntu VPS - Plan Resources Emulation & Spoofing System
Ensures container tools (nproc, free, df, lsblk, lscpu, /proc/cpuinfo, /proc/meminfo)
reflect the exact VPS plan specs (CPU cores, RAM, NVMe storage) rather than host hardware.
"""

import os
import sys
import subprocess
import re
import shutil

PLAN_PRESETS = {
    "1": {"cpu": 2, "ram_gb": 4, "storage_gb": 80, "disk_name": "nvme0n1", "disk_model": "NVMe SSD"},
    "2": {"cpu": 4, "ram_gb": 8, "storage_gb": 200, "disk_name": "nvme0n1", "disk_model": "NVMe SSD"},
    "3": {"cpu": 8, "ram_gb": 16, "storage_gb": 300, "disk_name": "nvme0n1", "disk_model": "NVMe SSD"},
    "4": {"cpu": 12, "ram_gb": 24, "storage_gb": 400, "disk_name": "nvme0n1", "disk_model": "NVMe SSD"},
    "5": {"cpu": 16, "ram_gb": 32, "storage_gb": 500, "disk_name": "nvme0n1", "disk_model": "NVMe SSD"},
}

def detect_vps_specs():
    plan_env = os.environ.get("VPS_PLAN", "").strip()
    cpu_env = os.environ.get("VPS_CPU", "").strip()
    ram_env = os.environ.get("VPS_RAM", "").strip()
    storage_env = os.environ.get("VPS_STORAGE", "").strip()
    disk_name_env = os.environ.get("VPS_DISK_NAME", "nvme0n1").strip()
    disk_model_env = os.environ.get("VPS_DISK_MODEL", "NVMe SSD").strip()

    hostname = ""
    try:
        with open("/etc/hostname", "r") as f:
            hostname = f.read().strip()
    except Exception:
        hostname = os.environ.get("HOSTNAME", "")

    match = re.search(r"ubuntu-vps-(\d+)", hostname)
    detected_num = match.group(1) if match else ""

    plan_key = plan_env
    if not plan_key and detected_num:
        if detected_num == "1":
            plan_key = "2" # root-ubuntu-vps-1 is Plan 2
        elif detected_num == "2":
            plan_key = "1" # root-ubuntu-vps-2 is Plan 1
        elif detected_num in PLAN_PRESETS:
            plan_key = detected_num

    preset = PLAN_PRESETS.get(plan_key, PLAN_PRESETS["3"])

    # Resolve CPU
    cpu = preset["cpu"]
    if cpu_env:
        try:
            cpu = int(re.sub(r"[^\d]", "", cpu_env))
        except Exception:
            pass
    elif os.path.exists("/sys/fs/cgroup/cpu.max"):
        try:
            with open("/sys/fs/cgroup/cpu.max") as f:
                parts = f.read().split()
                if len(parts) == 2 and parts[0] != "max":
                    cpu = max(1, int(int(parts[0]) / int(parts[1])))
        except Exception:
            pass

    # Resolve RAM
    ram_gb = preset["ram_gb"]
    if ram_env:
        try:
            ram_gb = int(re.sub(r"[^\d]", "", ram_env))
        except Exception:
            pass
    elif os.path.exists("/sys/fs/cgroup/memory.max"):
        try:
            with open("/sys/fs/cgroup/memory.max") as f:
                val = f.read().strip()
                if val != "max":
                    ram_gb = max(1, round(int(val) / (1024 ** 3)))
        except Exception:
            pass

    # Resolve Storage
    storage_gb = preset["storage_gb"]
    if storage_env:
        try:
            storage_gb = int(re.sub(r"[^\d]", "", storage_env))
        except Exception:
            pass
    else:
        if ram_gb <= 4:
            storage_gb = 80
        elif ram_gb <= 8:
            storage_gb = 200
        elif ram_gb <= 16:
            storage_gb = 300
        elif ram_gb <= 24:
            storage_gb = 400
        else:
            storage_gb = 500

    return {
        "cpu": cpu,
        "ram_gb": ram_gb,
        "ram_kb": ram_gb * 1024 * 1024,
        "storage_gb": storage_gb,
        "disk_name": disk_name_env,
        "disk_model": disk_model_env,
    }

def setup_fake_files(specs):
    os.makedirs("/etc/fake_proc", exist_ok=True)

    # 1. /etc/fake_vps.conf
    conf_content = f"""CPU={specs['cpu']}
RAM_KB={specs['ram_kb']}
RAM_GB={specs['ram_gb']}
DISK_GB={specs['storage_gb']}
DISK_NAME={specs['disk_name']}
DISK_MODEL={specs['disk_model']}
"""
    with open("/etc/fake_vps.conf", "w") as f:
        f.write(conf_content)

    # 2. /etc/fake_proc/cpuinfo
    model_name = "AMD EPYC-Rome Processor"
    vendor_id = "AuthenticAMD"
    cpu_mhz = "1996.249"
    flags = "fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 syscall nx mmxext fxsr_opt pdpe1gb rdtscp lm rep_good nopl cpuid extd_apicid tsc_known_freq pni pclmulqdq ssse3 fma cx16 sse4_1 sse4_2 x2apic movbe popcnt aes xsave avx f16c rdrand hypervisor lahf_lm svm cr8_legacy abm sse4a misalignsse 3dnowprefetch osvw topoext perfctr_core ibpb stibp vmmcall fsgsbase bmi1 avx2 smep bmi2 rdseed adx smap clflushopt clwb sha_ni xsaveopt xsavec xgetbv1 clzero xsaveerptr wbnoinvd arat npt nrip_save umip rdpid"
    
    try:
        with open("/proc/cpuinfo", "r") as f:
            content = f.read()
            m = re.search(r"model name\s*:\s*(.+)", content)
            if m: model_name = m.group(1).strip()
            v = re.search(r"vendor_id\s*:\s*(.+)", content)
            if v: vendor_id = v.group(1).strip()
            hz = re.search(r"cpu MHz\s*:\s*(.+)", content)
            if hz: cpu_mhz = hz.group(1).strip()
            fl = re.search(r"flags\s*:\s*(.+)", content)
            if fl: flags = fl.group(1).strip()
    except Exception:
        pass

    cpu_count = specs["cpu"]
    cpuinfo_blocks = []
    for i in range(cpu_count):
        block = f"""processor	: {i}
vendor_id	: {vendor_id}
cpu family	: 23
model		: 49
model name	: {model_name}
stepping	: 0
microcode	: 0x1000065
cpu MHz		: {cpu_mhz}
cache size	: 512 KB
physical id	: 0
siblings	: {cpu_count}
core id		: {i}
cpu cores	: {cpu_count}
apicid		: {i}
initial apicid	: {i}
fpu		: yes
fpu_exception	: yes
cpuid level	: 16
wp		: yes
flags		: {flags}
bugs		: sysret_ss_attrs null_seg spectre_v1 spectre_v2 spec_store_bypass retbleed
bogomips	: 3992.49
TLB size	: 3072 4K pages
clflush size	: 64
cache_alignment	: 64
address sizes	: 40 bits physical, 48 bits virtual
power management:
"""
        cpuinfo_blocks.append(block)

    with open("/etc/fake_proc/cpuinfo", "w") as f:
        f.write("\n".join(cpuinfo_blocks) + "\n")

    # 3. /etc/fake_proc/meminfo
    total_kb = specs["ram_kb"]
    used_kb = int(total_kb * 0.11)
    free_kb = int(total_kb * 0.74)
    buffer_kb = int(total_kb * 0.02)
    cached_kb = total_kb - used_kb - free_kb - buffer_kb
    avail_kb = free_kb + int(cached_kb * 0.8)

    meminfo_content = f"""MemTotal:       {total_kb} kB
MemFree:        {free_kb} kB
MemAvailable:   {avail_kb} kB
Buffers:         {buffer_kb} kB
Cached:         {cached_kb} kB
SwapCached:            0 kB
Active:          {int(total_kb * 0.14)} kB
Inactive:        {int(total_kb * 0.09)} kB
Active(anon):     {int(total_kb * 0.09)} kB
Inactive(anon):     {int(total_kb * 0.02)} kB
Active(file):     {int(total_kb * 0.05)} kB
Inactive(file):     {int(total_kb * 0.07)} kB
Unevictable:           0 kB
Mlocked:               0 kB
SwapTotal:             0 kB
SwapFree:              0 kB
Dirty:                48 kB
Writeback:             0 kB
AnonPages:       {int(total_kb * 0.09)} kB
Mapped:          {int(total_kb * 0.02)} kB
Shmem:              4096 kB
KReclaimable:     {int(total_kb * 0.01)} kB
Slab:            {int(total_kb * 0.02)} kB
SReclaimable:     {int(total_kb * 0.01)} kB
SUnreclaim:       {int(total_kb * 0.01)} kB
KernelStack:        5120 kB
PageTables:        12288 kB
NFS_Unstable:          0 kB
Bounce:                0 kB
WritebackTmp:          0 kB
CommitLimit:     {int(total_kb * 0.5)} kB
Committed_AS:    {int(total_kb * 0.12)} kB
VmallocTotal:   34359738367 kB
VmallocUsed:       45056 kB
VmallocChunk:          0 kB
Percpu:             4096 kB
HardwareCorrupted:     0 kB
AnonHugePages:         0 kB
ShmemHugePages:        0 kB
ShmemPmdMapped:        0 kB
FileHugePages:         0 kB
FilePmdMapped:         0 kB
HugePages_Total:       0
HugePages_Free:        0
HugePages_Rsvd:        0
HugePages_Surp:        0
Hugepagesize:       2048 kB
Hugetlb:               0 kB
DirectMap4k:      327680 kB
DirectMap2M:     {total_kb} kB
"""
    with open("/etc/fake_proc/meminfo", "w") as f:
        f.write(meminfo_content)

    # 4. /etc/fake_proc/stat
    stat_lines = ["cpu  25400 0 18200 98500000 1200 0 450 0 0 0"]
    for i in range(cpu_count):
        stat_lines.append(f"cpu{i} 3175 0 2275 12312500 150 0 56 0 0 0")
    stat_lines.extend([
        "intr 11250000 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0",
        "ctxt 28450000",
        "btime 1700000000",
        "processes 50000",
        "procs_running 1",
        "procs_blocked 0",
        "softirq 8500000 0 2500000 1200 450000 0 0 120000 0 0 5428800"
    ])
    with open("/etc/fake_proc/stat", "w") as f:
        f.write("\n".join(stat_lines) + "\n")

    # 5. /etc/fake_proc/partitions
    disk_blocks_1k = specs["storage_gb"] * 1024 * 1024
    dname = specs["disk_name"]
    part_content = f"""major minor  #blocks  name

 259     0  {disk_blocks_1k} {dname}
 259     1  {disk_blocks_1k} {dname}p1
"""
    with open("/etc/fake_proc/partitions", "w") as f:
        f.write(part_content)

    # 6. /etc/fake_proc/diskstats
    diskstats_content = f""" 259       0 {dname} 15000 0 1200000 4500 25000 0 2000000 9000 0 5000 13500 0 0 0 0 0 0
 259       1 {dname}p1 14500 0 1150000 4300 24500 0 1950000 8800 0 4800 13100 0 0 0 0 0 0
"""
    with open("/etc/fake_proc/diskstats", "w") as f:
        f.write(diskstats_content)

    # 7. /etc/fake_proc/cpu_online, possible, present
    online_str = f"0-{cpu_count - 1}" if cpu_count > 1 else "0"
    for fn in ["cpu_online", "cpu_possible", "cpu_present"]:
        with open(f"/etc/fake_proc/{fn}", "w") as f:
            f.write(online_str + "\n")

    # 8. /etc/fake_proc/mountinfo and mounts
    dpart = f"/dev/{dname}p1"
    try:
        with open("/proc/self/mountinfo", "r") as f:
            minfo = f.read()
        lines = []
        for line in minfo.splitlines():
            if re.search(r"\s/\s+.*\soverlay\s", line):
                parts = line.split(" - ")
                pre = parts[0]
                line = f"{pre} - ext4 {dpart} rw,relatime"
            lines.append(line)
        with open("/etc/fake_proc/mountinfo", "w") as f:
            f.write("\n".join(lines) + "\n")
    except Exception:
        pass

    try:
        with open("/proc/mounts", "r") as f:
            mounts = f.read()
        lines = []
        for line in mounts.splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[1] == "/":
                line = f"{dpart} / ext4 rw,relatime 0 0"
            lines.append(line)
        with open("/etc/fake_proc/mounts", "w") as f:
            f.write("\n".join(lines) + "\n")
    except Exception:
        pass

def compile_preload_lib():
    c_source = "/opt/fakevps/libfakevps.c"
    so_target = "/usr/local/lib/libfakevps.so"

    if not os.path.exists(c_source):
        for alt in ["/root/Root-Ubuntu-VPS/libfakevps.c", "/tmp/libfakevps.c", "/root/libfakevps.c"]:
            if os.path.exists(alt):
                c_source = alt
                break

    if os.path.exists(c_source):
        cmd = ["gcc", "-O2", "-fPIC", "-shared", c_source, "-o", so_target, "-ldl"]
        subprocess.run(cmd, check=True)

    preload_file = "/etc/ld.so.preload"
    lines = []
    if os.path.exists(preload_file):
        with open(preload_file, "r") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]

    if so_target not in lines:
        lines.append(so_target)
        with open(preload_file, "w") as f:
            f.write("\n".join(lines) + "\n")

def install_wrappers():
    # 1. nproc wrapper
    nproc_script = """#!/bin/sh
CPU=$(grep -s "^CPU=" /etc/fake_vps.conf | cut -d= -f2)
[ -z "$CPU" ] && CPU=8
for arg in "$@"; do
    case "$arg" in
        --help|--version)
            if [ -x /usr/bin/nproc.orig ]; then exec /usr/bin/nproc.orig "$@"; fi
            ;;
    esac
done
echo "$CPU"
"""
    # 2. free wrapper
    free_script = """#!/usr/bin/env python3
import sys

conf = {}
try:
    with open("/etc/fake_vps.conf") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                conf[k] = v
except Exception:
    pass

total_kb = int(conf.get("RAM_KB", 16777216))
used_kb = int(total_kb * 0.11)
free_kb = int(total_kb * 0.74)
shared_kb = 4096
buff_kb = total_kb - used_kb - free_kb
avail_kb = free_kb + int(buff_kb * 0.8)

args = sys.argv[1:]
unit = "k"
human = False

if any(a in ("-h", "--human") for a in args):
    human = True
elif any(a in ("-m", "--mebi", "--mega") for a in args):
    unit = "m"
elif any(a in ("-g", "--gibi", "--giga") for a in args):
    unit = "g"
elif any(a in ("-b", "--bytes") for a in args):
    unit = "b"

def fmt_human(kb):
    bytes_val = kb * 1024
    if bytes_val >= 1024**3:
        val = bytes_val / (1024**3)
        return f"{val:.1f}Gi" if val < 10 else f"{int(round(val))}Gi"
    elif bytes_val >= 1024**2:
        return f"{int(round(bytes_val / (1024**2)))}Mi"
    elif bytes_val >= 1024:
        return f"{int(round(bytes_val / 1024))}Ki"
    return f"{bytes_val}B"

def fmt_unit(kb, u):
    if u == "b": return str(kb * 1024)
    if u == "k": return str(kb)
    if u == "m": return str(kb // 1024)
    if u == "g": return str(kb // (1024 * 1024))
    return str(kb)

if human:
    print(f"{'':15}{'total':>12}{'used':>12}{'free':>12}{'shared':>12}{'buff/cache':>12}{'available':>12}")
    print(f"{'Mem:':<15}{fmt_human(total_kb):>12}{fmt_human(used_kb):>12}{fmt_human(free_kb):>12}{'4.0Mi':>12}{fmt_human(buff_kb):>12}{fmt_human(avail_kb):>12}")
    print(f"{'Swap:':<15}{'0B':>12}{'0B':>12}{'0B':>12}")
else:
    print(f"{'':15}{'total':>12}{'used':>12}{'free':>12}{'shared':>12}{'buff/cache':>12}{'available':>12}")
    print(f"{'Mem:':<15}{fmt_unit(total_kb, unit):>12}{fmt_unit(used_kb, unit):>12}{fmt_unit(free_kb, unit):>12}{fmt_unit(shared_kb, unit):>12}{fmt_unit(buff_kb, unit):>12}{fmt_unit(avail_kb, unit):>12}")
    print(f"{'Swap:':<15}{'0':>12}{'0':>12}{'0':>12}")
"""

    # 3. df wrapper
    df_script = """#!/usr/bin/env python3
import sys
import os
import subprocess

conf = {}
try:
    with open("/etc/fake_vps.conf") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                conf[k] = v
except Exception:
    pass

disk_gb = int(conf.get("DISK_GB", 300))
disk_name = conf.get("DISK_NAME", "nvme0n1")
root_dev = f"/dev/{disk_name}p1"

orig_df = "/bin/df.orig" if os.path.exists("/bin/df.orig") else "/usr/bin/df.orig"
res = subprocess.run([orig_df] + sys.argv[1:], capture_output=True, text=True)
lines = res.stdout.splitlines()

used_gb = max(15, int(disk_gb * 0.08))
avail_gb = disk_gb - used_gb
pct = f"{int(round((used_gb / disk_gb) * 100))}%"

out = []
for line in lines:
    parts = line.split()
    if len(parts) >= 6 and parts[-1] == "/":
        if any("-h" in a for a in sys.argv[1:]):
            line = f"{root_dev:<15} {disk_gb:>5}G {used_gb:>5}G {avail_gb:>5}G {pct:>4} /"
        elif any("-m" in a for a in sys.argv[1:]):
            line = f"{root_dev:<15} {disk_gb*1024:>7} {used_gb*1024:>7} {avail_gb*1024:>7} {pct:>4} /"
        else:
            line = f"{root_dev:<15} {disk_gb*1024*1024:>10} {used_gb*1024*1024:>10} {avail_gb*1024*1024:>10} {pct:>4} /"
    elif len(parts) >= 1 and (parts[0] == "overlay" or parts[0].startswith("/dev/")) and "/" in line and parts[-1] == "/":
        if any("-h" in a for a in sys.argv[1:]):
            line = f"{root_dev:<15} {disk_gb:>5}G {used_gb:>5}G {avail_gb:>5}G {pct:>4} /"
    out.append(line)

print("\\n".join(out))
"""

    # 4. lsblk wrapper
    lsblk_script = """#!/usr/bin/env python3
import sys

conf = {}
try:
    with open("/etc/fake_vps.conf") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                conf[k] = v
except Exception:
    pass

disk_gb = int(conf.get("DISK_GB", 300))
disk_name = conf.get("DISK_NAME", "nvme0n1")
disk_model = conf.get("DISK_MODEL", "NVMe SSD")

used_gb = max(15, int(disk_gb * 0.08))
avail_gb = disk_gb - used_gb
pct = f"{int(round((used_gb / disk_gb) * 100))}%"

args = sys.argv[1:]

cols_arg = None
for i, a in enumerate(args):
    if a in ("-o", "--output") and i + 1 < len(args):
        cols_arg = args[i + 1]
    elif a.startswith("-o="):
        cols_arg = a.split("=", 1)[1]
    elif a.startswith("-o") and len(a) > 2:
        cols_arg = a[2:]

disk_only = any("-d" in a or "--nodeps" in a for a in args)
fs_mode = any(a in ("-f", "--fs") for a in args)

if fs_mode:
    print(f"{'NAME':<12} {'FSTYPE':<7} {'FSVER':<6} {'LABEL':<6} {'UUID':<37} {'FSAVAIL':<8} {'FSUSE%':<7} {'MOUNTPOINTS'}")
    print(f"{disk_name:<12} {'':<7} {'':<6} {'':<6} {'':<37} {'':<8} {'':<7} ")
    if not disk_only:
        print(f"{'└─' + disk_name + 'p1':<12} {'ext4':<7} {'1.0':<6} {'':<6} {'e81a3d90-7f28-48bc-b2cf-3d719548bcde':<37} {f'{avail_gb}G':<8} {pct:<7} /")
elif cols_arg:
    cols = [c.upper() for c in cols_arg.split(",")]
    disk_vals = {
        "NAME": disk_name,
        "KNAME": disk_name,
        "SIZE": f"{disk_gb}G",
        "ROTA": "0",
        "MODEL": disk_model,
        "TYPE": "disk",
        "MAJ:MIN": "259:0",
        "RM": "0",
        "RO": "0",
        "MOUNTPOINT": "",
        "MOUNTPOINTS": "",
        "FSTYPE": "",
        "UUID": "",
        "STATE": "running",
        "VENDOR": "NVMe",
    }
    part_vals = {
        "NAME": f"{disk_name}p1" if disk_only else f"└─{disk_name}p1",
        "KNAME": f"{disk_name}p1",
        "SIZE": f"{disk_gb}G",
        "ROTA": "0",
        "MODEL": "",
        "TYPE": "part",
        "MAJ:MIN": "259:1",
        "RM": "0",
        "RO": "0",
        "MOUNTPOINT": "/",
        "MOUNTPOINTS": "/",
        "FSTYPE": "ext4",
        "UUID": "e81a3d90-7f28-48bc-b2cf-3d719548bcde",
        "STATE": "",
        "VENDOR": "",
    }
    widths = []
    for c in cols:
        w = max(len(c), len(disk_vals.get(c, "")), len(part_vals.get(c, "")))
        widths.append(max(w, 4))
        
    hdr = " ".join(f"{c:<{widths[i]}}" for i, c in enumerate(cols))
    row1 = " ".join(f"{disk_vals.get(c, ''):<{widths[i]}}" for i, c in enumerate(cols))
    
    print(hdr)
    print(row1)
    if not disk_only:
        row2 = " ".join(f"{part_vals.get(c, ''):<{widths[i]}}" for i, c in enumerate(cols))
        print(row2)
else:
    if disk_only:
        print(f"{'NAME':<10} {'MAJ:MIN':<7} {'RM':<3} {'SIZE':<5} {'RO':<3} {'TYPE':<4} {'MOUNTPOINTS'}")
        print(f"{disk_name:<10} {'259:0':<7} {'0':<3} {f'{disk_gb}G':<5} {'0':<3} {'disk':<4} ")
    else:
        print(f"{'NAME':<12} {'MAJ:MIN':<7} {'RM':<3} {'SIZE':<5} {'RO':<3} {'TYPE':<4} {'MOUNTPOINTS'}")
        print(f"{disk_name:<12} {'259:0':<7} {'0':<3} {f'{disk_gb}G':<5} {'0':<3} {'disk':<4} ")
        print(f"{'└─' + disk_name + 'p1':<12} {'259:1':<7} {'0':<3} {f'{disk_gb}G':<5} {'0':<3} {'part':<4} /")
"""

    # 5. lscpu wrapper
    lscpu_script = """#!/usr/bin/env python3
import sys
import subprocess
import os
import re

conf = {}
try:
    with open("/etc/fake_vps.conf") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                conf[k] = v
except Exception:
    pass

cpu_count = int(conf.get("CPU", 8))
orig_lscpu = "/usr/bin/lscpu.orig"

if os.path.exists(orig_lscpu):
    res = subprocess.run([orig_lscpu] + sys.argv[1:], capture_output=True, text=True)
    out = []
    for line in res.stdout.splitlines():
        if line.startswith("CPU(s):"):
            line = f"CPU(s):                                  {cpu_count}"
        elif line.startswith("On-line CPU(s) list:"):
            line = f"On-line CPU(s) list:                     0-{cpu_count - 1}"
        elif line.startswith("Thread(s) per core:"):
            line = "Thread(s) per core:                      1"
        elif line.startswith("Core(s) per socket:"):
            line = f"Core(s) per socket:                      {cpu_count}"
        elif line.startswith("Socket(s):"):
            line = "Socket(s):                               1"
        elif "NUMA node0 CPU(s):" in line:
            line = f"NUMA node0 CPU(s):                       0-{cpu_count - 1}"
        elif "instances)" in line:
            line = re.sub(r"\(\d+ instances\)", f"({cpu_count} instances)", line)
        out.append(line)
    print("\\n".join(out))
"""

    targets = [
        ("/usr/bin/nproc", "/usr/local/bin/nproc", nproc_script),
        ("/usr/bin/free", "/usr/local/bin/free", free_script),
        ("/bin/df", "/usr/local/bin/df", df_script),
        ("/usr/bin/lsblk", "/usr/local/bin/lsblk", lsblk_script),
        ("/usr/bin/lscpu", "/usr/local/bin/lscpu", lscpu_script),
    ]

    for orig_bin, local_bin, script in targets:
        backup_bin = orig_bin + ".orig"
        if os.path.exists(orig_bin) and not os.path.exists(backup_bin) and not os.path.islink(orig_bin):
            shutil.copy2(orig_bin, backup_bin)

        with open(local_bin, "w") as f:
            f.write(script)
        os.chmod(local_bin, 0o755)

        with open(orig_bin, "w") as f:
            f.write(script)
        os.chmod(orig_bin, 0o755)

        if orig_bin == "/bin/df" and os.path.exists("/usr/bin/df"):
            if not os.path.exists("/usr/bin/df.orig") and not os.path.islink("/usr/bin/df"):
                shutil.copy2("/usr/bin/df", "/usr/bin/df.orig")
            with open("/usr/bin/df", "w") as f:
                f.write(script)
            os.chmod("/usr/bin/df", 0o755)

def main():
    specs = detect_vps_specs()
    setup_fake_files(specs)
    try:
        compile_preload_lib()
    except Exception as e:
        print(f"[!] Warning during libfakevps compilation: {e}")
    install_wrappers()
    print(f"[✓] VPS Specs applied: CPU={specs['cpu']} Cores, RAM={specs['ram_gb']}GB, Disk={specs['storage_gb']}GB {specs['disk_model']}")

if __name__ == "__main__":
    main()
