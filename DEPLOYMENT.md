# 🚀 QuickNews - Cloudflare Container Deployment Guide

Complete guide to deploying your Django QuickNews application on Cloudflare's edge network using Docker containers.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Configuration](#configuration)
4. [Local Testing](#local-testing)
5. [Cloudflare Deployment](#cloudflare-deployment)
6. [Post-Deployment](#post-deployment)
7. [Maintenance](#maintenance)
8. [Troubleshooting](#troubleshooting)

---

## 📦 Prerequisites

### Required Accounts & Tools

- [x] **Cloudflare Account** - Sign up at [cloudflare.com](https://cloudflare.com)
- [x] **Workers Paid Plan** - $5/month (required for Containers)
- [x] **Docker Desktop** - Install from [docker.com](https://docker.com)
- [x] **Node.js & npm** - Install from [nodejs.org](https://nodejs.org) (v18 or later)
- [x] **Git** - For version control

### Verify Installations

```bash
# Check Docker
docker --version
# Expected: Docker version 24.0.0 or later

# Check Node.js
node --version
# Expected: v18.0.0 or later

# Check npm
npm --version
# Expected: 9.0.0 or later
```

---

## 🛠️ Initial Setup

### Step 1: Install Wrangler CLI

Wrangler is Cloudflare's command-line tool for managing Workers and Containers.

```bash
# Install globally
npm install -g wrangler

# Verify installation
wrangler --version

# Login to Cloudflare
wrangler login
```

This will open a browser window for authentication. Grant the requested permissions.

### Step 2: Subscribe to Workers Paid Plan

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Navigate to **Workers & Pages**
3. Click **Purchase Workers Paid** ($5/month)
4. Complete payment setup

✅ **Verify**: You should see "Workers Paid" plan active in your dashboard.

### Step 3: Prepare Your Project

```bash
# Navigate to project directory
cd /home/karanjot-singh/old_project_to_new_project/new_Django_News

# Ensure all deployment files exist
ls -la Dockerfile wrangler.jsonc src/index.js
```

---

## ⚙️ Configuration

### Step 1: Create Production Environment File

```bash
# Copy the example file
cp .env.production.example .env.production

# Edit with your values
nano .env.production
```

**Required Variables:**

```env
# Generate a new secret key
SECRET_KEY=django-insecure-GENERATE-A-NEW-SECRET-KEY-HERE

# Set to False for production
DEBUG=False

# Your domain or Cloudflare Workers domain
ALLOWED_HOSTS=quicknews.yourdomain.com,*.workers.dev

# Optional: Cloudflare R2 for static files
USE_R2=False
```

**🔐 Generate a Secure Secret Key:**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 2: Configure Wrangler

Edit `wrangler.jsonc`:

```jsonc
{
  "name": "quicknews-django",  // Your app name
  "routes": [
    {
      "pattern": "quicknews.yourdomain.com/*",  // Update with your domain
      "custom_domain": true
    }
  ]
}
```

### Step 3: Set Cloudflare Secrets

Store sensitive environment variables as Wrangler secrets:

```bash
# Set SECRET_KEY
wrangler secret put SECRET_KEY
# Paste your secret key when prompted

# Verify secrets
wrangler secret list
```

---

## 🧪 Local Testing

### Step 1: Test Docker Build

```bash
# Build the Docker image
docker build -t quicknews-django .

# Expected output: Successfully built and tagged
```

### Step 2: Run Container Locally

```bash
# Run the container
docker run -p 8080:8080 --env-file .env.production quicknews-django

# Test in browser
open http://localhost:8080
```

**✅ Success Indicators:**
- Server starts without errors
- Pages load correctly
- Static files are served
- SQLite database is accessible

### Step 3: Stop Local Container

```bash
# Find container ID
docker ps

# Stop container
docker stop <container_id>
```

---

## 🌐 Cloudflare Deployment

### Step 1: Initial Deployment

```bash
# Deploy to Cloudflare
wrangler deploy

# Expected output:
# ✨ Building container...
# 📦 Uploading image...
# 🚀 Deploying to Cloudflare...
# ✅ Published to https://quicknews-django.<your-subdomain>.workers.dev
```

**⏱️ First deployment takes 5-10 minutes** (container provisioning)

**🔍 Monitor deployment:**

```bash
# Watch live logs
wrangler tail

# In another terminal, test your deployment
curl https://quicknews-django.<your-subdomain>.workers.dev
```

### Step 2: Verify Deployment

```bash
# Check deployment status
wrangler deployments list

# View container logs
wrangler containers logs
```

**Test checklist:**
- [x] Homepage loads
- [x] Category pages work (/business, /sports, etc.)
- [x] Hindi pages load (/hindi, /hindi/sports, etc.)
- [x] Static files are served
- [x] Article modals open
- [x] News scraping works

### Step 3: Custom Domain Setup (Optional)

1. **Add Domain to Cloudflare** (if not already):
   - Dashboard → Websites → Add a Site
   - Follow nameserver setup

2. **Configure Custom Domain**:
   ```bash
   wrangler deploy
   ```

3. **Update DNS**:
   - Dashboard → DNS → Add CNAME record
   - Name: `quicknews` (or `@` for root)
   - Target: `quicknews-django.<your-subdomain>.workers.dev`

4. **Verify**:
   ```bash
   curl https://quicknews.yourdomain.com
   ```

---

## 🎉 Post-Deployment

### Step 1: Database Migration (if needed)

If you made schema changes:

```bash
# SSH into container (not directly possible with Cloudflare Containers)
# Instead, run migrations before deployment:

# Locally against production database
python manage.py makemigrations
python manage.py migrate

# Rebuild and redeploy
docker build -t quicknews-django .
wrangler deploy
```

### Step 2: Create Superuser

```bash
# Locally with production database
python manage.py createsuperuser

# Rebuild with updated database
docker build -t quicknews-django .
wrangler deploy
```

### Step 3: Collect Static Files

Already handled in Dockerfile during build:
```dockerfile
RUN python manage.py collectstatic --noinput
```

### Step 4: Set Up Monitoring

**Cloudflare Dashboard:**
1. Workers & Pages → Your Worker → Analytics
2. View metrics:
   - Request volume
   - Errors
   - Response times
   - CPU usage

**Enable Email Alerts:**
1. Dashboard → Notifications
2. Create alert for:
   - High error rate
   - Deployment failures

---

## 🔧 Maintenance

### Daily Backups

Use the provided backup script:

```bash
# Make script executable
chmod +x backup_sqlite.sh

# Run manual backup
./backup_sqlite.sh

# Schedule daily backups (cron)
crontab -e

# Add this line for daily 2 AM backups:
0 2 * * * /path/to/backup_sqlite.sh
```

### Update Deployment

```bash
# 1. Make code changes

# 2. Test locally
docker build -t quicknews-django .
docker run -p 8080:8080 --env-file .env.production quicknews-django

# 3. Deploy to Cloudflare
wrangler deploy

# 4. Verify
wrangler tail
```

### Rollback Deployment

```bash
# List recent deployments
wrangler deployments list

# Rollback to specific deployment
wrangler rollback --deployment-id <deployment-id>
```

### View Logs

```bash
# Live tail logs
wrangler tail

# Filter by log level
wrangler tail --format json | jq 'select(.level == "error")'

# Container-specific logs
wrangler containers logs
```

---

## 🐛 Troubleshooting

### Issue 1: "Container failed to start"

**Symptoms**: Deployment succeeds but container doesn't respond

**Solution**:
```bash
# Check logs
wrangler containers logs

# Common causes:
# 1. Port mismatch (must be 8080)
# 2. Missing dependencies in requirements.txt
# 3. Database migration issues

# Rebuild with verbose logging
docker build --progress=plain -t quicknews-django .
```

### Issue 2: "Static files not loading"

**Symptoms**: Pages load but CSS/JS missing

**Solution**:
```bash
# Verify collectstatic ran
docker build -t quicknews-django .
docker run quicknews-django ls -la /app/staticfiles

# Check STATIC_ROOT in settings
# Ensure WhiteNoise is in MIDDLEWARE

# Redeploy
wrangler deploy
```

### Issue 3: "Database locked" errors

**Symptoms**: SQLite database timeout errors

**Solution**:
```python
# In settings_production.py, increase timeout:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'OPTIONS': {
            'timeout': 30,  # Increased from 20
            'check_same_thread': False,
        }
    }
}
```

### Issue 4: "SECRET_KEY not found"

**Symptoms**: Deployment fails with SECRET_KEY error

**Solution**:
```bash
# Verify secret is set
wrangler secret list

# Re-add secret
wrangler secret put SECRET_KEY

# Redeploy
wrangler deploy
```

### Issue 5: "Cold start latency"

**Symptoms**: First request after idle takes 5+ seconds

**Solution**:
```jsonc
// In wrangler.jsonc, adjust sleep_after:
"container": {
  "sleep_after": 600  // Increase to 10 minutes
}

// Enable keep-alive cron (already configured):
"triggers": {
  "crons": ["*/5 * * * *"]  // Ping every 5 minutes
}
```

### Issue 6: "News scraping fails"

**Symptoms**: Articles not updating

**Solution**:
```bash
# Check scraper logs
wrangler tail | grep scraper

# Verify Inshorts.com is accessible
curl -I https://inshorts.com

# Check user-agent blocking
# Add to news/scraper.py:
headers = {
    'User-Agent': 'Mozilla/5.0 (compatible; QuickNews/1.0; +https://yourdomain.com)'
}
```

---

## 📊 Performance Optimization

### 1. Enable Container Keep-Alive

Already configured in `wrangler.jsonc`:
```jsonc
"triggers": {
  "crons": ["*/5 * * * *"]  // Prevents cold starts
}
```

### 2. Optimize Docker Image Size

```bash
# Use multi-stage build (if needed)
# Current image size check:
docker images quicknews-django

# Target: <500MB
```

### 3. Database Query Optimization

```python
# Use select_related() and prefetch_related()
# In views_new.py:
headlines = Headline.objects.select_related().filter(...)
```

---

## 💰 Cost Management

### Monitor Usage

```bash
# Check current billing
wrangler billing

# View detailed metrics
# Dashboard → Workers & Pages → Usage & Billing
```

### Expected Costs (Low Traffic)

| Service | Usage | Cost/Month |
|---------|-------|------------|
| Workers Paid Plan | Base | $5.00 |
| Container Runtime | 10,000 req | ~$0.50 |
| Storage (SQLite) | 10GB | ~$0.50 |
| **Total** | | **~$6.00** |

### Cost Optimization Tips

1. **Reduce sleep_after** for low-traffic sites
2. **Remove keep-alive cron** if cost is a concern
3. **Monitor analytics** to avoid unexpected spikes

---

## 🔒 Security Checklist

- [x] `DEBUG=False` in production
- [x] `SECRET_KEY` stored in Wrangler secrets
- [x] HTTPS enforced (`SECURE_SSL_REDIRECT=True`)
- [x] Secure cookies (`SESSION_COOKIE_SECURE=True`)
- [x] XSS protection enabled
- [x] CSRF protection enabled
- [x] `.env.production` in `.gitignore`
- [x] Regular database backups
- [x] Cloudflare's DDoS protection active

---

## 📚 Additional Resources

- [Cloudflare Containers Docs](https://developers.cloudflare.com/containers/)
- [Wrangler CLI Reference](https://developers.cloudflare.com/workers/wrangler/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Cloudflare Workers Community](https://discord.gg/cloudflaredev)

---

## 🆘 Getting Help

**If you encounter issues:**

1. Check logs: `wrangler tail`
2. Search [Cloudflare Community](https://community.cloudflare.com)
3. Join [Cloudflare Discord](https://discord.gg/cloudflaredev)
4. GitHub Issues (for project-specific problems)

---

## 🎉 Success!

Your Django QuickNews app is now running on Cloudflare's global edge network!

**Share your deployment:**
- 🔗 Public URL: `https://quicknews-django.<your-subdomain>.workers.dev`
- 📊 Analytics: Cloudflare Dashboard → Workers & Pages
- 🚀 Global distribution across 300+ cities worldwide

**Next steps:**
1. Set up monitoring alerts
2. Schedule regular backups
3. Optimize performance
4. Add custom domain
5. Share your portfolio project! 🎓

---

*Generated for QuickNews Django Application - Cloudflare Container Deployment*
*Last Updated: October 2025*
