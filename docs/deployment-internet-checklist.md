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
11. Database migrations:
    - CI/CD deploys already run migrations automatically via:
      - `docker compose run --rm migrate`
    - Manual fallback (only if you are deploying without CI/CD):
      - `docker compose run --rm migrate`
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

## Milestone 3.1 Detailed: Serve Static Files from CDN (S3 + CloudFront)

Use this when moving frontend static files to CDN while keeping API on EC2.

### Architecture

- CloudFront is the public entrypoint for `electricincubator.com` and `www.electricincubator.com`.
- Static web files are served from a private S3 bucket via CloudFront OAC.
- API traffic (`/v1/*`, `/health/db`) is routed by CloudFront to EC2/Nginx origin.
- Keep frontend API calls same-origin (no `VITE_API_BASE_URL` in production).

### 0) Prerequisites

1. Ensure EC2 API origin is running and healthy before DNS cutover.
2. Ensure AWS account is allowed to create CloudFront resources.
   - If blocked with account verification error, open AWS Support case and include the exact error message.
3. Request an ACM certificate in `us-east-1` for:
   - `electricincubator.com`
   - `www.electricincubator.com`
   - Note: CloudFront requires ACM certs from `us-east-1`. Certbot certs on EC2 cannot be attached to CloudFront.

### 1) Build frontend

```bash
cd /home/kane/Projects/simon-game/apps/web
npm ci
npm run build
```

### 2) Configure AWS CLI authentication (SSO)

```bash
aws configure sso
aws sso login --profile simon-prod
aws sts get-caller-identity --profile simon-prod
```

Recommended values:
- SSO session name: `simon-sso`
- Start URL: your organization IAM Identity Center URL
- SSO region: your Identity Center region (for this account it was `us-east-2`)
- Default client region: `us-east-2`
- Profile name: `simon-prod`

### 3) Upload static files to private S3 bucket

Replace `simon-storage-prod` with your bucket name if different.

```bash
cd /home/kane/Projects/simon-game/apps/web

aws s3 sync dist/assets s3://simon-storage-prod/assets \
  --delete \
  --cache-control "public,max-age=31536000,immutable" \
  --profile simon-prod

aws s3 cp dist/index.html s3://simon-storage-prod/index.html \
  --cache-control "no-cache" \
  --content-type "text/html" \
  --profile simon-prod

aws s3 sync dist s3://simon-storage-prod \
  --exclude "assets/*" \
  --cache-control "no-cache" \
  --profile simon-prod
```

S3 bucket rules:
- Keep `Block Public Access` enabled.
- Do not add public-read bucket policy.

### 4) Create CloudFront distribution

1. Create distribution (Free plan is fine to start).
2. Add S3 origin:
   - Origin type: S3 bucket endpoint (not website endpoint)
   - Enable private bucket access via OAC (recommended)
3. Add EC2/Nginx origin:
   - Origin type: custom origin
   - Origin domain: EC2 public DNS (or stable domain pointing to EC2)
4. Behaviors:
   - Default behavior `/*` -> S3 origin (static)
   - `/v1/*` -> EC2 origin, caching disabled
   - `/health/db` -> EC2 origin, caching disabled
5. Attach ACM certificate from `us-east-1` and set aliases:
   - `electricincubator.com`
   - `www.electricincubator.com`

### 5) DNS cutover

1. Point DNS records for `@` and `www` to the CloudFront distribution domain.
2. Wait for propagation.
3. Validate end-to-end:
   - `https://electricincubator.com/` loads frontend
   - `https://electricincubator.com/v1/leaderboard` returns API response
   - Score submit and leaderboard read work from browser gameplay flow

### 6) Post-cutover cleanup

1. Optionally remove frontend runtime dependency on Vite dev server in EC2 production path.
2. Keep EC2/Nginx/API for backend origin only.
3. Keep existing CI/CD deploy for migrations/API services.

### 7) Deploying future frontend updates

For each frontend deploy:
1. Build `apps/web/dist`.
2. Upload to S3 with same cache headers.
3. Invalidate CloudFront cache:

