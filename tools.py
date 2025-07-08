import yfinance as yf
import requests
import time
import threading
from typing import Dict, Any, Optional, Union
from datetime import datetime
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS
from crewai.tools import tool
from tracing import tracer  # Import the Phoenix tracer

class ErrorHandler:
    """Standardized error handling and reporting for FinSight tools."""
    
    @staticmethod
    def create_error_response(error_type: str, error_message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a standardized error response with detailed information.
        
        Args:
            error_type: Type of error (e.g., 'API_ERROR', 'TIMEOUT', 'DATA_NOT_FOUND')
            error_message: Human-readable error message
            context: Additional context information
            
        Returns:
            Standardized error response dictionary
        """
        error_response = {
            'success': False,
            'error_type': error_type,
            'error_message': error_message,
            'timestamp': datetime.now().isoformat(),
            'suggested_action': ErrorHandler._get_suggested_action(error_type),
            'fallback_available': ErrorHandler._has_fallback(error_type)
        }
        
        if context:
            error_response.update(context)
            
        return error_response
    
    @staticmethod
    def _get_suggested_action(error_type: str) -> str:
        """Get suggested action based on error type."""
        suggestions = {
            'API_ERROR': 'Try again in a few minutes or check API status',
            'TIMEOUT': 'Request may be processing, try again with shorter timeout',
            'DATA_NOT_FOUND': 'Verify company name/ticker and try alternative sources',
            'RATE_LIMIT': 'Wait 30-60 seconds before retrying',
            'NETWORK_ERROR': 'Check internet connection and try again',
            'INVALID_INPUT': 'Verify input format and try again',
            'UNKNOWN_ERROR': 'Contact support if problem persists'
        }
        return suggestions.get(error_type, 'Try again or contact support')
    
    @staticmethod
    def _has_fallback(error_type: str) -> bool:
        """Determine if fallback data is available for this error type."""
        fallback_available = {
            'API_ERROR': True,
            'TIMEOUT': True,
            'DATA_NOT_FOUND': False,
            'RATE_LIMIT': True,
            'NETWORK_ERROR': True,
            'INVALID_INPUT': False,
            'UNKNOWN_ERROR': False
        }
        return fallback_available.get(error_type, False)
    
    @staticmethod
    def get_fallback_data(data_type: str, company_name: Optional[str] = None, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Provide fallback data when primary sources fail.
        
        Args:
            data_type: Type of data needed ('stock_data', 'news', 'ticker')
            company_name: Company name for context
            ticker: Ticker symbol for context
            
        Returns:
            Fallback data with appropriate structure
        """
        if data_type == 'stock_data' and ticker:
            return {
                'success': True,
                'ticker': ticker,
                'company_name': company_name or ticker,
                'current_price': 'N/A - Data unavailable',
                'previous_close': 'N/A - Data unavailable',
                'volume': 'N/A - Data unavailable',
                'market_cap': 'N/A - Data unavailable',
                'pe_ratio': 'N/A - Data unavailable',
                'dividend_yield': 'N/A - Data unavailable',
                'currency': 'USD',
                'data_source': 'fallback',
                'data_quality': 'limited'
            }
        elif data_type == 'news' and company_name:
            return {
                'success': True,
                'company_name': company_name,
                'articles': [{
                    'title': f'Limited news available for {company_name}',
                    'snippet': 'News data is currently unavailable. Please try again later or check alternative sources.',
                    'date': datetime.now().isoformat(),
                    'source': 'Fallback System',
                    'financial_relevance_score': 0,
                    'financial_keywords_found': []
                }],
                'count': 1,
                'total_financial_keywords': 0,
                'data_source': 'fallback',
                'data_quality': 'limited'
            }
        elif data_type == 'ticker' and company_name:
            return {
                'success': True,
                'ticker': None,
                'company_name': company_name,
                'search_results': f"Unable to find ticker symbol for {company_name}. Please verify the company name or try alternative sources.",
                'original_query': company_name,
                'source': 'Fallback System',
                'data_quality': 'limited'
            }
        else:
            return {
                'success': False,
                'error_type': 'FALLBACK_UNAVAILABLE',
                'error_message': f'No fallback data available for {data_type}',
                'timestamp': datetime.now().isoformat()
            }

def run_with_timeout(func, args, kwargs, timeout=60):
    """Run a function with a timeout using threading."""
    result: list = [None]
    exception: list = [None]
    
    def target():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            exception[0] = e
    
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    
    if thread.is_alive():
        return ErrorHandler.create_error_response(
            error_type='TIMEOUT',
            error_message=f"Tool execution timed out after {timeout} seconds",
            context={'timeout_seconds': timeout, 'function_name': func.__name__}
        )
    
    if exception[0]:
        return ErrorHandler.create_error_response(
            error_type='API_ERROR',
            error_message=f"Tool execution failed: {str(exception[0])}",
            context={'function_name': func.__name__, 'exception_type': type(exception[0]).__name__}
        )
    
    return result[0]



class FinancialTools:
    """Tools for financial data retrieval with robust error handling."""
    
    @staticmethod
    def _get_stock_data_impl(ticker: str) -> Dict[str, Any]:
        """
        Fetch stock price and key financial metrics for a given ticker.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'TSLA', 'MSFT')
            
        Returns:
            Dictionary containing stock data or error information
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.history(period="1d")
            
            if info.empty:
                return ErrorHandler.create_error_response(
                    error_type='DATA_NOT_FOUND',
                    error_message=f"Could not find data for ticker '{ticker}'",
                    context={'ticker': ticker, 'data_source': 'yfinance'}
                )

            # Get basic price data
            current_price = info['Close'].iloc[0]
            prev_close = info['Open'].iloc[0]
            volume = info['Volume'].iloc[0]
            
            # Get additional info from stock.info
            stock_info = stock.info
            market_cap = stock_info.get('marketCap', 'N/A')
            pe_ratio = stock_info.get('trailingPE', 'N/A')
            dividend_yield = stock_info.get('dividendYield', 'N/A')
            company_name = stock_info.get('longName', stock_info.get('shortName', ticker))

            return {
                'success': True,
                'ticker': ticker,
                'company_name': company_name,
                'current_price': current_price,
                'previous_close': prev_close,
                'volume': volume,
                'market_cap': market_cap,
                'pe_ratio': pe_ratio,
                'dividend_yield': dividend_yield,
                'currency': stock_info.get('currency', 'USD')
            }
            
        except Exception as e:
            return ErrorHandler.create_error_response(
                error_type='API_ERROR',
                error_message=f"Failed to fetch stock data for {ticker}: {str(e)}",
                context={'ticker': ticker, 'data_source': 'yfinance', 'exception_type': type(e).__name__}
            )
    
    # CrewAI Tool wrappers
    @staticmethod
    @tool
    @tracer.chain
    def get_stock_data(ticker: str) -> Dict[str, Any]:
        """Fetch stock price and key financial metrics for a given ticker."""
        print(f"🔧 Tool: get_stock_data")
        print(f"   Input: ticker = '{ticker}'")
        result = FinancialTools._get_stock_data_impl(ticker)
        print(f"   Output: {result}")
        return result
    
    @staticmethod
    @tool
    @tracer.chain
    def get_ticker_symbol(company_name: str) -> Dict[str, Any]:
        """Get stock ticker symbol from company name using a reliable API."""
        print(f"🔧 Tool: get_ticker_symbol")
        print(f"   Input: company_name = '{company_name}'")
        result = FinancialTools._get_ticker_symbol_impl(company_name)
        print(f"   Output: {result}")
        return result
    
    @staticmethod
    @tool
    @tracer.chain
    def get_recent_news(company_name: str, max_results: int = 5) -> Dict[str, Any]:
        """Search for recent news articles about a company."""
        print(f"🔧 Tool: get_recent_news")
        print(f"   Input: company_name = '{company_name}', max_results = {max_results}")
        result = FinancialTools._get_recent_news_impl(company_name, max_results)
        print(f"   Output: {result}")
        return result
    
    @staticmethod
    def _get_ticker_symbol_impl(company_name: str) -> Dict[str, Any]:
        """
        Get stock ticker symbol from company name using DuckDuckGo search.
        
        Args:
            company_name: Name of the company (e.g., 'Microsoft', 'Tesla')
            
        Returns:
            Dictionary containing ticker symbol or error information
        """
        try:
            # Add delay to avoid rate limiting
            time.sleep(1.5)
            
            with DDGS() as ddgs:
                results = list(ddgs.text(f"ticker symbol for {company_name}", max_results=3))
                
            if results:
                # Extract ticker from search results using regex
                import re
                ticker_pattern = r'\b[A-Z]{1,5}\b'  # 1-5 uppercase letters
                
                for result in results:
                    text = f"{result.get('title', '')} {result.get('body', '')}"
                    matches = re.findall(ticker_pattern, text)
                    
                    # Filter out common non-ticker words
                    common_words = {'THE', 'AND', 'FOR', 'WITH', 'FROM', 'THIS', 'THAT', 'HAVE', 'WILL', 'ARE', 'WAS', 'NOT', 'BUT', 'HAS', 'HAD', 'CAN', 'ALL', 'NEW', 'ONE', 'TWO', 'NOW', 'GET', 'SEE', 'SAY', 'DAY', 'WAY', 'MAY', 'OUT', 'WHO', 'HER', 'HIS', 'ITS', 'OUR', 'YOUR', 'THEY', 'SHE', 'HIM', 'THEM', 'WHAT', 'WHEN', 'WHERE', 'WHY', 'HOW', 'EACH', 'MOST', 'SOME', 'SUCH', 'ONLY', 'VERY', 'JUST', 'MORE', 'MOST', 'OVER', 'UNDER', 'ABOVE', 'BELOW', 'BETWEEN', 'AMONG', 'AGAINST', 'TOWARD', 'THROUGH', 'DURING', 'BEFORE', 'AFTER', 'SINCE', 'UNTIL', 'WHILE', 'ALTHOUGH', 'BECAUSE', 'UNLESS', 'UNTIL', 'WHETHER', 'WHILE', 'WHEREAS', 'WHEREVER', 'WHENEVER', 'WHOEVER', 'WHATEVER', 'WHICHEVER', 'HOWEVER', 'THEREFORE', 'THUS', 'HENCE', 'SO', 'AND', 'OR', 'BUT', 'NOR', 'YET', 'SO', 'BOTH', 'EITHER', 'NEITHER', 'NOT', 'ONLY', 'JUST', 'VERY', 'QUITE', 'RATHER', 'FAIRLY', 'PRETTY', 'REALLY', 'EXTREMELY', 'HIGHLY', 'COMPLETELY', 'TOTALLY', 'ENTIRELY', 'FULLY', 'PARTIALLY', 'MOSTLY', 'MAINLY', 'PRIMARILY', 'SECONDARILY', 'FINALLY', 'EVENTUALLY', 'ULTIMATELY', 'GRADUALLY', 'SLOWLY', 'QUICKLY', 'RAPIDLY', 'IMMEDIATELY', 'INSTANTLY', 'SOON', 'LATER', 'EARLIER', 'PREVIOUSLY', 'RECENTLY', 'CURRENTLY', 'PRESENTLY', 'NOW', 'THEN', 'HERE', 'THERE', 'WHERE', 'WHEN', 'WHY', 'HOW', 'WHAT', 'WHO', 'WHICH', 'WHOSE', 'WHOM', 'WHERE', 'WHEN', 'WHY', 'HOW', 'WHAT', 'WHO', 'WHICH', 'WHOSE', 'WHOM'}
                    
                    for match in matches:
                        if match not in common_words and len(match) >= 2:
                            return {
                                'success': True,
                                'ticker': match,
                                'company_name': company_name,
                                'original_query': company_name,
                                'source': 'DuckDuckGo search'
                            }
                
                # If no ticker found in results, return the search results for manual extraction
                return {
                    'success': True,
                    'ticker': None,
                    'company_name': company_name,
                    'search_results': "\n".join([f"{res.get('title', '')} - {res.get('body', '')}" for res in results]),
                    'original_query': company_name,
                    'source': 'DuckDuckGo search (manual extraction needed)'
                }
            else:
                return ErrorHandler.create_error_response(
                    error_type='DATA_NOT_FOUND',
                    error_message=f"No ticker found for company: {company_name}",
                    context={'company_name': company_name, 'search_source': 'DuckDuckGo'}
                )
                
        except Exception as e:
            return ErrorHandler.create_error_response(
                error_type='API_ERROR',
                error_message=f"Failed to lookup ticker for {company_name}: {str(e)}",
                context={'company_name': company_name, 'search_source': 'DuckDuckGo', 'exception_type': type(e).__name__}
            )
    
    @staticmethod
    def _get_recent_news_impl(company_name: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Search for recent news articles about a company with focus on financial relevance.
        
        Args:
            company_name: Name of the company to search for
            max_results: Maximum number of news articles to return
            
        Returns:
            Dictionary containing news articles or error information
        """
        try:
            # Add delay to avoid rate limiting
            time.sleep(1.5)
            
            # Enhanced financial-focused queries
            financial_queries = [
                f"{company_name} earnings revenue profit financial results",
                f"{company_name} stock price analyst rating buy sell hold",
                f"{company_name} market cap valuation P/E ratio dividend",
                f"{company_name} quarterly results financial performance",
                f"{company_name} stock news trading volume market analysis"
            ]
            
            all_results = []
            
            with DDGS() as ddgs:
                # Try multiple financial-focused queries to get better results
                for query in financial_queries[:2]:  # Use first 2 queries to avoid rate limiting
                    try:
                        results = list(ddgs.news(query, max_results=max_results//2 + 1))
                        all_results.extend(results)
                        time.sleep(1)  # Small delay between queries
                    except Exception as e:
                        print(f"Warning: Query '{query}' failed: {str(e)}")
                        continue
            
            if all_results:
                # Remove duplicates based on title
                seen_titles = set()
                unique_results = []
                for result in all_results:
                    title = result.get('title', '').lower().strip()
                    if title and title not in seen_titles:
                        seen_titles.add(title)
                        unique_results.append(result)
                
                # Sort by date (most recent first) and take top results
                unique_results.sort(key=lambda x: x.get('date', ''), reverse=True)
                top_results = unique_results[:max_results]
                
                # Extract relevant information from each article with financial context
                articles = []
                for result in top_results:
                    # Calculate financial relevance score
                    financial_keywords = [
                        'earnings', 'revenue', 'profit', 'loss', 'growth', 'stock', 'price', 'market',
                        'financial', 'quarterly', 'annual', 'dividend', 'buy', 'sell', 'hold', 'rating',
                        'analyst', 'target', 'valuation', 'P/E', 'market cap', 'trading', 'volume',
                        'investment', 'portfolio', 'fund', 'ETF', 'index', 'sector', 'industry'
                    ]
                    
                    text = f"{result.get('title', '')} {result.get('body', '')}".lower()
                    relevance_score = sum(1 for keyword in financial_keywords if keyword in text)
                    
                    article = {
                        'title': result.get('title', ''),
                        'link': result.get('link', ''),
                        'snippet': result.get('body', ''),
                        'date': result.get('date', ''),
                        'source': result.get('source', ''),
                        'financial_relevance_score': relevance_score,
                        'financial_keywords_found': [kw for kw in financial_keywords if kw in text]
                    }
                    articles.append(article)
                
                # Sort by financial relevance score (highest first)
                articles.sort(key=lambda x: x['financial_relevance_score'], reverse=True)
                
                return {
                    'success': True,
                    'company_name': company_name,
                    'articles': articles,
                    'count': len(articles),
                    'total_financial_keywords': sum(article['financial_relevance_score'] for article in articles)
                }
            else:
                return ErrorHandler.create_error_response(
                    error_type='DATA_NOT_FOUND',
                    error_message=f"No recent news found for '{company_name}'",
                    context={'company_name': company_name, 'search_source': 'DuckDuckGo News'}
                )
                
        except Exception as e:
            return ErrorHandler.create_error_response(
                error_type='API_ERROR',
                error_message=f"Failed to fetch news for {company_name}: {str(e)}",
                context={'company_name': company_name, 'search_source': 'DuckDuckGo News', 'exception_type': type(e).__name__}
            ) 