# FinSight Web Application

A modern, AI-powered financial research platform with a beautiful web interface. FinSight uses multi-agent AI to analyze companies, gather financial data, research news, and synthesize comprehensive reports.

## 🌟 Features

- **Modern Web Interface**: Beautiful, responsive design with real-time updates
- **AI-Powered Analysis**: Multi-agent system using CrewAI for comprehensive financial research
- **Real-time Processing**: Background job processing with live status updates
- **Export & Share**: Download reports and share results
- **Cloud-Ready**: Fully containerized and ready for GCP deployment

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask API     │    │   FinSight      │
│   (HTML/CSS/JS) │◄──►│   (app.py)      │◄──►│   Core Engine   │
│                 │    │                 │    │   (main.py)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Background    │
                       │   Jobs (Redis)  │
                       └─────────────────┘
```

## 🚀 Quick Start

### Local Development

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Run the Application**
   ```bash
   python app.py
   ```

4. **Access the Web Interface**
   Open http://localhost:5000 in your browser

### Docker Development

1. **Build the Image**
   ```bash
   docker build -t finsight .
   ```

2. **Run the Container**
   ```bash
   docker run -p 5000:5000 --env-file .env finsight
   ```

## 🌐 GCP Deployment

### Prerequisites

- Google Cloud SDK installed and authenticated
- Docker installed
- GCP project with billing enabled

### Automated Deployment

1. **Set your GCP Project ID**
   ```bash
   export PROJECT_ID="your-gcp-project-id"
   ```

2. **Run the Deployment Script**
   ```bash
   ./deploy.sh
   ```

### Manual Deployment

1. **Enable Required APIs**
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

2. **Build and Push Image**
   ```bash
   docker build -t gcr.io/$PROJECT_ID/finsight .
   docker push gcr.io/$PROJECT_ID/finsight
   ```

3. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy finsight \
     --image gcr.io/$PROJECT_ID/finsight \
     --region us-central1 \
     --platform managed \
     --allow-unauthenticated \
     --memory 2Gi \
     --cpu 2 \
     --timeout 900 \
     --max-instances 10
   ```

## 📁 Project Structure

```
finsight/
├── app.py                 # Flask web application
├── main.py               # Core FinSight analysis engine
├── agents.py             # AI agent definitions
├── tasks.py              # Task definitions
├── tools.py              # Tool definitions
├── tracing.py            # Phoenix observability
├── evaluations.py        # Evaluation framework
├── templates/
│   └── index.html        # Main web interface
├── static/
│   ├── css/
│   │   └── style.css     # Modern styling
│   └── js/
│       └── app.js        # Frontend functionality
├── Dockerfile            # Container configuration
├── cloudbuild.yaml       # GCP Cloud Build config
├── service.yaml          # Cloud Run service config
├── deploy.sh             # Deployment script
└── requirements.txt      # Python dependencies
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for AI models | Yes |
| `FLASK_ENV` | Flask environment (development/production) | No |
| `PORT` | Port for the web server (default: 5000) | No |

### GCP Configuration

The application is configured for GCP Cloud Run with:
- **Memory**: 2GB
- **CPU**: 2 cores
- **Timeout**: 15 minutes
- **Max Instances**: 10
- **Concurrency**: 80 requests per instance

## 🎨 Frontend Features

### User Interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern UI**: Clean, professional financial theme
- **Real-time Updates**: Live status updates during analysis
- **Smooth Animations**: CSS animations and transitions

### User Experience
- **Form Validation**: Client-side validation with helpful error messages
- **Loading States**: Beautiful loading animations with progress indicators
- **Error Handling**: Graceful error handling with retry options
- **Export Options**: Download reports as text files
- **Share Functionality**: Native sharing or clipboard copy

## 🔌 API Endpoints

### Health Check
```
GET /api/health
```
Returns service health status and active job count.

### Start Analysis
```
POST /api/analyze
Content-Type: application/json

{
  "company_input": "Microsoft",
  "sector": "Technology"
}
```
Starts a new financial analysis job.

### Check Status
```
GET /api/status/{job_id}
```
Returns the status and results of an analysis job.

### List Jobs
```
GET /api/jobs
```
Returns a list of all active analysis jobs.

## 🧪 Testing

### Local Testing
```bash
# Test the web interface
curl http://localhost:5000/api/health

# Test analysis endpoint
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"company_input": "Apple", "sector": "Technology"}'
```

### Production Testing
```bash
# Test deployed service
curl https://your-service-url/api/health
```

## 📊 Monitoring

The application includes:
- **Health Checks**: Built-in health check endpoint
- **Phoenix Observability**: Distributed tracing and monitoring
- **GCP Logging**: Automatic logging to Cloud Logging
- **Error Tracking**: Comprehensive error handling and reporting

## 🔒 Security

- **Non-root Container**: Runs as non-root user in Docker
- **Environment Variables**: Secure handling of API keys
- **Input Validation**: Server-side validation of all inputs
- **CORS Configuration**: Proper CORS setup for web security

## 🚀 Performance

- **Background Processing**: Non-blocking analysis jobs
- **Connection Pooling**: Efficient database and API connections
- **Caching**: Intelligent caching of frequently accessed data
- **Load Balancing**: Cloud Run automatic load balancing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the documentation
- Review the code comments
- Open an issue on GitHub

## 🎯 Roadmap

- [ ] User authentication and accounts
- [ ] Historical analysis tracking
- [ ] Advanced financial metrics
- [ ] Real-time market data
- [ ] Portfolio analysis
- [ ] API rate limiting
- [ ] Advanced caching
- [ ] Multi-language support 