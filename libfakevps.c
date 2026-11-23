#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dlfcn.h>
#include <unistd.h>
#include <sched.h>
#include <sys/sysinfo.h>
#include <sys/statvfs.h>
#include <sys/vfs.h>
#include <fcntl.h>
#include <stdarg.h>

static int cfg_loaded = 0;
static int cfg_cpu = 8;
static unsigned long long cfg_ram_kb = 16777216ULL;
static unsigned long long cfg_disk_gb = 300ULL;
static char cfg_disk_name[64] = "nvme0n1";

static void load_config(void) {
    if (cfg_loaded) return;
    cfg_loaded = 1;

    FILE *f = fopen("/etc/fake_vps.conf", "r");
    if (!f) return;

    char line[256];
    while (fgets(line, sizeof(line), f)) {
        char *eq = strchr(line, '=');
        if (!eq) continue;
        *eq = '\0';
        char *key = line;
        char *val = eq + 1;
        char *nl = strchr(val, '\r'); if (nl) *nl = '\0';
        nl = strchr(val, '\n'); if (nl) *nl = '\0';

        if (strcmp(key, "CPU") == 0) {
            cfg_cpu = atoi(val);
            if (cfg_cpu <= 0) cfg_cpu = 1;
        } else if (strcmp(key, "RAM_KB") == 0) {
            cfg_ram_kb = strtoull(val, NULL, 10);
        } else if (strcmp(key, "DISK_GB") == 0) {
            cfg_disk_gb = strtoull(val, NULL, 10);
        } else if (strcmp(key, "DISK_NAME") == 0) {
            strncpy(cfg_disk_name, val, sizeof(cfg_disk_name) - 1);
        }
    }
    fclose(f);
}

static const char *redirect_path(const char *path) {
    if (!path) return NULL;
    if (strcmp(path, "/proc/cpuinfo") == 0) return "/etc/fake_proc/cpuinfo";
    if (strcmp(path, "/proc/meminfo") == 0) return "/etc/fake_proc/meminfo";
    if (strcmp(path, "/proc/stat") == 0) return "/etc/fake_proc/stat";
    if (strcmp(path, "/proc/partitions") == 0) return "/etc/fake_proc/partitions";
    if (strcmp(path, "/proc/diskstats") == 0) return "/etc/fake_proc/diskstats";
    if (strcmp(path, "/proc/mounts") == 0) return "/etc/fake_proc/mounts";
    if (strcmp(path, "/etc/mtab") == 0) return "/etc/fake_proc/mounts";
    if (strcmp(path, "/proc/self/mounts") == 0) return "/etc/fake_proc/mounts";
    if (strcmp(path, "/proc/self/mountinfo") == 0) return "/etc/fake_proc/mountinfo";
    if (strcmp(path, "/sys/devices/system/cpu/online") == 0) return "/etc/fake_proc/cpu_online";
    if (strcmp(path, "/sys/devices/system/cpu/possible") == 0) return "/etc/fake_proc/cpu_possible";
    if (strcmp(path, "/sys/devices/system/cpu/present") == 0) return "/etc/fake_proc/cpu_present";
    return path;
}

static int is_root_fs(const char *path) {
    if (!path) return 1;
    if (strcmp(path, "/") == 0) return 1;
    if (strncmp(path, "/dev", 4) == 0) return 0;
    if (strncmp(path, "/sys", 4) == 0) return 0;
    if (strncmp(path, "/proc", 5) == 0) return 0;
    if (strncmp(path, "/run", 4) == 0) return 0;
    return 1;
}

int open(const char *pathname, int flags, ...) {
    load_config();
    const char *target = redirect_path(pathname);
    int (*orig_open)(const char *, int, ...) = dlsym(RTLD_NEXT, "open");
    if (flags & (O_CREAT | O_TMPFILE)) {
        va_list args;
        va_start(args, flags);
        mode_t mode = va_arg(args, mode_t);
        va_end(args);
        return orig_open(target, flags, mode);
    }
    return orig_open(target, flags);
}

int open64(const char *pathname, int flags, ...) {
    load_config();
    const char *target = redirect_path(pathname);
    int (*orig_open64)(const char *, int, ...) = dlsym(RTLD_NEXT, "open64");
    if (!orig_open64) orig_open64 = dlsym(RTLD_NEXT, "open");
    if (flags & (O_CREAT | O_TMPFILE)) {
        va_list args;
        va_start(args, flags);
        mode_t mode = va_arg(args, mode_t);
        va_end(args);
        return orig_open64(target, flags, mode);
    }
    return orig_open64(target, flags);
}

