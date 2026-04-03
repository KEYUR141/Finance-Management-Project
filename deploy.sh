#!/bin/bash

# Cloud Run Deployment Script for Finance Dashboard
# Usage: ./deploy.sh [project-id] [service-name] [region]

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
PROJECT_ID="${1:-}"
SERVICE_NAME="${2:-finance-dashboard}"
REGION="${3:-us-central1}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if PROJECT_ID is provided
if [ -z "$PROJECT_ID" ]; then
    print_error "Project ID is required"
    echo "Usage: ./deploy.sh <project-id> [service-name] [region]"
    echo "Example: ./deploy.sh my-project finance-dashboard us-central1"
    exit 1
fi

print_status "Finance Dashboard Cloud Run Deployment"
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo ""

# Step 1: Check prerequisites
print_status "Checking prerequisites..."

if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI not found. Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    print_error "Docker not found. Install from: https://docs.docker.com/get-docker/"
    exit 1
fi

print_status "Prerequisites OK"

# Step 2: Set GCP project
print_status "Setting GCP project..."
gcloud config set project $PROJECT_ID

# Step 3: Enable required APIs
print_status "Enabling required GCP APIs..."
gcloud services enable run.googleapis.com &>/dev/null
gcloud services enable cloudbuild.googleapis.com &>/dev/null
gcloud services enable containerregistry.googleapis.com &>/dev/null
print_status "APIs enabled"

# Step 4: Build Docker image
print_status "Building Docker image..."
gcloud builds submit \
    --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    --region=$REGION \
    --timeout=1800s

print_status "Docker image built and pushed"

# Step 5: Deploy to Cloud Run
print_status "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --timeout 120 \
    --max-instances 100 \
    --set-env-vars CLOUD_RUN=true,ENVIRONMENT=production,DEBUG=false

print_status "Deployment complete!"

# Step 6: Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --format 'value(status.url)')

print_status "Service URL: $SERVICE_URL"
echo ""
echo "Next steps:"
echo "1. Update .env.production with CLOUD_RUN_SERVICE_URL=$SERVICE_URL"
echo "2. Run database migrations:"
echo "   gcloud run jobs create migrate-db --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest --region $REGION --execute -- python manage.py migrate"
echo "3. View logs:"
echo "   gcloud run logs read $SERVICE_NAME --platform managed --region $REGION --follow"
echo "4. Test API:"
echo "   curl -X POST $SERVICE_URL/api/authentication/ \\
  -H 'Content-Type: application/json' \\
  -d '{\"email\": \"demo.admin@gmail.com\", \"password\": \"demo@admin2026\"}'"