```bash
aws cloudfront create-invalidation \
  --distribution-id <DISTRIBUTION_ID> \
  --paths "/index.html" "/" \
  --profile simon-prod
```

If needed, invalidate `/*` for full refresh (higher cost):

```bash
aws cloudfront create-invalidation \
  --distribution-id <DISTRIBUTION_ID> \
  --paths "/*" \
  --profile simon-prod
```

## Milestone 3.1 Alternative: Serve Static Files from CDN (Cloudflare)

Use this path when CloudFront is blocked/unavailable but you still want CDN edge caching in front of the existing EC2 origin.

### Architecture

- Cloudflare proxies `electricincubator.com` and `www.electricincubator.com`.
- Origin remains EC2/Nginx.
- Nginx serves built static frontend files and proxies API requests to FastAPI.
- Cloudflare caches static assets and bypasses API paths.

### 0) Preconditions

1. Ensure production uses static frontend serving from Nginx (not Vite dev server):
   - `/` serves `index.html` from built `dist`
   - `/assets/*` serves static files
   - `/v1/*` and `/health/db` proxy to API
2. Ensure EC2 security group does not expose unused dev port `5173`.

### 1) Add and onboard domain in Cloudflare

1. In Cloudflare dashboard, onboard domain `electricincubator.com`.
2. Confirm DNS records exist in Cloudflare zone:
   - `A` record `@` -> EC2 Elastic IP (Proxy status: Proxied)
   - `A` record `www` -> EC2 Elastic IP (Proxy status: Proxied) or CNAME to `@`
   - `A` record `origin` -> EC2 Elastic IP (Proxy status: DNS only / gray cloud)
3. At Namecheap, change nameservers to the Cloudflare-assigned pair.
4. Wait for delegation propagation and verify:

```bash
dig +short NS electricincubator.com @1.1.1.1
dig +short NS electricincubator.com @8.8.8.8
```

Expected: both return Cloudflare nameservers (for example `bethany.ns.cloudflare.com`, `leonidas.ns.cloudflare.com`).

CI/CD SSH note:
- Do not use proxied hostnames (`@` / `www`) for SSH deployments.
- Set GitHub Actions `EC2_HOST` secret to `origin.electricincubator.com` (or directly to Elastic IP).
- Keep `origin` as DNS-only so SSH connects directly to EC2 instead of Cloudflare IPs.

### 2) SSL/TLS in Cloudflare

1. Set SSL/TLS mode to `Full` or `Full (strict)` (preferred when origin cert is valid).
2. Enable `Always Use HTTPS` in SSL/TLS edge settings.

### 3) Create Cloudflare cache rules

In `Caching -> Cache Rules`, add:

1. Bypass API cache:
   - Match: URI Path starts with `/v1/`
   - Action: Bypass cache
2. Bypass health endpoint cache:
   - Match: URI Path equals `/health/db`
   - Action: Bypass cache
3. Cache static assets:
   - Match: URI Path starts with `/assets/`
   - Action: Eligible for cache / Cache Everything
   - Edge TTL: long-lived (or respect origin cache headers)

### 4) Validate CDN behavior

1. Confirm traffic is proxied through Cloudflare:

```bash
curl -I https://electricincubator.com
```

Expected headers include `server: cloudflare` and `cf-ray`.

2. Confirm static asset caching:

```bash
curl -I https://electricincubator.com/assets/<current-built-asset>.js
curl -I https://electricincubator.com/assets/<current-built-asset>.js
```

Expected on second request: `cf-cache-status: HIT`.

3. Confirm API is dynamic (not cached):

```bash
curl -X GET -i https://electricincubator.com/v1/leaderboard
```

Expected: `200 OK` and `cf-cache-status: DYNAMIC` (or non-HIT equivalent).

### Notes / gotchas

- `curl -I` sends `HEAD`; `/v1/leaderboard` may return `405` with `allow: GET`. Use `curl -X GET -i` for API validation.
- If you get `404` + `cf-cache-status: HIT` on an asset, you likely cached an old hashed filename. Fetch current asset names from live HTML and retry.