int openat(int dirfd, const char *pathname, int flags, ...) {
    load_config();
    const char *target = pathname;
    if (pathname && pathname[0] == '/') {
        target = redirect_path(pathname);
    }
    int (*orig_openat)(int, const char *, int, ...) = dlsym(RTLD_NEXT, "openat");
    if (flags & (O_CREAT | O_TMPFILE)) {
        va_list args;
        va_start(args, flags);
        mode_t mode = va_arg(args, mode_t);
        va_end(args);
        return orig_openat(dirfd, target, flags, mode);
    }
    return orig_openat(dirfd, target, flags);
}

int openat64(int dirfd, const char *pathname, int flags, ...) {
    load_config();
    const char *target = pathname;
    if (pathname && pathname[0] == '/') {
        target = redirect_path(pathname);
    }
    int (*orig_openat64)(int, const char *, int, ...) = dlsym(RTLD_NEXT, "openat64");
    if (!orig_openat64) orig_openat64 = dlsym(RTLD_NEXT, "openat");
    if (flags & (O_CREAT | O_TMPFILE)) {
        va_list args;
        va_start(args, flags);
        mode_t mode = va_arg(args, mode_t);
        va_end(args);
        return orig_openat64(dirfd, target, flags, mode);
    }
    return orig_openat64(dirfd, target, flags);
}

FILE *fopen(const char *pathname, const char *mode) {
    load_config();
    const char *target = redirect_path(pathname);
    FILE *(*orig_fopen)(const char *, const char *) = dlsym(RTLD_NEXT, "fopen");
    return orig_fopen(target, mode);
}

FILE *fopen64(const char *pathname, const char *mode) {
    load_config();
    const char *target = redirect_path(pathname);
    FILE *(*orig_fopen64)(const char *, const char *) = dlsym(RTLD_NEXT, "fopen64");
    if (!orig_fopen64) orig_fopen64 = dlsym(RTLD_NEXT, "fopen");
    return orig_fopen64(target, mode);
}

FILE *setmntent(const char *filename, const char *type) {
    load_config();
    const char *target = redirect_path(filename);
    FILE *(*orig_setmntent)(const char *, const char *) = dlsym(RTLD_NEXT, "setmntent");
    return orig_setmntent(target, type);
}

int sched_getaffinity(pid_t pid, size_t cpusetsize, cpu_set_t *mask) {
    load_config();
    if (!mask) return -1;
    CPU_ZERO(mask);
    for (int i = 0; i < cfg_cpu; i++) {
        CPU_SET(i, mask);
    }
    return 0;
}

long sysconf(int name) {
    load_config();
    if (name == _SC_NPROCESSORS_ONLN || name == _SC_NPROCESSORS_CONF) {
        return cfg_cpu;
    }
    if (name == _SC_PHYS_PAGES) {
        long page_size = sysconf(_SC_PAGESIZE);
        if (page_size <= 0) page_size = 4096;
        return (long)((cfg_ram_kb * 1024ULL) / page_size);
    }
    if (name == _SC_AVPHYS_PAGES) {
        long page_size = sysconf(_SC_PAGESIZE);
        if (page_size <= 0) page_size = 4096;
        return (long)(((cfg_ram_kb * 3ULL / 4ULL) * 1024ULL) / page_size);
    }
    long (*orig_sysconf)(int) = dlsym(RTLD_NEXT, "sysconf");
    return orig_sysconf(name);
}

int get_nprocs(void) {
    load_config();
    return cfg_cpu;
}

int get_nprocs_conf(void) {
    load_config();
    return cfg_cpu;
}

int sysinfo(struct sysinfo *info) {
    load_config();
    int (*orig_sysinfo)(struct sysinfo *) = dlsym(RTLD_NEXT, "sysinfo");
    int res = orig_sysinfo(info);
    if (res == 0 && info) {
        info->mem_unit = 1;
        info->totalram = cfg_ram_kb * 1024ULL;
        info->freeram = (cfg_ram_kb * 3ULL / 4ULL) * 1024ULL;
        info->sharedram = 4 * 1024 * 1024ULL;
        info->bufferram = (cfg_ram_kb / 10ULL) * 1024ULL;
        info->totalswap = 0;
        info->freeswap = 0;
        info->procs = 20;
    }
    return res;
}

