name: Ubuntu 24.04 VPS with Password SSH

on:
  workflow_dispatch: # Manual trigger ke liye

jobs:
  vps-session:
    runs-on: ubuntu-24.04
    timeout-minutes: 350 # 6 ghante se thoda kam, kyunki runner ka maximum time limit hai

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Install Tailscale
        run: |
          curl -fsSL https://tailscale.com/install.sh | sh
          sudo tailscaled &
          sleep 5

      - name: Connect to Tailscale
        run: |
          # Yahan apni Tailscale Auth Key use karein, ya GitHub Secrets mein rakhein
          sudo tailscale up --authkey ${{ secrets.TAILSCALE_AUTHKEY }} --hostname github-vps-$(date +%s)
          sleep 10
          echo "Tailscale IP: $(tailscale ip -4)"
          echo "VPS_IP=$(tailscale ip -4)" >> $GITHUB_ENV

      - name: Setup SSH with Password
        run: |
          # 1. SSH server install karein
          sudo apt update
          sudo apt install -y openssh-server

          # 2. Password set karein (yahan demo password hai, ise badal dein!)
          # Format: username:password
          echo "runner:YourStrongPassword123!" | sudo chpasswd

          # 3. SSH configuration modify karein taaki password login allow ho
          # Ubuntu 24.04 aam taur par sshd_config.d mein config include karta hai
          sudo sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
          # Agar upar wala command kaam na kare, toh forced override file banayein
          echo "PasswordAuthentication yes" | sudo tee /etc/ssh/sshd_config.d/99-enable-password.conf
          
          # 4. SSH service restart karein
          sudo systemctl restart ssh

          # 5. Verify karein (optional, logs mein dikhega)
          sudo sshd -T | grep passwordauthentication

      - name: Keep Session Alive
        run: |
          echo "=========================================="
          echo "VPS taiyar hai!"
          echo "IP: ${{ env.VPS_IP }}"
          echo "Username: runner"
          echo "Password: YourStrongPassword123! (script mein set kiya gaya)"
          echo "=========================================="
          # Session ko chalaye rakhein
          sleep 6h
