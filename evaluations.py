import csv
import re
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import tiktoken
import statistics

# Make TextBlob optional to handle missing dependencies gracefully
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("Warning: TextBlob not available. Content quality metrics will be simplified.")

from main import run_finsight_analysis
from tracing import tracer

class FinSightEvaluator:
    """Unified evaluation system for the FinSight Agent with comprehensive metrics."""
    
    def __init__(self, enhanced_mode: bool = True):
        self.eval_results = []
        self.performance_baselines = {}
        self.enhanced_mode = enhanced_mode
        if enhanced_mode:
            self.token_encoder = tiktoken.get_encoding("cl100k_base")
    
    def measure_response_time(self, start_time: float, end_time: float) -> Dict[str, Any]:
        """Measure and evaluate response time performance."""
        response_time = end_time - start_time
        
        excellent_threshold = 30.0
        good_threshold = 60.0
        poor_threshold = 120.0
        
        if response_time <= excellent_threshold:
            score = 1.0
            grade = "excellent"
        elif response_time <= good_threshold:
            score = 0.8
            grade = "good"
        elif response_time <= poor_threshold:
            score = 0.5
            grade = "poor"
        else:
            score = 0.2
            grade = "unacceptable"
        
        return {
            'test': 'response_time',
            'passed': response_time <= good_threshold,
            'score': score,
            'details': f"Response time: {response_time:.2f}s ({grade})",
            'response_time': response_time,
            'grade': grade
        }
    
    def measure_cost_efficiency(self, input_text: str, output_text: str, model: str = "gpt-4") -> Dict[str, Any]:
        """Measure token usage and cost efficiency."""
        input_tokens = len(self.token_encoder.encode(input_text))
        output_tokens = len(self.token_encoder.encode(output_text))
        total_tokens = input_tokens + output_tokens
        
        cost_rates = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
        }
        
        if model in cost_rates:
            rates = cost_rates[model]
            estimated_cost = (input_tokens * rates["input"] + output_tokens * rates["output"]) / 1000
        else:
            estimated_cost = 0.0
        
        if estimated_cost <= 0.05:
            score = 1.0
            grade = "excellent"
        elif estimated_cost <= 0.10:
            score = 0.8
            grade = "good"
        elif estimated_cost <= 0.20:
            score = 0.5
            grade = "poor"
        else:
            score = 0.2
            grade = "expensive"
        
        return {
            'test': 'cost_efficiency',
            'passed': estimated_cost <= 0.10,
            'score': score,
            'details': f"Cost: ${estimated_cost:.4f}, Tokens: {total_tokens} ({grade})",
            'estimated_cost': estimated_cost,
            'total_tokens': total_tokens,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens
        }
    
    def evaluate_content_quality(self, report: str) -> Dict[str, Any]:
        """Evaluate content quality using multiple metrics."""
        if not report or len(report.strip()) < 50:
            return {
                'test': 'content_quality',
                'passed': False,
                'score': 0.0,
                'details': "Report too short or empty",
                'sentiment': 0.0,
                'readability': 0.0,
                'completeness': 0.0
            }
        
        # Check if TextBlob is available
        if not TEXTBLOB_AVAILABLE:
            # Fallback to simplified content quality assessment
            required_sections = ['summary', 'financial', 'news', 'insights', 'risk']
            section_count = sum(1 for section in required_sections if section.lower() in report.lower())
            completeness = section_count / len(required_sections)
            
            # Simple length-based quality score
            length_score = min(1.0, len(report) / 1000)  # Normalize by expected length
            quality_score = (completeness * 0.7) + (length_score * 0.3)
            
            return {
                'test': 'content_quality',
                'passed': quality_score >= 0.6,
                'score': quality_score,
                'details': f"Quality score: {quality_score:.2f} (completeness: {completeness:.2f}, length: {length_score:.2f}) - TextBlob not available",
                'sentiment': 0.0,
                'readability': 0.0,
                'completeness': completeness
            }
        
        # Full TextBlob-based analysis
        try:
            blob = TextBlob(report)
            sentiment_score = blob.sentiment.polarity
            
            sentences = len(blob.sentences)
            words = len(blob.words)
            syllables = sum(self._count_syllables(word) for word in blob.words)
            
            if sentences > 0 and words > 0:
                readability = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
                readability = max(0, min(100, readability))
            else:
                readability = 0
            
            required_sections = ['summary', 'financial', 'news', 'insights', 'risk']
            section_count = sum(1 for section in required_sections if section.lower() in report.lower())
            completeness = section_count / len(required_sections)
            
            quality_score = (sentiment_score + 1) / 2 * 0.3 + (readability / 100) * 0.4 + completeness * 0.3
            
            return {
                'test': 'content_quality',
                'passed': quality_score >= 0.6,
                'score': quality_score,
                'details': f"Quality score: {quality_score:.2f} (sentiment: {sentiment_score:.2f}, readability: {readability:.1f}, completeness: {completeness:.2f})",
                'sentiment': sentiment_score,
                'readability': readability,
                'completeness': completeness
            }
        except Exception as e:
            # Fallback if TextBlob analysis fails
            required_sections = ['summary', 'financial', 'news', 'insights', 'risk']
            section_count = sum(1 for section in required_sections if section.lower() in report.lower())
            completeness = section_count / len(required_sections)
            
            length_score = min(1.0, len(report) / 1000)
            quality_score = (completeness * 0.7) + (length_score * 0.3)
            
            return {
                'test': 'content_quality',
                'passed': quality_score >= 0.6,
                'score': quality_score,
                'details': f"Quality score: {quality_score:.2f} (completeness: {completeness:.2f}, length: {length_score:.2f}) - TextBlob analysis failed: {str(e)}",
                'sentiment': 0.0,
                'readability': 0.0,
                'completeness': completeness
            }
    
    def _count_syllables(self, word: str) -> int:
        """Simple syllable counting for readability calculation."""
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        on_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not on_vowel:
                count += 1
            on_vowel = is_vowel
        
        if word.endswith('e'):
            count -= 1
        if count == 0:
            count = 1
        return count
    
    def extract_stock_price(self, report: str) -> Optional[float]:
        """
        Extract stock price from the report using regex patterns.
        
        Args:
            report: The generated report text
            
        Returns:
            Extracted stock price as float, or None if not found
        """
        # Look for price patterns like "$123.45", "123.45", "price: 123.45"
        price_patterns = [
            r'\$(\d+\.?\d*)',  # $123.45
            r'price[:\s]*(\d+\.?\d*)',  # price: 123.45
            r'current[:\s]*(\d+\.?\d*)',  # current: 123.45
            r'(\d+\.?\d*)\s*USD',  # 123.45 USD
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, report, re.IGNORECASE)
            if matches:
                try:
                    return float(matches[0])
                except ValueError:
                    continue
        
        return None
    
    def check_factual_consistency(self, report: str, expected_price: float) -> Dict[str, Any]:
        """
        Check if the reported stock price matches the expected price.
        
        Args:
            report: The generated report
            expected_price: The expected stock price from data sources
            
        Returns:
            Dictionary with consistency check results
        """
        extracted_price = self.extract_stock_price(report)
        
        if extracted_price is None:
            return {
                'test': 'factual_consistency',
                'passed': False,
                'score': 0.0,
                'details': 'No stock price found in report',
                'expected': expected_price,
                'found': None
            }
        
        # Allow for small rounding differences (within 1%)
        tolerance = expected_price * 0.01
        difference = abs(extracted_price - expected_price)
        
        if difference <= tolerance:
            score = 1.0
            passed = True
            details = f"Price matches within tolerance ({difference:.2f} difference)"
        else:
            score = 0.0
            passed = False
            details = f"Price mismatch: expected {expected_price}, found {extracted_price} (difference: {difference:.2f})"
        
        return {
            'test': 'factual_consistency',
            'passed': passed,
            'score': score,
            'details': details,
            'expected': expected_price,
            'found': extracted_price
        }
    
    def evaluate_news_relevance(self, report: str) -> Dict[str, Any]:
        """
        Evaluate if the news content in the report is financially relevant.
        
        Args:
            report: The generated report
            
        Returns:
            Dictionary with news relevance evaluation results
        """
        # Simple heuristics for financial relevance
        financial_keywords = [
            'earnings', 'revenue', 'profit', 'loss', 'stock', 'market', 'investor',
            'quarterly', 'annual', 'growth', 'decline', 'analyst', 'rating',
            'dividend', 'buyback', 'merger', 'acquisition', 'ipo', 'sec'
        ]
        
        # Count financial keywords in the report
        report_lower = report.lower()
        keyword_count = sum(1 for keyword in financial_keywords if keyword in report_lower)
        
        # Calculate relevance score (0-1)
        if len(report) < 100:
            score = 0.0
            passed = False
            details = "Report too short to evaluate news relevance"
        else:
            # Normalize by report length and expected keyword density
            expected_keywords = len(report) / 100  # Expect ~1 keyword per 100 chars
            score = min(1.0, keyword_count / expected_keywords)
            passed = score >= 0.3  # Threshold for relevance
            details = f"Found {keyword_count} financial keywords, relevance score: {score:.2f}"
        
        return {
            'test': 'news_relevance',
            'passed': passed,
            'score': score,
            'details': details,
            'keyword_count': keyword_count
        }
    
    def check_graceful_failure(self, report: str) -> Dict[str, Any]:
        """
        Check if the system handled failures gracefully.
        
        Args:
            report: The generated report
            
        Returns:
            Dictionary with failure handling evaluation results
        """
        # Look for error indicators
        error_indicators = [
            'error', 'failed', 'unable', 'not found', 'rate limit', 'timeout',
            'connection', 'network', 'api', 'service unavailable'
        ]
        
        report_lower = report.lower()
        error_count = sum(1 for indicator in error_indicators if indicator in report_lower)
        
        # Check if report is too short (might indicate failure)
        is_too_short = len(report.strip()) < 200
        
        # Check if report contains clear error reporting
        has_error_reporting = any(indicator in report_lower for indicator in ['error', 'failed', 'unable'])
        
        if error_count > 0 and has_error_reporting:
            # System failed but reported it clearly - this is good failure handling
            score = 0.8
            passed = True
            details = f"System failed gracefully with clear error reporting ({error_count} error indicators)"
        elif error_count > 0 and not has_error_reporting:
            # System failed but didn't report it clearly
            score = 0.2
            passed = False
            details = f"System failed but error reporting was unclear ({error_count} error indicators)"
        elif is_too_short:
            # Report is suspiciously short
            score = 0.5
            passed = False
            details = "Report is unusually short, may indicate silent failure"
        else:
            # No obvious errors
            score = 1.0
            passed = True
            details = "No errors detected, system appears to have completed successfully"
        
        return {
            'test': 'graceful_failure',
            'passed': passed,
            'score': score,
            'details': details,
            'error_count': error_count,
            'report_length': len(report)
        }
    
    def extract_ticker(self, report: str) -> Optional[str]:
        # Look for ticker patterns (e.g., (AAPL), Ticker: AAPL, etc.)
        match = re.search(r'\b([A-Z]{1,6})\b', report)
        return match.group(1) if match else None

    def extract_latest_price(self, report: str) -> Optional[float]:
        # Look for price patterns like $123.45, 123.45 USD, etc.
        price_patterns = [
            r'\$(\d+\.?\d*)',
            r'price[:\s]*(\d+\.?\d*)',
            r'current[:\s]*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*USD',
        ]
        for pattern in price_patterns:
            matches = re.findall(pattern, report, re.IGNORECASE)
            if matches:
                try:
                    return float(matches[0])
                except ValueError:
                    continue
        return None

    def check_ticker_accuracy(self, report: str, expected_ticker: str) -> dict:
        extracted_ticker = self.extract_ticker(report)
        if extracted_ticker and extracted_ticker.upper() == expected_ticker.upper():
            return {
                'test': 'ticker_accuracy',
                'passed': True,
                'score': 1.0,
                'details': f'Ticker correctly identified as {extracted_ticker}',
                'expected': expected_ticker,
                'found': extracted_ticker
            }
        else:
            return {
                'test': 'ticker_accuracy',
                'passed': False,
                'score': 0.0,
                'details': f'Ticker mismatch: expected {expected_ticker}, found {extracted_ticker}',
                'expected': expected_ticker,
                'found': extracted_ticker
            }

    def check_price_range(self, report: str, high52: float, low52: float) -> dict:
        extracted_price = self.extract_latest_price(report)
        if extracted_price is None:
            return {
                'test': 'price_range',
                'passed': False,
                'score': 0.0,
                'details': 'No price found in report',
                'expected_range': f'{low52:.2f} - {high52:.2f}',
                'found': None
            }
        
        if low52 <= extracted_price <= high52:
            return {
                'test': 'price_range',
                'passed': True,
                'score': 1.0,
                'details': f'Price {extracted_price:.2f} within 52-week range',
                'expected_range': f'{low52:.2f} - {high52:.2f}',
                'found': extracted_price
            }
        else:
            return {
                'test': 'price_range',
                'passed': False,
                'score': 0.0,
                'details': f'Price {extracted_price:.2f} outside 52-week range',
                'expected_range': f'{low52:.2f} - {high52:.2f}',
                'found': extracted_price
            }

    def check_sector_relevance(self, report: str, sector: str) -> dict:
        # Simple check: does the sector keyword appear in the news section?
        sector_keywords = {
            'Technology': ['tech', 'software', 'hardware', 'ai', 'cloud', 'digital'],
            'Healthcare': ['health', 'medical', 'pharma', 'biotech', 'clinical'],
            'Finance': ['bank', 'financial', 'insurance', 'credit', 'lending'],
            'Energy': ['oil', 'gas', 'energy', 'renewable', 'solar', 'wind'],
            'Consumer': ['retail', 'consumer', 'brand', 'product', 'marketing']
        }
        
        report_lower = report.lower()
        sector_lower = sector.lower()
        
        # Check for exact sector match
        if sector_lower in report_lower:
            score = 1.0
            passed = True
            details = f'Sector "{sector}" found in report'
        else:
            # Check for related keywords
            keywords = sector_keywords.get(sector, [])
            keyword_matches = sum(1 for keyword in keywords if keyword in report_lower)
            
            if keyword_matches > 0:
                score = 0.8
                passed = True
                details = f'Found {keyword_matches} sector-related keywords'
            else:
                score = 0.3
                passed = False
                details = f'No sector "{sector}" or related keywords found'
        
        return {
            'test': 'sector_relevance',
            'passed': passed,
            'score': score,
            'details': details,
            'expected_sector': sector
        }

    @tracer.chain
    def run_evaluation(self, company_input: str, expected_price: Optional[float] = None, 
                      expected_ticker: Optional[str] = None, sector: Optional[str] = None, 
                      high: Optional[float] = None, low: Optional[float] = None) -> Dict[str, Any]:
        """
        Run comprehensive evaluation on a single company input.
        
        Args:
            company_input: Company name or ticker to analyze
            expected_price: Expected stock price for consistency checking
            expected_ticker: Expected ticker symbol
            sector: Expected sector for relevance checking
            high: 52-week high for range checking
            low: 52-week low for range checking
            
        Returns:
            Dictionary with evaluation results
        """
        start_time = time.time()
        
        try:
            # Run the actual analysis
            report = run_finsight_analysis(company_input)
            end_time = time.time()
            
            evaluations = []
            
            # Basic evaluations (always run)
            evaluations.append(self.check_graceful_failure(report))
            evaluations.append(self.evaluate_news_relevance(report))
            
            # Enhanced evaluations (if enabled)
            if self.enhanced_mode:
                evaluations.append(self.measure_response_time(start_time, end_time))
                evaluations.append(self.measure_cost_efficiency(company_input, report))
                evaluations.append(self.evaluate_content_quality(report))
            
            # Conditional evaluations based on provided data
            if expected_price is not None:
                evaluations.append(self.check_factual_consistency(report, expected_price))
            
            if expected_ticker is not None:
                evaluations.append(self.check_ticker_accuracy(report, expected_ticker))
            
            if high is not None and low is not None:
                evaluations.append(self.check_price_range(report, high, low))
            
            if sector is not None:
                evaluations.append(self.check_sector_relevance(report, sector))
            
            # Calculate overall score
            if evaluations:
                overall_score = sum(eval_result['score'] for eval_result in evaluations) / len(evaluations)
            else:
                overall_score = 0.0
            
            result = {
                'company': company_input,
                'report': report,
                'evaluations': evaluations,
                'overall_score': overall_score,
                'response_time': end_time - start_time,
                'timestamp': datetime.now().isoformat()
            }
            
            self.eval_results.append(result)
            return result
            
        except Exception as e:
            error_result = {
                'company': company_input,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.eval_results.append(error_result)
            return error_result

    def save_results(self, filename: str = 'evaluation_results.csv'):
        """Save evaluation results to CSV file."""
        if not self.eval_results:
            print("No evaluation results to save.")
            return
        
        # Determine all possible test names from all evaluations
        all_test_names = set()
        for result in self.eval_results:
            if 'evaluations' in result:
                for eval_result in result['evaluations']:
                    all_test_names.add(eval_result['test'])
        
        # Sort test names for consistent ordering
        test_names = sorted(list(all_test_names))
        
        # Create CSV headers
        headers = ['company', 'overall_score', 'response_time', 'timestamp']
        headers.extend([f'{test}_score' for test in test_names])
        headers.extend([f'{test}_passed' for test in test_names])
        headers.extend([f'{test}_details' for test in test_names])
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for result in self.eval_results:
                row = {
                    'company': result.get('company', ''),
                    'overall_score': result.get('overall_score', 0.0),
                    'response_time': result.get('response_time', 0.0),
                    'timestamp': result.get('timestamp', '')
                }
                
                # Add test-specific data
                if 'evaluations' in result:
                    for eval_result in result['evaluations']:
                        test_name = eval_result['test']
                        row[f'{test_name}_score'] = eval_result.get('score', 0.0)
                        row[f'{test_name}_passed'] = eval_result.get('passed', False)
                        row[f'{test_name}_details'] = eval_result.get('details', '')
                
                # Fill in missing values
                for test_name in test_names:
                    if f'{test_name}_score' not in row:
                        row[f'{test_name}_score'] = 0.0
                    if f'{test_name}_passed' not in row:
                        row[f'{test_name}_passed'] = False
                    if f'{test_name}_details' not in row:
                        row[f'{test_name}_details'] = ''
                
                writer.writerow(row)
        
        print(f"Results saved to {filename}")
    
    def save_enhanced_results(self, filename: str = 'enhanced_evaluation_results.csv'):
        """Alias for save_results for backward compatibility."""
        self.save_results(filename)
    
    def run_enhanced_evaluation(self, company_input: str, expected_price: Optional[float] = None, 
                               expected_ticker: Optional[str] = None, sector: Optional[str] = None, 
                               high: Optional[float] = None, low: Optional[float] = None) -> Dict[str, Any]:
        """Alias for run_evaluation for backward compatibility."""
        return self.run_evaluation(company_input, expected_price, expected_ticker, sector, high, low) 