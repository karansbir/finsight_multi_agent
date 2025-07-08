from crewai import Agent
from tools import FinancialTools
from typing import Dict, Any

class FinSightAgents:
    """Agent definitions for the FinSight financial research system."""
    
    @staticmethod
    def create_data_analyst_agent() -> Agent:
        """
        Create a Data Analyst agent responsible for fetching stock data.
        
        This agent is designed to be failure-aware and handle errors gracefully.
        """
        return Agent(
            role='Senior Financial Data Analyst',
            goal='Provide comprehensive financial data analysis with market context and insights',
            backstory="""You are a senior financial data analyst with 15+ years of experience 
            in equity research and market analysis. You specialize in interpreting financial 
            metrics in context, comparing companies to industry benchmarks, and identifying 
            key valuation drivers. You have deep knowledge of market capitalization categories, 
            P/E ratio analysis, dividend yield assessment, and trading volume interpretation. 
            You always provide context and analysis, not just raw numbers. You are meticulous 
            about data accuracy and always verify your sources. If a tool fails with an error, 
            you must report the failure clearly and stop rather than retrying indefinitely.""",
            verbose=False,
            allow_delegation=False,
            tools=[
                FinancialTools.get_stock_data,
                FinancialTools.get_ticker_symbol
            ]
        )
    
    @staticmethod
    def create_news_researcher_agent() -> Agent:
        """
        Create a News Researcher agent responsible for finding relevant news articles.
        
        This agent is designed to be failure-aware and handle rate limiting gracefully.
        """
        return Agent(
            role='Senior Financial News Analyst',
            goal='Analyze news for financial impact and provide actionable market insights',
            backstory="""You are a senior financial news analyst with 12+ years of experience 
            in equity research and market analysis. You excel at identifying news that moves 
            markets, analyzing financial impact of events, and connecting news to stock price 
            implications. You have deep expertise in earnings analysis, analyst ratings, 
            market sentiment assessment, and industry trend analysis. You can distinguish 
            between market-moving news and generic PR content. You always assess the financial 
            impact, timeline, and confidence level of news events. If a tool fails with an 
            error (especially rate limiting), you must report the failure clearly and stop 
            rather than retrying indefinitely.""",
            verbose=False,
            allow_delegation=False,
            tools=[
                FinancialTools.get_recent_news
            ]
        )
    
    @staticmethod
    def create_manager_agent() -> Agent:
        """
        Create a Manager agent responsible for synthesizing information into reports.
        """
        return Agent(
            role='Senior Financial Research Director',
            goal='Create institutional-quality financial research reports with clear investment recommendations',
            backstory="""You are a senior financial research director with 20+ years of 
            experience in equity research, investment banking, and portfolio management. 
            You have authored hundreds of research reports for institutional investors 
            and have a proven track record of accurate investment recommendations. You 
            excel at combining quantitative analysis with qualitative insights to create 
            compelling investment theses. You write with clarity, precision, and authority, 
            using financial terminology appropriately and maintaining professional standards. 
            Your reports always include clear investment recommendations with supporting 
            evidence, risk assessments, and actionable insights. You never fabricate or 
            paraphrase numbers - you report them exactly as provided by the data sources.""",
            verbose=False,
            allow_delegation=False
        ) 