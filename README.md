# FinSight Agent - Multi-Agentic Financial Research System

A sophisticated multi-agent system for financial research that combines stock data analysis, news research, and AI-powered synthesis to generate comprehensive company reports.

## 🎯 What It Does

The **FinSight Agent** is a multi-agent system that performs comprehensive financial research on public companies. When given a company's stock ticker or name, it:

1. **Fetches real-time stock data** (price, market cap, P/E ratio, dividend yield)
2. **Searches for recent news articles** about the company
3. **Synthesizes the information** into a professional, actionable report

## 🏗️ Architecture

### Multi-Agent System
- **Data Analyst Agent**: Fetches and analyzes stock market data
- **News Researcher Agent**: Finds and summarizes relevant financial news
- **Manager Agent**: Synthesizes data and news into comprehensive reports

### Tools & APIs
- **yfinance**: Real-time stock data
- **DuckDuckGo Search**: News article retrieval
- **Yahoo Finance API**: Ticker symbol lookup
- **OpenAI GPT-4**: AI-powered analysis and synthesis

### Evaluation & Observability
- **Phoenix OpenTelemetry**: Distributed tracing and observability
- **Custom Evaluator**: Comprehensive metrics including performance, cost efficiency, content quality
- **CSV Export**: Detailed evaluation results with 8+ metrics

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd finsight

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env_example.txt .env
# Edit .env with your API keys
```

### 2. Configure API Keys

Create a `.env` file with your API keys:

#### Setting up Phoenix OpenTelemetry (Optional)
1. Go to [Phoenix](https://phoenix.arize.com/)
2. Sign up for a free account
3. Create a new project
4. Get your API key and collector endpoint
5. Add them to your `.env` file

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (for observability)
# Get these from https://phoenix.arize.com/ (free tier)
PHOENIX_API_KEY=your_phoenix_api_key_here
PHOENIX_COLLECTOR_ENDPOINT=your_collector_endpoint_here

### 3. Run Analysis

```bash
# Analyze a single company
python main.py "Microsoft"

# Or run interactively
python main.py
# Then enter: Microsoft
```

### 4. Run Evaluations

```bash
# Run comprehensive evaluation on test cases
python run_evaluations.py
```

### 5. Test System Components

```bash
# Test enhanced evaluation system
python test_enhanced_eval.py

# Run comprehensive evaluation
python run_evaluations.py --enhanced
```

## 📊 Evaluation System

The evaluation system tests 8+ key aspects:

### 1. Performance Metrics
- **Response Time**: Tracks execution time with grading (excellent/good/poor/unacceptable)
- **Cost Efficiency**: Token usage and estimated API costs
- **Content Quality**: Sentiment analysis, readability scores, and completeness

### 2. Reliability Metrics
- **Graceful Failure Handling**: Detects and evaluates error reporting quality
- **News Relevance**: Financial keyword density and relevance scoring
- **Ticker Accuracy**: Correct identification of stock symbols
- **Sector Relevance**: Industry-specific content detection

### 3. Consistency Testing
- **Factual Consistency**: Price accuracy verification
- **Price Range Validation**: 52-week high/low boundary checking

## 🔧 Key Features

### Robust Error Handling
- **Failure-aware agents**: Clear instructions to stop on errors
- **Max retries**: Prevents infinite loops (max_retries=2)
- **Rate limiting protection**: Built-in delays and error detection

### Tool Reliability
- **Direct API calls**: Yahoo Finance API for ticker lookup
- **Fallback mechanisms**: Multiple data sources
- **Structured outputs**: Consistent error reporting

### Observability
- **Phoenix OpenTelemetry integration**: Automatic tracing and monitoring
- **Detailed logging**: Agent interactions and tool calls
- **Evaluation metrics**: Quantitative performance tracking with 8+ metrics

## 📈 Example Output

```
🔍 Starting FinSight analysis for: Microsoft
============================================================

📊 FINAL REPORT
============================================================

# Microsoft Corporation (MSFT) - Financial Research Report

## Executive Summary
Microsoft Corporation (MSFT) is currently trading at $415.26 per share with a market 
capitalization of $3.09 trillion. The company shows strong financial metrics with a 
P/E ratio of 36.8 and continues to demonstrate robust performance in the technology sector.

