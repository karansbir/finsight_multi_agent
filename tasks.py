from crewai import Task
from typing import Dict, Any, Optional
from agents import FinSightAgents

class FinSightTasks:
    """Task definitions for the FinSight financial research system."""
    
    @staticmethod
    def create_data_analysis_task(company_input: str, sector: Optional[str] = None) -> Task:
        """
        Create a task for the Data Analyst agent to fetch stock data.
        
        Args:
            company_input: Company name or ticker symbol
            
        Returns:
            Task for the Data Analyst agent
        """
        sector_context = f"""
            
            SECTOR-SPECIFIC ANALYSIS:
            - Analyze metrics in context of the {sector} sector
            - Compare to typical {sector} industry benchmarks
            - Identify {sector}-specific valuation drivers
            - Consider {sector} market trends and dynamics
            - Use {sector} industry terminology and metrics""" if sector else ""
            
        return Task(
            description=f"""Analyze the comprehensive financial data for {company_input}. 
            
            If {company_input} is a company name (not a ticker symbol), first use the 
            get_ticker_symbol tool to find the correct ticker symbol.
            
            Then use the get_stock_data tool to fetch and analyze the following information:
            
            CORE METRICS:
            - Current stock price and previous close
            - Market capitalization (with size classification: Large-cap/Mid-cap/Small-cap)
            - P/E ratio (with valuation context: High/Moderate/Low compared to industry)
            - Dividend yield (if applicable, with attractiveness assessment)
            - Trading volume (with activity level: High/Moderate/Low)
            
            ADDITIONAL ANALYSIS:
            - Company name and sector/industry
            - Currency of trading
            - Any significant price movements or patterns
            - Market cap ranking within sector (if data available)
            
            CONTEXTUAL INFORMATION:
            - Compare P/E ratio to typical industry ranges
            - Assess dividend yield attractiveness (if applicable)
            - Evaluate trading volume relative to average
            - Identify any data quality issues or missing information{sector_context}
            
            If any tool fails with an error, report the failure clearly and stop. 
            Do not retry indefinitely.
            
            Provide the data in a clear, structured format with financial context and analysis.""",
            agent=FinSightAgents.create_data_analyst_agent(),
            expected_output="""A comprehensive financial data report containing:
            - Ticker symbol and company name
            - Current stock price with previous close comparison
            - Market capitalization with size classification
            - P/E ratio with valuation context and industry comparison
            - Dividend yield with attractiveness assessment (if applicable)
            - Trading volume with activity level assessment
            - Currency and sector information
            - Financial context and analysis
            - Any errors encountered during data retrieval""",
            max_retries=2  # Prevent infinite loops
        )
    
    @staticmethod
    def create_news_research_task(company_name: str, sector: Optional[str] = None) -> Task:
        """
        Create a task for the News Researcher agent to find relevant news.
        
        Args:
            company_name: Name of the company to research
            
        Returns:
            Task for the News Researcher agent
        """
        sector_context = f"""
            
            SECTOR-SPECIFIC FOCUS:
            - Prioritize {sector} industry news and trends
            - Look for {sector}-specific regulatory changes
            - Identify {sector} competitive dynamics
            - Consider {sector} market consolidation or disruption
            - Analyze {sector} technology or innovation trends""" if sector else ""
            
        return Task(
            description=f"""Research recent news articles about {company_name} with focus on financial impact.
            
            Use the get_recent_news tool to find the 5 most recent and financially relevant 
            news articles about {company_name}. Prioritize articles that discuss:
            
            FINANCIAL PRIORITIES (in order of importance):
            1. **Earnings Reports & Financial Performance**
               - Quarterly/annual earnings results
               - Revenue growth, profit margins, EPS
               - Financial guidance and forecasts
            
            2. **Stock Price Movements & Catalysts**
               - Significant price changes and reasons
               - Analyst upgrades/downgrades
               - Price target revisions
            
            3. **Market Analysis & Ratings**
               - Buy/sell/hold recommendations
               - Market analyst coverage
               - Institutional investor activity
            
            4. **Business Developments**
               - M&A activity, partnerships, acquisitions
               - New product launches or market expansion
               - Regulatory changes affecting business
            
            5. **Industry Trends & Competition**
               - Sector-specific developments
               - Competitive positioning changes
               - Market share shifts{sector_context}
            
            AVOID: Generic PR, marketing content, or non-financial news.
            
            FOR EACH ARTICLE, ANALYZE:
            - **Financial Impact**: How will this affect stock price? (Positive/Negative/Neutral)
            - **Key Metrics**: Revenue, earnings, growth rates, market cap changes
            - **Timeline**: Immediate (days), Short-term (weeks), Medium-term (months)
            - **Confidence**: High/Medium/Low based on source credibility and data quality
            
            If the tool fails with an error (especially rate limiting), report 
            the failure clearly and stop. Do not retry indefinitely.
            
            Provide structured summaries with clear financial implications for each article.""",
            agent=FinSightAgents.create_news_researcher_agent(),
            expected_output="""A comprehensive financial news analysis including:
            - Article titles, sources, and publication dates
            - Detailed summaries with financial context
            - Impact assessment (Positive/Negative/Neutral) with reasoning
            - Key financial metrics mentioned (revenue, earnings, growth, etc.)
            - Timeline for expected impact (immediate/short/medium-term)
            - Confidence level in the analysis
            - Any errors encountered during news retrieval""",
            max_retries=2  # Prevent infinite loops
        )
    
    @staticmethod
    def create_synthesis_task(sector: Optional[str] = None) -> Task:
        """
        Create a task for the Manager agent to synthesize information into a final report.
        
        Returns:
            Task for the Manager agent
        """
        return Task(
            description="""Create a professional financial research report that combines quantitative data with qualitative analysis. 
            
            STRUCTURE YOUR REPORT EXACTLY AS FOLLOWS:
            
            # EXECUTIVE SUMMARY
            - Write 2-3 compelling sentences highlighting the most critical financial metrics and market position
            - Include current stock price, market cap, and one key insight
            - Use active voice and clear, engaging language
            
            # CURRENT FINANCIAL POSITION
            - **Stock Price**: [Exact price from data source] with [% change if available]
            - **Market Capitalization**: [Exact figure] - [Context: e.g., "Large-cap", "Mid-cap", "Small-cap"]
            - **P/E Ratio**: [Exact ratio] - [Context: "Above/below industry average" or "High/low valuation"]
            - **Dividend Yield**: [Exact yield if applicable] - [Context: "Attractive/Moderate/Low yield"]
            - **Volume**: [Trading volume] - [Context: "Above/below average trading activity"]
            
            # RECENT DEVELOPMENTS & MARKET SENTIMENT
            - Analyze each news article for financial impact
            - Connect news events to potential stock price implications
            - Identify market sentiment (bullish/bearish/neutral) with specific reasons
            - Highlight any earnings reports, analyst ratings, or market-moving events
            
            # KEY INSIGHTS & ANALYSIS
            - Provide 3-5 actionable insights based on the data and news
            - Include competitive positioning and industry context
            - Analyze valuation metrics in context of sector/industry
            - Identify growth drivers or headwinds
            - Consider sector-specific factors and trends
            
            # RISK FACTORS
            - List 2-4 specific risks with clear explanations
            - Include both company-specific and market-wide risks
            - Rate each risk as Low/Medium/High impact
            
            # INVESTMENT OUTLOOK
            - Provide a clear recommendation: Buy/Hold/Sell with reasoning
            - Include price target or valuation range if data supports it
            - Specify time horizon (short-term/medium-term/long-term)
            
            WRITING GUIDELINES:
            - Use financial terminology: P/E ratio, market cap, revenue growth, EBITDA, etc.
            - Write in active voice with clear, concise sentences
            - Target Flesch Reading Ease score of 60+ (avoid overly complex sentences)
            - Use bullet points and bold headers for readability
            - Be specific and actionable - avoid generic statements
            - Connect quantitative data with qualitative insights
            - Report exact numbers from data sources - do not round or approximate
            
            QUALITY REQUIREMENTS:
            - Minimum 800 words for comprehensive analysis
            - Include specific financial metrics and their implications
            - Provide clear investment thesis with supporting evidence
            - Use industry-specific terminology and context
            - Ensure professional tone suitable for institutional investors""",
            agent=FinSightAgents.create_manager_agent(),
            expected_output="""A comprehensive, professional financial research report with:
            - Executive summary with key metrics and insights
            - Detailed financial position with exact numbers and context
            - News analysis with financial impact assessment
            - 3-5 actionable insights with supporting evidence
            - Specific risk factors with impact ratings
            - Clear investment recommendation with reasoning
            - Professional formatting with headers, bullet points, and bold text
            - Minimum 800 words with financial terminology and active voice""",
            max_retries=1  # No retries for synthesis task
        ) 