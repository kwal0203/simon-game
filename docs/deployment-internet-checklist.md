# Simon Game Internet Deployment Checklist

Use this sequence to deploy the Simon Game to the public internet on AWS EC2.

1. Launch an EC2 instance.
2. Attach a security group with inbound rules:
   - `22` (SSH) from `My IP`
   - `80` (HTTP) from `0.0.0.0/0`
   - `443` (HTTPS) from `0.0.0.0/0`
3. Allocate an Elastic IP.
4. Associate the Elastic IP with the EC2 instance.
5. Point domain DNS `A` records (`@` and `www`) to the Elastic IP.
6. SSH into the running EC2 instance.
7. Install Docker and Docker Compose.
8. Add `ec2-user` to the `docker` group, then reconnect SSH.
9. Clone the repository on EC2 (for example: `~/apps/simon-game`).
10. Start services:
    - `docker compose up --build -d`
11. Run database migrations:
    - `docker compose run --rm api uv run alembic upgrade head`
12. Configure Nginx + Let's Encrypt certificates, then restart Nginx.
13. Verify deployment:
    - `http://<domain>` redirects to `https://<domain>`
    - Game loads at `https://<domain>`
    - API/database health endpoint works (`/health/db`)

## Optional Cleanup to Avoid Cost

When pausing work:
1. Stop or terminate EC2 instance.
2. Release Elastic IP if not needed.
3. Keep DNS updated when a new Elastic IP is allocated.

## Docker Install (Amazon Linux 2023)

```bash
sudo dnf update -y
sudo dnf install -y docker git
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user

sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL https://github.com/docker/compose/releases/download/v2.39.4/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

docker --version
docker compose version
```

Reconnect SSH after `usermod -aG docker ec2-user` so Docker group permissions take effect.

## Step 12 Detailed: Nginx + Let's Encrypt

1. Ensure Nginx has an HTTP server block with ACME challenge path:
   - `location /.well-known/acme-challenge/ { root /var/www/certbot; }`
2. Ensure `docker-compose.yml` mounts:
   - `./certbot/www:/var/www/certbot`
   - `./certbot/conf:/etc/letsencrypt`
3. Install Certbot on EC2 host:

```bash
sudo dnf install -y certbot
```

4. Start Nginx on HTTP first:
   - `docker compose up -d nginx`
5. Issue certificate from EC2 host:

```bash
sudo certbot certonly --webroot \
  -w /home/ec2-user/apps/simon-game/certbot/www \
  -d your-domain.com \
  -d www.your-domain.com \
  --email you@example.com \
  --agree-tos \
  --no-eff-email
```

Important: `sudo certbot` writes certs to host path `/etc/letsencrypt`, but Nginx container reads from the bind mount `./certbot/conf:/etc/letsencrypt`.
Sync certs into the mounted project path before starting HTTPS Nginx:

```bash
mkdir -p ./certbot/conf
sudo rsync -a /etc/letsencrypt/ ./certbot/conf/
sudo chown -R ec2-user:ec2-user ./certbot/conf
```

6. Configure Nginx TLS certificate paths in HTTPS (`443`) server block:
   - `/etc/letsencrypt/live/your-domain.com/fullchain.pem`
   - `/etc/letsencrypt/live/your-domain.com/privkey.pem`
7. Set HTTP (`80`) server block to redirect to HTTPS.
8. Recreate/restart Nginx:

```bash
docker compose up -d --force-recreate nginx
docker compose logs nginx --tail=100
```

9. Validate HTTPS:
   - `curl -Ik https://your-domain.com`
