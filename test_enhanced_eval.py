#!/usr/bin/env python3
"""
Quick test script for the unified evaluation system.
"""

import os
from dotenv import load_dotenv
from evaluations import FinSightEvaluator

# Load environment variables
load_dotenv()

def test_unified_evaluator():
    """Test the unified evaluator with a simple case."""
    print("🧪 Testing Unified FinSight Evaluator")
    print("=" * 50)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables.")
        print("Please set your OpenAI API key in the .env file.")
        return
    
    # Create evaluator (enhanced mode by default)
    evaluator = FinSightEvaluator(enhanced_mode=True)
    
    # Test with a simple case
    print("🔍 Testing with: Microsoft")
    
    try:
        result = evaluator.run_evaluation(
            company_input="Microsoft",
            expected_ticker="MSFT",
            sector="Technology",
            high=500.76,
            low=344.79
        )
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Overall Score: {result['overall_score']:.2f}")
            print(f"⏱️  Response Time: {result['response_time']:.2f}s")
            
            # Print individual evaluation results
            for eval_result in result['evaluations']:
                status = "✅" if eval_result['passed'] else "❌"
                print(f"  {status} {eval_result['test']}: {eval_result['score']:.2f} - {eval_result['details']}")
            
            print("\n📊 Test completed successfully!")
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    test_unified_evaluator() 