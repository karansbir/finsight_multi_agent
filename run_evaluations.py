#!/usr/bin/env python3
"""
Unified Evaluation Runner for FinSight Agent

This script runs comprehensive evaluations with advanced metrics including
performance, cost efficiency, content quality, and consistency testing.
"""

import csv
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from evaluations import FinSightEvaluator

# Load environment variables
load_dotenv()

def load_eval_set_from_csv(filename="eval_set.csv"):
    """Load evaluation set from a CSV file."""
    eval_set = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Convert numeric fields
            for key in ["52week_high", "52week_low"]:
                try:
                    row[key] = float(row[key]) if row[key] else None
                except Exception:
                    row[key] = None
            eval_set.append(row)
    return eval_set

def generate_evaluation_report(evaluator, successful_results, error_results):
    """Generate a comprehensive evaluation report."""
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_evaluations': len(evaluator.eval_results),
            'successful_evaluations': len(successful_results),
            'failed_evaluations': len(error_results),
            'success_rate': len(successful_results) / len(evaluator.eval_results) if evaluator.eval_results else 0
        },
        'performance_metrics': {},
        'test_breakdown': {},
        'insights': []
    }
    
    if successful_results:
        # Overall performance
        avg_score = sum(r['overall_score'] for r in successful_results) / len(successful_results)
        avg_response_time = sum(r['response_time'] for r in successful_results) / len(successful_results)
        
        report['performance_metrics'] = {
            'average_overall_score': avg_score,
            'average_response_time': avg_response_time,
            'best_performer': max(successful_results, key=lambda x: x['overall_score'])['company'],
            'worst_performer': min(successful_results, key=lambda x: x['overall_score'])['company']
        }
        
        # Test breakdown
        test_scores = {}
        test_pass_rates = {}
        
        for result in successful_results:
            for eval_result in result['evaluations']:
                test_name = eval_result['test']
                if test_name not in test_scores:
                    test_scores[test_name] = []
                    test_pass_rates[test_name] = []
                test_scores[test_name].append(eval_result['score'])
                test_pass_rates[test_name].append(eval_result['passed'])
        
        for test_name, scores in test_scores.items():
            avg_test_score = sum(scores) / len(scores)
            pass_rate = sum(test_pass_rates[test_name]) / len(test_pass_rates[test_name])
            report['test_breakdown'][test_name] = {
                'average_score': avg_test_score,
                'pass_rate': pass_rate,
                'total_tests': len(scores)
            }
        
        # Generate insights
        insights = []
        
        # Performance insights
        if avg_response_time > 60:
            insights.append("Response times are above optimal threshold (60s). Consider optimizing API calls or caching.")
        
        # Cost insights
        cost_efficiency_scores = [r for r in successful_results if any(e['test'] == 'cost_efficiency' for e in r['evaluations'])]
        if cost_efficiency_scores:
            avg_cost_score = sum(e['score'] for r in cost_efficiency_scores for e in r['evaluations'] if e['test'] == 'cost_efficiency') / len(cost_efficiency_scores)
            if avg_cost_score < 0.8:
                insights.append("Cost efficiency is below target. Consider using more efficient models or optimizing prompts.")
        
        # Content quality insights
        quality_scores = [r for r in successful_results if any(e['test'] == 'content_quality' for e in r['evaluations'])]
        if quality_scores:
            avg_quality_score = sum(e['score'] for r in quality_scores for e in r['evaluations'] if e['test'] == 'content_quality') / len(quality_scores)
            if avg_quality_score < 0.7:
                insights.append("Content quality needs improvement. Consider enhancing prompts or model selection.")
        
        report['insights'] = insights
    
    return report

