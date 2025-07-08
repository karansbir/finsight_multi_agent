import os
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="phoenix.otel.otel")
from tracing import tracer  # Import the Phoenix tracer

import sys
from typing import Optional
from dotenv import load_dotenv
from crewai import Crew, Process
from agents import FinSightAgents
from tasks import FinSightTasks

# Load environment variables
load_dotenv()

@tracer.chain
def run_finsight_analysis(company_input: str, sector: Optional[str] = None) -> str:
    """
    Run the FinSight Agent analysis for a given company.
    
    Args:
        company_input: Company name or ticker symbol (e.g., 'Microsoft', 'MSFT', 'TSLA')
        sector: Optional sector information for enhanced analysis (e.g., 'Tech', 'Retail', 'F&B')
        
    Returns:
        Comprehensive financial research report
    """
    print(f"🔍 Starting FinSight analysis for: {company_input}")
    if sector:
        print(f"📊 Sector context: {sector}")
    print("=" * 60)
    
    # Create tasks with sector context
    data_task = FinSightTasks.create_data_analysis_task(company_input, sector)
    news_task = FinSightTasks.create_news_research_task(company_input, sector)
    synthesis_task = FinSightTasks.create_synthesis_task(sector)
    
    # Create crew
    crew = Crew(
        agents=[
            FinSightAgents.create_data_analyst_agent(),
            FinSightAgents.create_news_researcher_agent(),
            FinSightAgents.create_manager_agent()
        ],
        tasks=[data_task, news_task, synthesis_task],
        process=Process.sequential,
        verbose=False
    )
    
    print("🚀 Crew Execution Started")
    print("=" * 60)
    
    # Execute the crew
    try:
        result = crew.kickoff()
        print("✅ Crew Execution Completed")
        print("=" * 60)
        return str(result)
    except Exception as e:
        error_msg = f"Error during FinSight analysis: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

def main():
    """Main function to run the FinSight Agent."""
    print("🚀 Welcome to FinSight Agent - Financial Research Assistant")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables.")
        print("Please set your OpenAI API key in the .env file.")
        sys.exit(1)
    
    # Get company input
    if len(sys.argv) > 1:
        company_input = sys.argv[1]
    else:
        company_input = input("Enter company name or ticker symbol: ").strip()
    
    if not company_input:
        print("❌ No company input provided.")
        sys.exit(1)
    
    # Run analysis
    result = run_finsight_analysis(company_input)
    
    # Display results
    print("\n" + "=" * 60)
    print("📊 FINAL REPORT")
    print("=" * 60)
    print(result)
    print("=" * 60)
    print("✅ Analysis complete!")

if __name__ == "__main__":
    main() 