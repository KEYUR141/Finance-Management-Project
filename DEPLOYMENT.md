# Cloud Run Deployment Guide

This guide walks you through deploying the Finance Management Dashboard to Google Cloud Run.

---

## Prerequisites

1. **Google Cloud Project** - Create one at [Google Cloud Console](https://console.cloud.google.com)
2. **gcloud CLI** - Install from [Google Cloud SDK docs](https://cloud.google.com/sdk/docs/install)
3. **Docker** - Install from [Docker official docs](https://docs.docker.com/get-docker/)
4. **Git** - For pushing to Cloud Source Repositories or GitHub

---

## Step 1: Set Up Google Cloud Project

### 1.1 Create or Select Your Project
```bash
# List your existing projects
gcloud projects list

# Set your project
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID
```

### 1.2 Enable Required APIs
```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Container Registry/Artifact Registry
gcloud services enable artifactregistry.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Enable Cloud Build (for automated deployments)
gcloud services enable cloudbuild.googleapis.com
```

### 1.3 Set Up Authentication
```bash
# Authenticate with Google Cloud
gcloud auth login

# Initialize Application Default Credentials
gcloud auth application-default login
```

---

## Step 2: Prepare Your Application

### 2.1 Update Configuration Files
Update the following with your values:

**`.env.production`:**
```env
CLOUD_RUN=true
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-new-secret-key-from-python
CLOUD_RUN_SERVICE_URL=https://your-service-name.run.app  # Set after first deployment
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

**Generate a new SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2.2 Update Dockerfile Environment (Already Done)
The Dockerfile has been updated to:
- Use `gunicorn` instead of Django dev server
- Enable `whitenoise` for static files
- Use environment variables for configuration

### 2.3 Update requirements.txt (Already Done)
`gunicorn` and `whitenoise` have been added.

### 2.4 Collect Static Files
```bash
cd Backend/project
python manage.py collectstatic --noinput --clear
```

---

## Step 3: Build and Deploy

### Option A: Deploy Using gcloud CLI (Recommended for First Time)

#### A.1 Build the Docker Image
```bash
# Set variables
export SERVICE_NAME="finance-dashboard"
export REGION="us-central1"  # Change to your preferred region

# Build the image
gcloud builds submit \
  --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
  --region=$REGION
```

#### A.2 Deploy to Cloud Run
```bash
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 120 \
  --max-instances 100 \
  --set-env-vars CLOUD_RUN=true,ENVIRONMENT=production,DEBUG=false,SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
```

**Output:**
```
Service [finance-dashboard] revision [finance-dashboard-00001-abc] has been deployed and is serving 100% of traffic.
Service URL: https://finance-dashboard-xyz123.run.app
```

#### A.3 Copy Your Service URL
After deployment, save your service URL:
```bash
# Save the URL to a variable
export SERVICE_URL=$(gcloud run services describe finance-dashboard --platform managed --region $REGION --format 'value(status.url)')

echo "Your service URL: $SERVICE_URL"
```

### Option B: Deploy Using Cloud Build (CI/CD Automation)

This option automatically builds and deploys when you push to your Git repository.

#### B.1 Connect Your Repository
```bash
# If using Cloud Source Repositories
gcloud source repos create finance-dashboard
gcloud source repos clone finance-dashboard

# OR if using GitHub
# 1. Go to https://console.cloud.google.com/cloud-build/github/connect
# 2. Click "Connect repository"
# 3. Select GitHub and authorize
# 4. Select your repo
```

#### B.2 Create Cloud Build Trigger
```bash
gcloud builds create-github-trigger \
  --repo-name=finance-dashboard \
  --repo-owner=your-github-username \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml \
  --name=deploy-to-cloudrun
```

#### B.3 Push Your Code
```bash
git add .
git commit -m "Enable Cloud Run deployment"
git push origin main
```

Cloud Build will automatically build and deploy on each push to `main`.

---

## Step 4: Run Database Migrations on Cloud Run

After initial deployment, run migrations:

```bash
# Connect to your Cloud Run container and run migrations
gcloud run services describe finance-dashboard \
  --platform managed \
  --region $REGION

# Run migrations using Cloud Run job or SSH into container
# Use Cloud SQL Proxy for secure database access
```

**Alternative: Use Cloud Tasks to Run Migrations**
```bash
# Create a one-time task to run migrations
gcloud tasks create-http-task migrate \
  --queue=default \
  --uri=https://finance-dashboard-xyz.run.app/migrate/
```

---

## Step 5: Configure Cloud SQL (Optional - For Persistent Database)

For production, use Cloud SQL PostgreSQL instead of SQLite:

### 5.1 Create Cloud SQL Instance
```bash
gcloud sql instances create finance-db \
  --database-version=POSTGRES_15 \
  --tier=db-g1-small \
  --region=$REGION \
  --availability-type=ZONAL

# Create database
gcloud sql databases create finance_db \
  --instance=finance-db

# Create user
gcloud sql users create django-user \
  --instance=finance-db \
  --password
```

### 5.2 Update Cloud Run to Use Cloud SQL
```bash
# Update your Cloud Run service to connect to Cloud SQL
gcloud run deploy $SERVICE_NAME \
  --add-cloudsql-instances=$PROJECT_ID:$REGION:finance-db \
  --set-cloudsql-instances=$PROJECT_ID:$REGION:finance-db \
  --set-env-vars USE_CLOUD_SQL=true

# Update settings.py to use cloud SQL (already configured in settings.py)
```

---

## Step 6: Set Up Monitoring and Logging

### 6.1 View Logs
```bash
# Real-time logs
gcloud run logs read $SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --limit 50 \
  --follow

# View specific date range
gcloud run logs read $SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --limit 100 \
  --start-time=2026-04-01T00:00:00Z
```

### 6.2 Set Up Alarms (Cloud Monitoring)
```bash
# View metrics in Google Cloud Console
# https://console.cloud.google.com/monitoring
```

### 6.3 Enable Application Logging
Check your logs at: `https://console.cloud.google.com/logs/query`

---

## Step 7: Configure Custom Domain (Optional)

Map your custom domain to Cloud Run:

```bash
# Map your domain
gcloud beta run domain-mappings create \
  --service=$SERVICE_NAME \
  --domain=yourdomain.com \
  --platform=managed \
  --region=$REGION

# Add DNS records as instructed by gcloud
```

---

## Step 8: Test Your Deployment

### 8.1 Test Login
```bash
curl -X POST https://your-service-url.run.app/api/authentication/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo.admin@gmail.com",
    "password": "demo@admin2026"
  }'
```

### 8.2 Test Dashboard API
```bash
# Get the access token from login, then use it
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  https://your-service-url.run.app/api/financial-records/dashboard-kpi/
```

### 8.3 Access Frontend
Open: `https://your-service-url.run.app`

---

## Step 9: Performance Optimization

### 9.1 Configure Cloud Run Settings
```bash
gcloud run deploy $SERVICE_NAME \
  --memory 512Mi \
  --cpu 2 \
  --max-instances 50 \
  --concurrency 80
```

**Settings Explanation:**
- **Memory**: 512Mi (512 MB) - Adjust based on traffic
- **CPU**: 2 - Allocated CPU cores
- **Max Instances**: 50 - Maximum concurrent containers
- **Concurrency**: 80 - Requests per container

### 9.2 Enable CDN for Static Files
```bash
# Use Cloud CDN to cache static files
gcloud compute backend-services create finance-cdn \
  --global \
  --enable-cdn \
  --cache-mode CACHE_ALL_STATIC
```

---

## Step 10: Security Configuration

### 10.1 Restrict Access
```bash
# Require authentication (remove --allow-unauthenticated)
gcloud run deploy $SERVICE_NAME \
  --no-allow-unauthenticated \
  --region $REGION \
  --platform managed
```

### 10.2 Set IAM Policies
```bash
# Allow only specific users
gcloud run services add-iam-policy-binding $SERVICE_NAME \
  --member=user:your-email@gmail.com \
  --role=roles/run.invoker \
  --region $REGION \
  --platform managed
```

### 10.3 Configure VPC Connector (For Private Database)
```bash
gcloud compute networks vpc-connectors create finance-connector \
  --network=default \
  --region=$REGION \
  --range 10.8.0.0/28

# Use with Cloud Run
gcloud run deploy $SERVICE_NAME \
  --vpc-connector=finance-connector \
  --vpc-egress=private-ranges-only
```

---

## Troubleshooting

### Issue: "Build failed with error: Docker build failed"
**Solution:**
```bash
# Check build logs in detail
gcloud builds log --stream

# Rebuild with verbose output
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:latest --timeout=1800s
```

### Issue: "Connection refused" or "Database error"
**Solution:**
- Ensure migrations have been run
- Check database configuration in `.env.production`
- View logs: `gcloud run logs read $SERVICE_NAME --platform managed --region $REGION --limit 50`

### Issue: "Static files not loading"
**Solution:**
```bash
# Collect static files and rebuild
python manage.py collectstatic --noinput --clear
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:latest
```

### Issue: "CORS errors in browser console"
**Solution:**
- Update `CORS_ALLOWED_ORIGINS` in `.env.production`
- Redeploy with correct frontend domain

---

## Cost Estimation

Google Cloud Run pricing (as of 2026):

| Item | Cost |
|------|------|
| Requests | $0.40 per 1 million requests |
| Compute (vCPU-seconds) | $0.0000275 per vCPU-second |
| Memory (GB-seconds) | $0.0000050 per GB-second |
| Free tier quota | 2 million requests/month, 360,000 GB-seconds/month |

**Estimated monthly cost** (with free tier):
- 100,000 requests/day: ~$0-5/month
- 1 million requests/day: ~$20-30/month

---

## Useful gcloud Commands

```bash
# List all Cloud Run services
gcloud run services list --platform managed

# Get service details
gcloud run services describe $SERVICE_NAME --platform managed --region $REGION

# Update environment variables
gcloud run deploy $SERVICE_NAME \
  --update-env-vars KEY=value \
  --platform managed \
  --region $REGION

# Delete service
gcloud run services delete $SERVICE_NAME --platform managed --region $REGION

# View revision history
gcloud run revisions list --service=$SERVICE_NAME --platform managed --region $REGION

# Roll back to previous version
gcloud run deploy $SERVICE_NAME \
  --revision=$OLD_REVISION_ID \
  --platform managed \
  --region $REGION
```

---

## Next Steps

1. ✅ Deploy to Cloud Run
2. 📊 Set up monitoring and alerts
3. 🔐 Configure custom domain and SSL
4. 📈 Monitor API usage and performance
5. 🗄️ Migrate to Cloud SQL for persistent storage
6. 🚀 Enable CI/CD with Cloud Build

---

**For more information:**
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [Pricing Calculator](https://cloud.google.com/pricing/calculator)