def run_batch_evaluation(enhanced_mode: bool = True):
    """
    Run evaluation on the entire golden set.
    
    Args:
        enhanced_mode: Whether to run enhanced metrics (default: True)
    """
    mode_text = "Enhanced" if enhanced_mode else "Basic"
    print(f"🚀 Starting {mode_text} FinSight Agent Evaluation")
    print("=" * 80)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables.")
        print("Please set your OpenAI API key in the .env file.")
        sys.exit(1)
    
    # Create evaluator
    evaluator = FinSightEvaluator(enhanced_mode=enhanced_mode)
    
    # Get evaluation set from CSV
    eval_set = load_eval_set_from_csv()
    
    print(f"📋 Running {mode_text.lower()} evaluation on {len(eval_set)} test cases:")
    for i, test_case in enumerate(eval_set, 1):
        print(f"  {i}. {test_case['company_name']} - {test_case.get('sector', '')}")
    
    print("\n" + "=" * 80)
    
    # Run evaluations
    for i, test_case in enumerate(eval_set, 1):
        print(f"\n🔍 Test Case {i}/{len(eval_set)}: {test_case['company_name']}")
        print(f"Expected Ticker: {test_case.get('expected_ticker', '')}")
        print(f"Sector: {test_case.get('sector', '')}")
        print(f"52 Week High: {test_case.get('52week_high', '')}, Low: {test_case.get('52week_low', '')}")
        print("-" * 50)
        
        try:
            result = evaluator.run_evaluation(
                company_input=test_case['company_name'],
                expected_ticker=test_case.get('expected_ticker'),
                sector=test_case.get('sector'),
                high=test_case.get('52week_high'),
                low=test_case.get('52week_low')
            )
            
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Overall Score: {result['overall_score']:.2f}")
                if enhanced_mode:
                    print(f"⏱️  Response Time: {result['response_time']:.2f}s")
                
                # Print individual evaluation results
                for eval_result in result['evaluations']:
                    status = "✅" if eval_result['passed'] else "❌"
                    print(f"  {status} {eval_result['test']}: {eval_result['score']:.2f} - {eval_result['details']}")
        
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
        
        print("-" * 50)
    
    # Generate comprehensive report
    print("\n" + "=" * 80)
    print("📊 Evaluation Summary")
    print("=" * 80)
    
    # Calculate summary statistics
    successful_results = [r for r in evaluator.eval_results if 'error' not in r]
    error_results = [r for r in evaluator.eval_results if 'error' in r]
    
    if successful_results:
        avg_score = sum(r['overall_score'] for r in successful_results) / len(successful_results)
        print(f"✅ Successful evaluations: {len(successful_results)}")
        print(f"📈 Average overall score: {avg_score:.2f}")
        
        if enhanced_mode:
            avg_response_time = sum(r['response_time'] for r in successful_results) / len(successful_results)
            print(f"⏱️  Average response time: {avg_response_time:.2f}s")
        
        # Test breakdown
        test_scores = {}
        test_pass_rates = {}
        
        for result in successful_results:
            for eval_result in result['evaluations']:
                test_name = eval_result['test']
                if test_name not in test_scores:
                    test_scores[test_name] = []
                    test_pass_rates[test_name] = []
                test_scores[test_name].append(eval_result['score'])
                test_pass_rates[test_name].append(eval_result['passed'])
        
        for test_name, scores in test_scores.items():
            avg_test_score = sum(scores) / len(scores)
            passed_count = sum(test_pass_rates[test_name])
            print(f"  📊 {test_name}: {avg_test_score:.2f} ({passed_count}/{len(scores)} passed)")
    
    if error_results:
        print(f"❌ Failed evaluations: {len(error_results)}")
        for error_result in error_results:
            print(f"  - {error_result['company']}: {error_result['error']}")
    
    # Generate and save comprehensive report
    report = generate_evaluation_report(evaluator, successful_results, error_results)
    
    # Save detailed results
    output_filename = 'enhanced_evaluation_results.csv' if enhanced_mode else 'evaluation_results.csv'
    evaluator.save_results(output_filename)
    
    # Save JSON report
    json_filename = 'evaluation_report.json'
    with open(json_filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "=" * 80)
    print("🎯 Key Insights from Evaluation")
    print("=" * 80)
    
    # Generate insights
    if successful_results:
        print("1. **Factual Consistency**: Check if stock prices are reported accurately")
        print("2. **News Relevance**: Verify that news content is financially relevant")
        print("3. **Graceful Failure**: Ensure system handles errors without infinite loops")
        print("4. **Tool Reliability**: Monitor for rate limiting and API failures")
        
        if enhanced_mode:
            print("5. **Performance**: Monitor response times and optimize for speed")
            print("6. **Cost Efficiency**: Track token usage and optimize for cost")
            print("7. **Content Quality**: Ensure reports are comprehensive and well-structured")
    
    if report['insights']:
        print("\n🔍 Specific Insights:")
        for insight in report['insights']:
            print(f"  • {insight}")
    
    print(f"\n✅ Evaluation complete! Check {output_filename} for detailed results.")
    print(f"📄 Comprehensive report saved to {json_filename}")

def main():
    """Main function."""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help':
            print("FinSight Agent Evaluation Runner")
            print("Usage: python run_evaluations.py [--basic|--enhanced]")
            print("\nOptions:")
            print("  --basic     Run basic evaluation (original metrics only)")
            print("  --enhanced  Run enhanced evaluation (default, includes performance, cost, quality)")
            print("  --help      Show this help message")
            print("\nThis script runs a comprehensive evaluation of the FinSight Agent")
            print("using a predefined set of test cases covering various scenarios.")
            return
        elif sys.argv[1] == '--basic':
            run_batch_evaluation(enhanced_mode=False)
            return
        elif sys.argv[1] == '--enhanced':
            run_batch_evaluation(enhanced_mode=True)
            return
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information.")
            return
    
    # Default to enhanced mode
    run_batch_evaluation(enhanced_mode=True)

if __name__ == "__main__":
    main() 