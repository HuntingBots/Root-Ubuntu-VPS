FROM ubuntu:22.04

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive
ENV SHELL=/bin/bash
ENV PORT=7681

# Install core packages, network tools, SSH server, and build utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    curl \
    wget \
    git \
    sudo \
    openssh-server \
    openssh-client \
    net-tools \
    iproute2 \
    iputils-ping \
    dnsutils \
    iptables \
    procps \
    htop \
    tmux \
    screen \
    nano \
    vim \
    unzip \
    tar \
    ca-certificates \
    python3 \
    python3-pip \
    nodejs \
    npm \
    build-essential \
    tmate \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install Tailscale
RUN curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.noarmor.gpg | tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null \
    && curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.tailscale-keyring.list | tee /etc/apt/sources.list.d/tailscale.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends tailscale \
    && rm -rf /var/lib/apt/lists/*

# Install ttyd, cloudflared, and ngrok (multi-arch support for amd64 & arm64)
RUN ARCH=$(dpkg --print-architecture) && \
    if [ "$ARCH" = "amd64" ]; then \
        curl -fsSL -o /usr/local/bin/ttyd https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.x86_64 && \
        curl -fsSL -o /usr/local/bin/cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 && \
        curl -fsSL https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz | tar -xz -C /usr/local/bin; \
    elif [ "$ARCH" = "arm64" ]; then \
        curl -fsSL -o /usr/local/bin/ttyd https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.aarch64 && \
        curl -fsSL -o /usr/local/bin/cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 && \
        curl -fsSL https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz | tar -xz -C /usr/local/bin; \
    fi && \
    chmod +x /usr/local/bin/ttyd /usr/local/bin/cloudflared /usr/local/bin/ngrok 2>/dev/null || true

# SSH server configuration
RUN mkdir -p /var/run/sshd /root/.ssh && \
    sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    mkdir -p /etc/ssh/sshd_config.d && \
    echo "PermitRootLogin yes" > /etc/ssh/sshd_config.d/root.conf && \
    echo "PasswordAuthentication yes" > /etc/ssh/sshd_config.d/password.conf

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Working directory
WORKDIR /root

# Expose default Web Terminal & SSH ports
EXPOSE 7681 22

ENTRYPOINT ["/entrypoint.sh"]