## Current Financial Position
- **Stock Price**: $415.26 USD
- **Market Capitalization**: $3.09 trillion
- **P/E Ratio**: 36.8
- **Dividend Yield**: 0.7%

## Recent News Analysis
Recent news indicates Microsoft's continued focus on AI integration across its product 
suite, with significant investments in OpenAI and Azure AI services. The company's 
cloud computing division continues to show strong growth, contributing to positive 
market sentiment.

## Key Insights
1. Strong market position with trillion-dollar valuation
2. Continued AI leadership through strategic partnerships
3. Robust cloud computing growth driving revenue
4. Stable dividend policy providing shareholder value

## Risk Factors
- High P/E ratio suggests premium valuation
- Dependency on cloud computing market growth
- Competition in AI and cloud services intensifying

============================================================
✅ Analysis complete!
```

## 🧪 Evaluation Results

The evaluation system provides detailed metrics:

```
📊 Evaluation Summary
============================================================
✅ Successful evaluations: 30+
📈 Average overall score: 0.65

  📊 response_time: 1.0 (excellent range: 18-45s)
  📊 cost_efficiency: 1.0 (excellent: $0.03-0.05 per analysis)
  📊 content_quality: 0.52 (moderate, room for improvement)
  📊 graceful_failure: 0.6 (mixed results)
  📊 news_relevance: 0.24 (below target thresholds)
  📊 ticker_accuracy: 0.8 (good accuracy)
  📊 sector_relevance: 0.6 (moderate sector detection)

🎯 Key Insights from Evaluation
============================================================
1. **Cost Efficiency**: Excellent token usage optimization
2. **Response Time**: Generally good, with some variability
3. **Content Quality**: Moderate scores, room for improvement
4. **News Relevance**: Below target thresholds, indicating need for better filtering
```

## 🔍 Lessons Learned

### Production Risks Identified

1. **Hallucination & Factual Drift**: LLMs sometimes "paraphrase" numbers
2. **Tool Errors & Agent Fragility**: Network failures can cause infinite loops
3. **Instrumentation Complexity**: Observability setup can be challenging

### Solutions Implemented

1. **Robust Error Handling**: Clear failure instructions and retry limits
2. **Tool Fortification**: Reliable APIs with fallback mechanisms
3. **Evaluation Framework**: Systematic testing of system behavior

## 🛠️ Development

### Project Structure
```
finsight/
├── main.py              # Main application entry point
├── agents.py            # Agent definitions
├── tasks.py             # Task definitions
├── tools.py             # Financial data tools
├── evaluations.py       # Evaluation system
├── run_evaluations.py   # Evaluation runner
├── requirements.txt     # Dependencies
├── env_example.txt      # Environment variables template
└── README.md           # This file
```

### Adding New Tools
1. Add tool function to `tools.py`
2. Update agent definitions in `agents.py`
3. Modify task descriptions in `tasks.py`
4. Test with evaluation system

### Extending Evaluations
1. Add new evaluation method to `FinSightEvaluator`
2. Update `run_evaluation()` method
3. Modify CSV export fields
4. Add to test cases in `run_evaluations.py`

## 🚀 Quick Reproduction Guide

### For New Users (Fork & Run)

1. **Fork this repository** to your GitHub account
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/finsight.git
   cd finsight
   ```

3. **Set up the environment**:
   ```bash
   # Create virtual environment
   python -m venv finsight_env
   source finsight_env/bin/activate  # On Windows: finsight_env\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

4. **Configure API keys**:
   ```bash
   # Copy environment template
   cp env_example.txt .env
   
   # Edit .env with your OpenAI API key (required)
   # Optional: Add Phoenix API key for observability
   ```

5. **Test the system**:
   ```bash
   # Run a quick test
   python main.py "Microsoft"
   
   # Run comprehensive evaluation
   python run_evaluations.py --enhanced
   ```

### Expected Results

- **Single Analysis**: 18-45 seconds response time
- **Cost**: $0.03-0.05 per analysis
- **Evaluation**: 30+ companies tested with detailed CSV output
- **Files Generated**: `enhanced_evaluation_results.csv`, `evaluation_report.json`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run the evaluation suite
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **CrewAI**: Multi-agent framework
- **OpenAI**: LLM capabilities
- **Phoenix**: Observability platform
- **yfinance**: Financial data access 