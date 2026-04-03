# Cloud Run Deployment Script for Finance Dashboard (Windows)
# Usage: .\deploy.ps1 -ProjectId "my-project" -ServiceName "finance-dashboard" -Region "us-central1"

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,
    
    [Parameter(Mandatory=$false)]
    [string]$ServiceName = "finance-dashboard",
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "us-central1"
)

# Color output functions
function Write-Status {
    Write-Host "[✓] $args" -ForegroundColor Green
}

function Write-Error-Custom {
    Write-Host "[✗] $args" -ForegroundColor Red
    exit 1
}

function Write-Warning-Custom {
    Write-Host "[!] $args" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Finance Dashboard Cloud Run Deployment" -ForegroundColor Cyan
Write-Host "Project: $ProjectId" -ForegroundColor Gray
Write-Host "Service: $ServiceName" -ForegroundColor Gray
Write-Host "Region: $Region" -ForegroundColor Gray
Write-Host ""

# Step 1: Check prerequisites
Write-Status "Checking prerequisites..."

$hasGcloud = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $hasGcloud) {
    Write-Error-Custom "gcloud CLI not found. Install from: https://cloud.google.com/sdk/docs/install"
}

$hasDocker = Get-Command docker -ErrorAction SilentlyContinue
if (-not $hasDocker) {
    Write-Error-Custom "Docker not found. Install from: https://docs.docker.com/get-docker/"
}

Write-Status "Prerequisites OK"

# Step 2: Set GCP project
Write-Status "Setting GCP project to $ProjectId..."
& gcloud config set project $ProjectId
if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Failed to set GCP project"
}

# Step 3: Enable required APIs
Write-Status "Enabling required GCP APIs..."
& gcloud services enable run.googleapis.com 2>$null
& gcloud services enable cloudbuild.googleapis.com 2>$null
& gcloud services enable containerregistry.googleapis.com 2>$null
Write-Status "APIs enabled"

# Step 4: Build Docker image
Write-Status "Building Docker image..."
& gcloud builds submit `
    --tag gcr.io/$ProjectId/$ServiceName:latest `
    --region=$Region `
    --timeout=1800s

if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Docker build failed"
}

Write-Status "Docker image built and pushed"

# Step 5: Deploy to Cloud Run
Write-Status "Deploying to Cloud Run..."
& gcloud run deploy $ServiceName `
    --image gcr.io/$ProjectId/$ServiceName:latest `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --memory 512Mi `
    --cpu 1 `
    --timeout 120 `
    --max-instances 100 `
    --set-env-vars CLOUD_RUN=true,ENVIRONMENT=production,DEBUG=false

if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Cloud Run deployment failed"
}

Write-Status "Deployment complete!"

# Step 6: Get service URL
$ServiceUrl = & gcloud run services describe $ServiceName `
    --platform managed `
    --region $Region `
    --format 'value(status.url)'

Write-Status "Service URL: $ServiceUrl"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Update .env.production with CLOUD_RUN_SERVICE_URL=$ServiceUrl"
Write-Host "2. Run database migrations:"
Write-Host "   gcloud run jobs create migrate-db --image gcr.io/$ProjectId/$ServiceName:latest --region $Region --execute -- python manage.py migrate"
Write-Host "3. View logs:"
Write-Host "   gcloud run logs read $ServiceName --platform managed --region $Region --follow"
Write-Host "4. Test API with:"
Write-Host "   curl -X POST ""$ServiceUrl/api/authentication/"" -H 'Content-Type: application/json' -d '{""email"": ""demo.admin@gmail.com"", ""password"": ""demo@admin2026""}'`n"
