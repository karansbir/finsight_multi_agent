// FinSight Frontend JavaScript
class FinSightApp {
    constructor() {
        this.currentJobId = null;
        this.statusCheckInterval = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.checkHealth();
    }

    bindEvents() {
        // Form submission
        const form = document.getElementById('analysisForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }

        // New analysis button
        const newAnalysisBtn = document.getElementById('newAnalysisBtn');
        if (newAnalysisBtn) {
            newAnalysisBtn.addEventListener('click', () => this.showAnalysisForm());
        }

        // Retry button
        const retryBtn = document.getElementById('retryBtn');
        if (retryBtn) {
            retryBtn.addEventListener('click', () => this.showAnalysisForm());
        }

        // Download button
        const downloadBtn = document.getElementById('downloadBtn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.downloadReport());
        }

        // Share button
        const shareBtn = document.getElementById('shareBtn');
        if (shareBtn) {
            shareBtn.addEventListener('click', () => this.shareReport());
        }
    }

    async checkHealth() {
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            console.log('Health check:', data);
        } catch (error) {
            console.error('Health check failed:', error);
        }
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const companyInput = formData.get('company_input');
        const sector = formData.get('sector');

        if (!companyInput.trim()) {
            this.showError('Please enter a company name or ticker symbol.');
            return;
        }

        this.startAnalysis(companyInput, sector);
    }

    async startAnalysis(companyInput, sector) {
        try {
            // Show loading state
            this.showLoading(companyInput);

            // Start analysis
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    company_input: companyInput,
                    sector: sector
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to start analysis');
            }

            this.currentJobId = data.job_id;
            this.startStatusPolling();

        } catch (error) {
            console.error('Analysis start error:', error);
            this.showError(error.message);
        }
    }

    startStatusPolling() {
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
        }

        this.statusCheckInterval = setInterval(async () => {
            await this.checkStatus();
        }, 2000); // Check every 2 seconds
    }

    async checkStatus() {
        if (!this.currentJobId) return;

        try {
            const response = await fetch(`/api/status/${this.currentJobId}`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to check status');
            }

            switch (data.status) {
                case 'completed':
                    this.showResults(data);
                    this.stopStatusPolling();
                    break;
                case 'failed':
                    this.showError(data.error || 'Analysis failed');
                    this.stopStatusPolling();
                    break;
                case 'running':
                    // Continue polling
                    break;
                default:
                    console.log('Unknown status:', data.status);
            }

        } catch (error) {
            console.error('Status check error:', error);
            this.showError('Failed to check analysis status');
            this.stopStatusPolling();
        }
    }

    stopStatusPolling() {
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
            this.statusCheckInterval = null;
        }
    }

    showLoading(companyName) {
        // Hide other sections
        this.hideAllSections();

        // Show loading section
        const loadingSection = document.getElementById('loadingSection');
        const loadingCompany = document.getElementById('loadingCompany');
        
        if (loadingSection && loadingCompany) {
            loadingCompany.textContent = companyName;
            loadingSection.style.display = 'block';
            loadingSection.classList.add('fade-in');
        }
    }

    showResults(data) {
        // Hide other sections
        this.hideAllSections();

        // Show results section
        const resultsSection = document.getElementById('resultsSection');
        const resultCompany = document.getElementById('resultCompany');
        const resultSector = document.getElementById('resultSector');
        const resultContent = document.getElementById('resultContent');

        if (resultsSection) {
            // Populate results
            if (resultCompany) {
                resultCompany.textContent = data.company_input;
            }
            
            if (resultSector && data.sector) {
                resultSector.textContent = data.sector;
                resultSector.style.display = 'inline-block';
            } else if (resultSector) {
                resultSector.style.display = 'none';
            }
            
            if (resultContent) {
                resultContent.textContent = data.result;
            }

            // Show section with animation
            resultsSection.style.display = 'block';
            resultsSection.classList.add('slide-up');
        }
    }

    showError(message) {
        // Hide other sections
        this.hideAllSections();

        // Show error section
        const errorSection = document.getElementById('errorSection');
        const errorMessage = document.getElementById('errorMessage');

        if (errorSection && errorMessage) {
            errorMessage.textContent = message;
            errorSection.style.display = 'block';
            errorSection.classList.add('fade-in');
        }
    }

    showAnalysisForm() {
        // Hide other sections
        this.hideAllSections();

        // Show analysis form
        const analysisSection = document.querySelector('.analysis-section');
        if (analysisSection) {
            analysisSection.style.display = 'block';
            analysisSection.classList.add('fade-in');
        }

        // Reset form
        const form = document.getElementById('analysisForm');
        if (form) {
            form.reset();
        }

        // Reset current job
        this.currentJobId = null;
        this.stopStatusPolling();
    }

    hideAllSections() {
        const sections = [
            document.querySelector('.analysis-section'),
            document.getElementById('loadingSection'),
            document.getElementById('resultsSection'),
            document.getElementById('errorSection')
        ];

        sections.forEach(section => {
            if (section) {
                section.style.display = 'none';
                section.classList.remove('fade-in', 'slide-up');
            }
        });
    }

    downloadReport() {
        const resultContent = document.getElementById('resultContent');
        const resultCompany = document.getElementById('resultCompany');
        
        if (resultContent && resultCompany) {
            const content = resultContent.textContent;
            const company = resultCompany.textContent;
            
            const blob = new Blob([content], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `finsight-analysis-${company.toLowerCase().replace(/\s+/g, '-')}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }
    }

    shareReport() {
        const resultContent = document.getElementById('resultContent');
        const resultCompany = document.getElementById('resultCompany');
        
        if (resultContent && resultCompany) {
            const content = resultContent.textContent;
            const company = resultCompany.textContent;
            
            if (navigator.share) {
                navigator.share({
                    title: `FinSight Analysis: ${company}`,
                    text: content.substring(0, 100) + '...',
                    url: window.location.href
                }).catch(console.error);
            } else {
                // Fallback: copy to clipboard
                navigator.clipboard.writeText(content).then(() => {
                    this.showNotification('Report copied to clipboard!');
                }).catch(() => {
                    this.showNotification('Failed to copy report');
                });
            }
        }
    }

    showNotification(message) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #667eea;
            color: white;
            padding: 1rem 2rem;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            z-index: 1000;
            animation: slideInRight 0.3s ease-out;
        `;

        // Add animation styles
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(style);

        // Add to page
        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new FinSightApp();
});

// Add some utility functions
window.FinSightApp = {
    // Format currency
    formatCurrency: (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },

    // Format percentage
    formatPercentage: (value) => {
        return new Intl.NumberFormat('en-US', {
            style: 'percent',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value / 100);
    },

    // Format date
    formatDate: (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
}; 