static void fix_statvfs(struct statvfs *buf) {
    if (!buf) return;
    buf->f_frsize = 4096;
    buf->f_bsize = 4096;
    unsigned long long total_blocks = (cfg_disk_gb * 1024ULL * 1024ULL * 1024ULL) / 4096ULL;
    unsigned long long used_blocks = (total_blocks * 8ULL) / 100ULL;
    if (used_blocks == 0) used_blocks = 200000ULL;
    buf->f_blocks = total_blocks;
    buf->f_bfree = total_blocks - used_blocks;
    buf->f_bavail = buf->f_bfree;
    buf->f_files = total_blocks / 4;
    buf->f_ffree = buf->f_files - 100000;
}

static void fix_statvfs64(struct statvfs64 *buf) {
    if (!buf) return;
    buf->f_frsize = 4096;
    buf->f_bsize = 4096;
    unsigned long long total_blocks = (cfg_disk_gb * 1024ULL * 1024ULL * 1024ULL) / 4096ULL;
    unsigned long long used_blocks = (total_blocks * 8ULL) / 100ULL;
    if (used_blocks == 0) used_blocks = 200000ULL;
    buf->f_blocks = total_blocks;
    buf->f_bfree = total_blocks - used_blocks;
    buf->f_bavail = buf->f_bfree;
    buf->f_files = total_blocks / 4;
    buf->f_ffree = buf->f_files - 100000;
}

static void fix_statfs(struct statfs *buf) {
    if (!buf) return;
    buf->f_frsize = 4096;
    buf->f_bsize = 4096;
    unsigned long long total_blocks = (cfg_disk_gb * 1024ULL * 1024ULL * 1024ULL) / 4096ULL;
    unsigned long long used_blocks = (total_blocks * 8ULL) / 100ULL;
    if (used_blocks == 0) used_blocks = 200000ULL;
    buf->f_blocks = total_blocks;
    buf->f_bfree = total_blocks - used_blocks;
    buf->f_bavail = buf->f_bfree;
    buf->f_files = total_blocks / 4;
    buf->f_ffree = buf->f_files - 100000;
}

static void fix_statfs64(struct statfs64 *buf) {
    if (!buf) return;
    buf->f_frsize = 4096;
    buf->f_bsize = 4096;
    unsigned long long total_blocks = (cfg_disk_gb * 1024ULL * 1024ULL * 1024ULL) / 4096ULL;
    unsigned long long used_blocks = (total_blocks * 8ULL) / 100ULL;
    if (used_blocks == 0) used_blocks = 200000ULL;
    buf->f_blocks = total_blocks;
    buf->f_bfree = total_blocks - used_blocks;
    buf->f_bavail = buf->f_bfree;
    buf->f_files = total_blocks / 4;
    buf->f_ffree = buf->f_files - 100000;
}

int statvfs(const char *path, struct statvfs *buf) {
    load_config();
    int (*orig_statvfs)(const char *, struct statvfs *) = dlsym(RTLD_NEXT, "statvfs");
    int res = orig_statvfs(path, buf);
    if (res == 0 && is_root_fs(path)) {
        fix_statvfs(buf);
    }
    return res;
}

int statvfs64(const char *path, struct statvfs64 *buf) {
    load_config();
    int (*orig_statvfs64)(const char *, struct statvfs64 *) = dlsym(RTLD_NEXT, "statvfs64");
    if (!orig_statvfs64) orig_statvfs64 = dlsym(RTLD_NEXT, "statvfs");
    int res = orig_statvfs64(path, buf);
    if (res == 0 && is_root_fs(path)) {
        fix_statvfs64(buf);
    }
    return res;
}

int statfs(const char *path, struct statfs *buf) {
    load_config();
    int (*orig_statfs)(const char *, struct statfs *) = dlsym(RTLD_NEXT, "statfs");
    int res = orig_statfs(path, buf);
    if (res == 0 && is_root_fs(path)) {
        fix_statfs(buf);
    }
    return res;
}

int statfs64(const char *path, struct statfs64 *buf) {
    load_config();
    int (*orig_statfs64)(const char *, struct statfs64 *) = dlsym(RTLD_NEXT, "statfs64");
    if (!orig_statfs64) orig_statfs64 = dlsym(RTLD_NEXT, "statfs");
    int res = orig_statfs64(path, buf);
    if (res == 0 && is_root_fs(path)) {
        fix_statfs64(buf);
    }
    return res;
}
