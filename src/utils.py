"""
Utility functions for the trading bot
"""
import logging
import time
import hmac
import hashlib
from urllib.parse import urlencode
from typing import Dict, Any, Optional
import requests
from src.config import LOG_FILE, LOG_FORMAT, LOG_LEVEL, API_KEY, API_SECRET, BASE_URL, MAX_RETRIES, RETRY_DELAY
from src.constants import ERROR_MESSAGES

# Setup logging
def setup_logger(name: str = __name__) -> logging.Logger:
    """
    Set up and configure logger
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Avoid adding handlers multiple times
    if not logger.handlers:
        # File handler
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

# Initialize logger
logger = setup_logger()


def get_timestamp() -> int:
    """Get current timestamp in milliseconds"""
    return int(time.time() * 1000)


def create_signature(query_string: str) -> str:
    """
    Create HMAC SHA256 signature for Binance API
    
    Args:
        query_string: Query parameters as string
        
    Returns:
        HMAC signature
    """
    return hmac.new(
        API_SECRET.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def parse_api_error(error_response: Dict[str, Any]) -> str:
    """
    Parse Binance API error and return user-friendly message
    
    Args:
        error_response: Error response from API
        
    Returns:
        User-friendly error message
    """
    if isinstance(error_response, dict):
        error_code = error_response.get('code', 0)
        error_msg = error_response.get('msg', 'Unknown error')
        
        # Common Binance error codes with user-friendly messages
        error_map = {
            -1000: "Insufficient balance or invalid order parameters. Please check your account balance.",
            -1001: "Connection timeout. Please check your internet connection and try again.",
            -1002: "Unauthorized. Please check your API keys.",
            -1003: "Too many requests. Please wait a moment and try again.",
            -1013: "Invalid quantity. Please check the order quantity.",
            -1021: "Timestamp error. Your system time may be out of sync.",
            -1022: "Invalid signature. Please check your API credentials.",
            -2010: "Insufficient balance. You don't have enough funds for this order.",
            -2011: "Unknown order. The order does not exist.",
            -2013: "Order does not exist.",
            -2014: "API key format invalid.",
            -2015: "Invalid API key, IP, or permissions. Please regenerate your API keys.",
            -4000: "Invalid parameter.",
            -4001: "Price too high.",
            -4002: "Price too low.",
            -4003: "Quantity too high.",
            -4004: "Quantity too low.",
            -4131: "Market is closed.",
            -5021: "Due to risk control, your trading is restricted."
        }
        
        # Return user-friendly message if available
        if error_code in error_map:
            return f"{error_map[error_code]} (Error code: {error_code})"
        else:
            return f"{error_msg} (Error code: {error_code})"
    
    return str(error_response)


def make_request(
    method: str,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    signed: bool = False
) -> Dict[str, Any]:
    """
    Make HTTP request to Binance API with retry logic
    
    Args:
        method: HTTP method (GET, POST, DELETE)
        endpoint: API endpoint
        params: Request parameters
        signed: Whether request needs signature
        
    Returns:
        API response as dictionary
        
    Raises:
        Exception: If request fails after retries
    """
    url = f"{BASE_URL}{endpoint}"
    headers = {'X-MBX-APIKEY': API_KEY}
    
    if params is None:
        params = {}
    
    # Add timestamp and signature for signed requests
    if signed:
        params['timestamp'] = get_timestamp()
        query_string = urlencode(params)
        params['signature'] = create_signature(query_string)
    
    # Retry logic
    for attempt in range(MAX_RETRIES):
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, params=params, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, params=params, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Check response status
            if response.status_code == 200:
                logger.debug(f"API Request successful: {method} {endpoint}")
                return response.json()
            else:
                error_data = response.json() if response.text else {}
                logger.error(f"API Error [{response.status_code}]: {error_data}")
                
                # Parse error for user-friendly message
                friendly_error = parse_api_error(error_data)
                
                # Don't retry on client errors (4xx) - these are usually parameter issues
                if 400 <= response.status_code < 500:
                    raise Exception(friendly_error)
                
                # For 5xx errors (server errors), retry but also provide friendly message
                if attempt == MAX_RETRIES - 1:
                    raise Exception(friendly_error)
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request attempt {attempt + 1} failed: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                logger.error(f"All retry attempts failed for {method} {endpoint}")
                raise Exception(ERROR_MESSAGES['NETWORK_ERROR'])
    
    raise Exception("Request failed after all retries")


def validate_symbol(symbol: str) -> bool:
    """
    Validate trading symbol format
    
    Args:
        symbol: Trading pair symbol (e.g., BTCUSDT)
        
    Returns:
        True if valid, False otherwise
    """
    if not symbol or not isinstance(symbol, str):
        return False
    
    # Basic validation - should end with USDT for futures
    if not symbol.upper().endswith('USDT'):
        logger.warning(f"Symbol {symbol} may not be valid. Should end with USDT")
    
    return len(symbol) >= 6


def validate_quantity(quantity: float) -> bool:
    """
    Validate order quantity
    
    Args:
        quantity: Order quantity
        
    Returns:
        True if valid, False otherwise
    """
    try:
        qty = float(quantity)
        if qty <= 0:
            logger.error(ERROR_MESSAGES['INVALID_QUANTITY'])
            return False
        return True
    except (ValueError, TypeError):
        logger.error(ERROR_MESSAGES['INVALID_QUANTITY'])
        return False


def validate_price(price: float) -> bool:
    """
    Validate order price
    
    Args:
        price: Order price
        
    Returns:
        True if valid, False otherwise
    """
    try:
        p = float(price)
        if p <= 0:
            logger.error(ERROR_MESSAGES['INVALID_PRICE'])
            return False
        return True
    except (ValueError, TypeError):
        logger.error(ERROR_MESSAGES['INVALID_PRICE'])
        return False


def get_account_balance() -> Dict[str, Any]:
    """
    Get account balance information
    
    Returns:
        Account balance data
    """
    try:
        response = make_request('GET', '/fapi/v2/balance', signed=True)
        logger.info("Retrieved account balance")
        return response
    except Exception as e:
        logger.error(f"Failed to get account balance: {str(e)}")
        raise


def get_symbol_price(symbol: str) -> float:
    """
    Get current market price for symbol
    
    Args:
        symbol: Trading pair symbol
        
    Returns:
        Current price
    """
    try:
        response = make_request('GET', '/fapi/v1/ticker/price', {'symbol': symbol})
        price = float(response['price'])
        logger.debug(f"Current price for {symbol}: {price}")
        return price
    except Exception as e:
        logger.error(f"Failed to get price for {symbol}: {str(e)}")
        raise


def format_order_response(response: Dict[str, Any]) -> str:
    """
    Format order response for display
    
    Args:
        response: Order response from API
        
    Returns:
        Formatted string
    """
    return f"""
Order Placed Successfully:
------------------------
Order ID: {response.get('orderId')}
Symbol: {response.get('symbol')}
Side: {response.get('side')}
Type: {response.get('type')}
Quantity: {response.get('origQty')}
Price: {response.get('price', 'MARKET')}
Status: {response.get('status')}
Time: {response.get('updateTime')}
"""


def calculate_notional_value(quantity: float, price: float) -> float:
    """
    Calculate notional value of order
    
    Args:
        quantity: Order quantity
        price: Order price
        
    Returns:
        Notional value (quantity * price)
    """
    return quantity * price
