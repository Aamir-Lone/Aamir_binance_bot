"""
Configuration file for Binance Futures Trading Bot
Store your API credentials here or use environment variables
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Binance API Credentials
API_KEY = os.getenv('BINANCE_API_KEY', '')
API_SECRET = os.getenv('BINANCE_API_SECRET', '')

# Trading Configuration
TESTNET = os.getenv('USE_TESTNET', 'True').lower() == 'true'

# API Endpoints
if TESTNET:
    # Binance FUTURES testnet - API keys from testnet.binance.vision work here
    BASE_URL = 'https://testnet.binancefuture.com'
    WS_URL = 'wss://stream.binancefuture.com'
else:
    BASE_URL = 'https://fapi.binance.com'
    WS_URL = 'wss://fstream.binance.com'

# Logging Configuration
LOG_FILE = 'bot.log'
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Trading Limits (Safety Features)
MAX_POSITION_SIZE = 1000  # Maximum position size in USD
MIN_ORDER_SIZE = 10  # Minimum order size in USD
MAX_LEVERAGE = 10  # Maximum allowed leverage

# Retry Configuration
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Validation
if not TESTNET and (not API_KEY or not API_SECRET):
    print("WARNING: API credentials not set. Please configure them in .env file or environment variables.")
