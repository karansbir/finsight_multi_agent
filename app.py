from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="phoenix.otel.otel")
from tracing import tracer
from main import run_finsight_analysis
from dotenv import load_dotenv
import threading
import queue
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Store for active analysis jobs
active_jobs = {}

class AnalysisJob:
    def __init__(self, job_id, company_input, sector=None):
        self.job_id = job_id
        self.company_input = company_input
        self.sector = sector
        self.status = "pending"
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None
        self.progress = 0
        
    def run_analysis(self):
        """Run the analysis in a separate thread"""
        self.status = "running"
        self.start_time = time.time()
        
        try:
            # Run the analysis
            result = run_finsight_analysis(self.company_input, self.sector)
            self.result = result
            self.status = "completed"
        except Exception as e:
            self.error = str(e)
            self.status = "failed"
        finally:
            self.end_time = time.time()

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def start_analysis():
    """Start a new analysis job"""
    try:
        data = request.get_json()
        company_input = data.get('company_input', '').strip()
        sector = data.get('sector', '').strip() or None
        
        if not company_input:
            return jsonify({'error': 'Company input is required'}), 400
        
        # Generate job ID
        job_id = f"job_{int(time.time() * 1000)}"
        
        # Create and store job
        job = AnalysisJob(job_id, company_input, sector)
        active_jobs[job_id] = job
        
        # Start analysis in background thread
        thread = threading.Thread(target=job.run_analysis)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'job_id': job_id,
            'status': 'started',
            'message': f'Analysis started for {company_input}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<job_id>')
def get_status(job_id):
    """Get the status of an analysis job"""
    if job_id not in active_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = active_jobs[job_id]
    
    response = {
        'job_id': job_id,
        'status': job.status,
        'company_input': job.company_input,
        'sector': job.sector,
        'start_time': job.start_time,
        'end_time': job.end_time
    }
    
    if job.status == 'completed':
        response['result'] = job.result
    elif job.status == 'failed':
        response['error'] = job.error
    
    return jsonify(response)

@app.route('/api/jobs')
def list_jobs():
    """List all active jobs"""
    jobs = []
    for job_id, job in active_jobs.items():
        jobs.append({
            'job_id': job_id,
            'company_input': job.company_input,
            'sector': job.sector,
            'status': job.status,
            'start_time': job.start_time,
            'end_time': job.end_time
        })
    
    return jsonify({'jobs': jobs})

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'active_jobs': len(active_jobs)
    })

if __name__ == '__main__':
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables.")
        print("Please set your OpenAI API key in the .env file.")
        exit(1)
    
    print("🚀 Starting FinSight Web Application...")
    print("📊 API will be available at http://localhost:8080")
    print("🌐 Frontend will be available at http://localhost:8080")
    
    app.run(debug=True, host='0.0.0.0', port=8080) 