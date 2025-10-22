# 🚀 QuickNews - Cloudflare Deployment Quick Start

**Your Django app is ready to deploy to Cloudflare Containers!**

---

## ✅ What's Been Created

All deployment files are ready:

```
✅ Dockerfile                    - Container image definition
✅ wrangler.jsonc                - Cloudflare configuration
✅ src/index.js                  - Worker router
✅ .dockerignore                 - Build optimization
✅ requirements.txt              - Updated with gunicorn + whitenoise
✅ DjangoNews/settings_production.py  - Production settings
✅ .env.production.example       - Environment variables template
✅ backup_sqlite.sh              - Database backup script
✅ DEPLOYMENT.md                 - Complete deployment guide
```

---

## 🎯 Deploy in 3 Steps

### Step 1: Setup (5 minutes)

```bash
# 1. Install Wrangler CLI
npm install -g wrangler

# 2. Login to Cloudflare
wrangler login

# 3. Subscribe to Workers Paid Plan ($5/month)
# Visit: https://dash.cloudflare.com → Workers & Pages → Purchase
```

### Step 2: Configure (2 minutes)

```bash
# 1. Create your .env file
cp .env.production.example .env

# 2. Generate a new SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 3. Edit .env and paste the SECRET_KEY
nano .env

# Example .env:
# SECRET_KEY=django-insecure-xyz123abc...
# DEBUG=False
# ALLOWED_HOSTS=*.workers.dev
```

### Step 3: Deploy (10 minutes)

```bash
# 1. Test Docker build locally
docker build -t quicknews-django .

# 2. Test locally (optional)
docker run -p 8080:8080 --env-file .env quicknews-django

# 3. Deploy to Cloudflare
wrangler deploy

# 4. Watch deployment
wrangler tail

# ✅ Your app will be live at:
# https://quicknews-django.<your-subdomain>.workers.dev
```

---

## 📋 Environment Variables You Need

**Only 3 required variables:**

1. **SECRET_KEY** - Django secret (generate new one)
2. **DEBUG** - Must be `False` in production
3. **ALLOWED_HOSTS** - Your domain(s), e.g., `*.workers.dev`

**That's it!** Everything else has defaults.

---

## 🎓 For Your Portfolio/Resume

**What You Can Say:**

✨ "Deployed Django application on Cloudflare's global edge network using Docker containers"

✨ "Implemented stateful containerization with Durable Objects for SQLite persistence"

✨ "Configured production deployment with WhiteNoise static file serving and security headers"

✨ "Set up CI/CD pipeline with Wrangler CLI for automated deployments"

**Tech Stack:**
- Django 5.2.7
- Docker containerization
- Cloudflare Workers & Containers
- Gunicorn WSGI server
- WhiteNoise static files
- SQLite with Durable Objects persistence
- Global edge distribution

---

## 🐛 Troubleshooting

**Issue: "Container failed to start"**
```bash
# Check logs
wrangler containers logs

# Rebuild with verbose output
docker build --progress=plain -t quicknews-django .
```

**Issue: "SECRET_KEY not set"**
```bash
# Store as Wrangler secret
wrangler secret put SECRET_KEY
# Paste your secret key when prompted
```

**Issue: "Static files not loading"**
```bash
# Verify collectstatic ran
docker run quicknews-django ls -la /app/staticfiles

# Should see CSS, JS, images
```

---

## 📊 What Happens When You Deploy

1. **Wrangler builds** your Docker image locally
2. **Image is pushed** to Cloudflare's registry
3. **Container is provisioned** on Cloudflare's edge network (5-10 min first time)
4. **SQLite database** is stored in Durable Object (persists across deployments)
5. **Static files** served by WhiteNoise from container
6. **Your app is live** globally with sub-100ms latency

---

## 💰 Cost Estimate

For a portfolio/showcase project:

| Item | Cost |
|------|------|
| Workers Paid Plan | $5/month |
| Container runtime (low traffic) | ~$0.50/month |
| Storage (10GB SQLite) | ~$0.50/month |
| **Total** | **~$6/month** |

**Free tier included:**
- SSL certificate
- DDoS protection
- Global CDN
- 1TB network egress

---

## 🔗 Quick Links

- **Cloudflare Dashboard:** https://dash.cloudflare.com
- **Wrangler Docs:** https://developers.cloudflare.com/workers/wrangler/
- **Full Deployment Guide:** See `DEPLOYMENT.md`
- **Get Help:** https://discord.gg/cloudflaredev

---

## ✅ Pre-Deployment Checklist

Before `wrangler deploy`:

- [ ] Docker installed and running
- [ ] Node.js & npm installed
- [ ] Wrangler CLI installed (`npm install -g wrangler`)
- [ ] Logged into Cloudflare (`wrangler login`)
- [ ] Workers Paid Plan active ($5/month)
- [ ] `.env` file created with SECRET_KEY
- [ ] Docker build tested locally
- [ ] Database backed up (`./backup_sqlite.sh`)

---

## 🎉 After Deployment

**Test your deployment:**

```bash
# Get your URL
wrangler deployments list

# Test homepage
curl https://quicknews-django.<your-subdomain>.workers.dev

# Check specific pages
curl https://quicknews-django.<your-subdomain>.workers.dev/business/
curl https://quicknews-django.<your-subdomain>.workers.dev/hindi/
```

**Monitor your app:**

```bash
# Live logs
wrangler tail

# Container logs
wrangler containers logs

# Cloudflare Dashboard
# → Workers & Pages → quicknews-django → Analytics
```

**Add custom domain (optional):**

1. Dashboard → DNS → Add CNAME
2. Point to your `.workers.dev` URL
3. Wait for DNS propagation (2-5 minutes)

---

## 📚 Next Steps

1. ✅ Deploy to Cloudflare
2. ✅ Test all pages work
3. ✅ Set up monitoring alerts
4. ✅ Schedule database backups (cron)
5. ✅ Add custom domain (optional)
6. ✅ Update README with live URL
7. ✅ Share on LinkedIn/portfolio! 🎓

---

**Need help?** See full guide in `DEPLOYMENT.md` or join [Cloudflare Discord](https://discord.gg/cloudflaredev)

**Ready to deploy?** Run `wrangler deploy` now! 🚀

---

*QuickNews - Django News Aggregation App*
*Deployed on Cloudflare's Global Edge Network*
