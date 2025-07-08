# GCP Deployment Guide for FinSight

This guide will walk you through deploying the FinSight web application to Google Cloud Platform using Cloud Run.

## 🚀 Quick Deployment

### Prerequisites

1. **Google Cloud SDK** installed and authenticated
2. **Docker** installed locally
3. **GCP Project** with billing enabled
4. **OpenAI API Key** for the AI functionality

### Step 1: Setup GCP Project

```bash
# Set your project ID
export PROJECT_ID="your-gcp-project-id"

# Authenticate with gcloud
gcloud auth login

# Set the project
gcloud config set project $PROJECT_ID
```

### Step 2: Enable Required APIs

```bash
# Enable necessary APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### Step 3: Set Environment Variables

Create a `.env` file with your OpenAI API key:

```bash
echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
```

### Step 4: Deploy Using Script

```bash
# Make the deployment script executable
chmod +x deploy.sh

# Run the deployment
./deploy.sh
```

## 🔧 Manual Deployment

If you prefer to deploy manually, follow these steps:

### Step 1: Build and Push Docker Image

```bash
# Build the image
docker build -t gcr.io/$PROJECT_ID/finsight .

# Push to Container Registry
docker push gcr.io/$PROJECT_ID/finsight
```

### Step 2: Deploy to Cloud Run

```bash
gcloud run deploy finsight \
  --image gcr.io/$PROJECT_ID/finsight \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 900 \
  --max-instances 10 \
  --set-env-vars FLASK_ENV=production \
  --port 5000
```

### Step 3: Set Environment Variables

```bash
# Set the OpenAI API key
gcloud run services update finsight \
  --region us-central1 \
  --set-env-vars OPENAI_API_KEY=your-openai-api-key-here
```

## 🌐 Access Your Application

After deployment, you'll get a URL like:
```
https://finsight-xxxxxxxx-uc.a.run.app
```

### Test the Deployment

```bash
# Health check
curl https://your-service-url/api/health

# Test analysis (replace with your actual URL)
curl -X POST https://your-service-url/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"company_input": "Apple", "sector": "Technology"}'
```

## 📊 Monitoring and Logs

### View Logs

```bash
# View recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=finsight" --limit=50

# Stream logs in real-time
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=finsight"
```

### Monitor Performance

```bash
# View service details
gcloud run services describe finsight --region=us-central1

# Check metrics in Cloud Console
# Go to: https://console.cloud.google.com/run/detail/us-central1/finsight/metrics
```

## 🔄 Continuous Deployment

### Option 1: Cloud Build Triggers

1. Connect your GitHub repository to Cloud Build
2. Create a trigger for automatic deployment on push
3. Use the `cloudbuild.yaml` file for build configuration

### Option 2: GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Google Cloud SDK
      uses: google-github-actions/setup-gcloud@v0
      with:
        project_id: ${{ secrets.GCP_PROJECT_ID }}
        service_account_key: ${{ secrets.GCP_SA_KEY }}
    
    - name: Build and Deploy
      run: |
        gcloud auth configure-docker
        docker build -t gcr.io/${{ secrets.GCP_PROJECT_ID }}/finsight .
        docker push gcr.io/${{ secrets.GCP_PROJECT_ID }}/finsight
        gcloud run deploy finsight \
          --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/finsight \
          --region us-central1 \
          --platform managed \
          --allow-unauthenticated
```

## 🔒 Security Considerations

### Environment Variables

- Store sensitive data in Secret Manager
- Use environment variables for configuration
- Never commit API keys to version control

### IAM Permissions

```bash
# Create a service account for deployment
gcloud iam service-accounts create finsight-deployer \
  --display-name="FinSight Deployer"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:finsight-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:finsight-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"
```

## 💰 Cost Optimization

### Resource Configuration

- **Memory**: 2GB (sufficient for AI processing)
- **CPU**: 2 cores (good balance of performance and cost)
- **Max Instances**: 10 (prevents runaway costs)
- **Timeout**: 15 minutes (sufficient for analysis)

### Monitoring Costs

```bash
# View current costs
gcloud billing accounts list

# Set up billing alerts in Cloud Console
# Go to: https://console.cloud.google.com/billing
```

## 🚨 Troubleshooting

### Common Issues

1. **Port 5000 in use locally**
   - Change to port 8080 in `app.py`
   - Or disable AirPlay Receiver on macOS

2. **API Key not found**
   - Ensure `OPENAI_API_KEY` is set in environment variables
   - Check Cloud Run service configuration

3. **Build failures**
   - Check Docker build logs
   - Ensure all dependencies are in `requirements.txt`

4. **Service not responding**
   - Check Cloud Run logs
   - Verify health check endpoint
   - Check resource limits

### Debug Commands

```bash
# Check service status
gcloud run services describe finsight --region=us-central1

# View recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=finsight" --limit=10

# Test locally
docker run -p 8080:5000 --env-file .env gcr.io/$PROJECT_ID/finsight
```

## 📈 Scaling

### Automatic Scaling

Cloud Run automatically scales based on:
- Number of requests
- CPU utilization
- Memory usage

### Manual Scaling

```bash
# Update scaling configuration
gcloud run services update finsight \
  --region us-central1 \
  --max-instances 20 \
  --min-instances 1
```

## 🔄 Updates and Rollbacks

### Update Service

```bash
# Build new image
docker build -t gcr.io/$PROJECT_ID/finsight:v2 .

# Push new image
docker push gcr.io/$PROJECT_ID/finsight:v2

# Deploy new version
gcloud run services update finsight \
  --image gcr.io/$PROJECT_ID/finsight:v2 \
  --region us-central1
```

### Rollback

```bash
# List revisions
gcloud run revisions list --service=finsight --region=us-central1

# Rollback to previous revision
gcloud run services update-traffic finsight \
  --to-revisions=REVISION_NAME=100 \
  --region us-central1
```

## 🎯 Next Steps

1. **Set up monitoring** with Cloud Monitoring
2. **Configure alerts** for errors and performance
3. **Set up CI/CD** for automatic deployments
4. **Add custom domain** for your service
5. **Implement authentication** if needed
6. **Add rate limiting** for API protection

## 📞 Support

For issues with:
- **GCP Services**: Check [GCP Documentation](https://cloud.google.com/docs)
- **FinSight Application**: Check the main README and code comments
- **Deployment Issues**: Review logs and troubleshooting section above 