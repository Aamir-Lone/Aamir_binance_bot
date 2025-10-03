# Binance Futures Trading Bot

A comprehensive CLI-based trading bot for Binance USDT-M Futures with support for multiple order types, advanced trading strategies, and robust logging system.

---

## Features

### Core Order Types (50% of Requirements)
- Market Orders - Execute trades immediately at current market price
- Limit Orders - Place orders at specific price levels with cancel/list functionality

### Advanced Order Types (30% Bonus Features)
- Stop-Limit Orders - Conditional orders triggered when stop price is hit
- OCO Orders - One-Cancels-the-Other strategy (take-profit + stop-loss)
- TWAP Strategy - Time-Weighted Average Price for splitting large orders
- Grid Trading - Automated range trading with multiple buy/sell levels

### System Features
- Comprehensive Logging - All API calls, errors, and executions logged to `bot.log`
- Input Validation - Validates symbols, quantities, and prices before execution
- Retry Logic - Automatic retry with exponential backoff for failed requests
- Position Management - Support for LONG, SHORT, and BOTH position sides
- Environment Configuration - Secure API key management via `.env` file
- Testnet Support - Safe testing with fake money before live trading
- Interactive Menu - User-friendly CLI interface with `bot.py`
- Command Line Interface - Direct execution via individual scripts

---

## Requirements

- Python: 3.8 or higher
- Operating System: Linux, macOS, or Windows
- Binance Account: Futures Testnet account (for safe testing)
- Internet Connection: Required for API communication

---

## Installation

### Step 1: Navigate to Project Directory
```bash
cd Aamir_binance_bot
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv .venv
```

### Step 3: Activate Virtual Environment

On macOS/Linux:
```bash
source .venv/bin/activate
```

On Windows:
```bash
.venv\Scripts\activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

You should see:
```
Successfully installed requests-2.31.0 python-dotenv-1.0.0
```

---

## Getting API Keys

### Important: Use Testnet for Safe Testing!

ALWAYS START WITH TESTNET - it uses fake money and is completely safe for learning and testing.

### Step-by-Step Guide to Get Testnet API Keys:

#### 1. Visit Binance Futures Testnet
Go to: https://testnet.binancefuture.com/

#### 2. Login with Your Account
- Click on "Login" or "Sign In"
- You'll be redirected to authenticate
- Use GitHub or Google to login
- No separate registration needed - it uses your existing accounts

#### 3. Generate API Keys
Once logged in:
- Look for "API Key" section in the dashboard
- Click "Generate HMAC_SHA256 Key"
- You'll see two values:
  - API Key (64 characters, starts with letters/numbers)
  - Secret Key (64 characters, starts with letters/numbers)

#### 4. Copy Your Keys
- Copy the API Key - all 64 characters
- Copy the Secret Key - all 64 characters
- WARNING: Store them safely - you'll need these in the next step

#### 5. Get Free Test USDT
- On the same testnet page, find the "Get Test USDT" button
- Click it to receive 10,000 USDT (fake money for testing)
- You can click it multiple times if you need more

### Example of What Keys Look Like:
```
API Key:     HROcqoc7YusEyberqbke4GAL4fhsgeyNPGxyauf0Gb6oroYxpL2lhOncPCTcy3VQ
Secret Key:  1RO0L7zZ40wnyQ29tOg0I7QEgas4gAc8cc4W9hjXba38iMb27NAaKObPkRDgoexO9
```
(These are examples - use your own keys!)

---

## Configuration

### Step 1: Create .env File

### Step 2: Edit .env File

Open `.env`file and add your API keys:

```bash
# Binance API Credentials
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_secret_key_here

# Trading Mode
USE_TESTNET=True
```

Replace:
- `your_api_key_here` with your actual API Key (64 characters)
- `your_secret_key_here` with your actual Secret Key (64 characters)

### Step 3: Verify Configuration

Run the validation script:
```bash
python validate.py
```

Expected output:
```
PASS - Python Version
PASS - Dependencies
PASS - File Structure
PASS - Configuration
PASS - Logging
PASS - API Connection

Results: 6/6 checks passed
```

If you see errors, check:
- API keys are correct (no extra spaces)
- `.env` file is in the project root directory
- Virtual environment is activated

---

## Verification

### Using validate.py - Setup Health Check

After configuration, verify everything is set up correctly:

```bash
python validate.py
```

**What validate.py checks:**

1. **Python Version** - Ensures you have Python 3.8 or higher
2. **Dependencies** - Verifies all required packages are installed (requests, python-dotenv)
3. **File Structure** - Confirms all bot files exist and are in correct locations
4. **Configuration** - Checks if `.env` file exists and API keys are configured
5. **Logging** - Validates logging system is functional
6. **API Connection** - Tests actual connection to Binance and verifies your API keys work

**Expected output when everything is correct:**

```
==============================================================
BINANCE FUTURES BOT - VALIDATION SCRIPT
==============================================================

Python Version Check...
   ✓ Python 3.13.2 (OK)

Dependencies Check...
   ✓ requests - HTTP client for API calls
   ✓ dotenv - Environment variable management

File Structure Check...
   ✓ src/config.py - Configuration module
   ✓ src/constants.py - Constants and enums
   ✓ src/utils.py - Utility functions
   ✓ src/market_orders.py - Market orders
   ✓ src/limit_orders.py - Limit orders
   ✓ src/advanced/stop_limit.py - Stop-limit orders
   ✓ src/advanced/oco.py - OCO orders
   ✓ src/advanced/twap.py - TWAP strategy
   ✓ src/advanced/grid_orders.py - Grid trading
   ✓ bot.py - Interactive CLI
   ✓ requirements.txt - Dependencies
   ✓ README.md - Documentation

Configuration Check...
   ✓ .env file exists
   ✓ API_KEY configured (length: 64)
   ✓ API_SECRET configured (length: 64)
   Testnet Mode: TESTNET (Safe for testing)

Logging Check...
   ✓ Logging configured - bot.log exists

API Connection Check...
   Testing connection to Binance...
   ✓ Connection OK - BTC Price: $62,450.00
   Connected to TESTNET

==============================================================
VALIDATION SUMMARY
==============================================================
✓ PASS - Python Version
✓ PASS - Dependencies
✓ PASS - File Structure
✓ PASS - Configuration
✓ PASS - Logging
✓ PASS - API Connection
==============================================================
Results: 6/6 checks passed

All checks passed! You're ready to use the bot.

Next steps:
   1. Review README.md for usage instructions
   2. Try: python bot.py (interactive mode)
   3. Or use CLI: python src/market_orders.py BTCUSDT BUY 0.001
```

**If validation fails:**

The script will show specific errors and provide troubleshooting tips:
- Missing dependencies: Run `pip install -r requirements.txt`
- API credentials not set: Check your `.env` file
- Connection failed: Verify API keys and internet connection

**When to run validate.py:**
- After initial setup
- When switching between testnet and live mode
- After making configuration changes
- When troubleshooting issues
- Before starting a trading session

---

## Usage

### Option 1: Interactive Menu (Recommended)

Run the interactive bot:
```bash
python bot.py
```

You'll see a menu:
```
    ┌──────────────────────────────────────────────────────────┐
    │  MAIN MENU                                               │
    ├──────────────────────────────────────────────────────────┤
    │  CORE ORDERS                                             │
    │    1. Market Order (Buy/Sell at current price)           │
    │    2. Limit Order (Buy/Sell at specific price)           │
    │                                                          │
    │  ADVANCED ORDERS                                         │
    │    3. Stop-Limit Order (Conditional limit order)         │
    │    4. OCO Order (One-Cancels-the-Other)                  │
    │    5. TWAP Strategy (Time-weighted average)              │
    │    6. Grid Trading (Range trading strategy)              │
    │                                                          │
    │  UTILITIES                                               │
    │    7. Check Account Balance                              │
    │    8. Get Symbol Price                                   │
    │    9. View Open Orders                                   │
    │                                                          │
    │    0. Exit                                               │
    └──────────────────────────────────────────────────────────┘
```

Usage:
- Enter a number (0-9) to select an option
- Follow the prompts to enter trading parameters
- All actions are logged to `bot.log`

### Option 2: Command Line Interface

Execute orders directly from the command line using individual scripts:

---

## Order Types

### Market Orders

Execute orders at current market price:

```bash
# Buy 0.001 BTC at market price
python src/market_orders.py BTCUSDT BUY 0.001

# Sell 0.5 ETH at market price
python src/market_orders.py ETHUSDT SELL 0.5

# Buy with reduce-only flag (close position)
python src/market_orders.py BTCUSDT BUY 0.001 --reduce-only

# Specify position side
python src/market_orders.py BTCUSDT BUY 0.001 --position-side LONG
```

### Limit Orders

Place orders at specific price levels:

```bash
# Buy 0.001 BTC at $50,000
python src/limit_orders.py BTCUSDT BUY 0.001 50000

# Sell 0.5 ETH at $3,000
python src/limit_orders.py ETHUSDT SELL 0.5 3000

# Post-only mode (maker order only)
python src/limit_orders.py BTCUSDT BUY 0.001 50000 --post-only

# Different time-in-force options
python src/limit_orders.py BTCUSDT BUY 0.001 50000 --time-in-force IOC

# List all open orders
python src/limit_orders.py BTCUSDT --list

# Cancel a specific order
python src/limit_orders.py BTCUSDT --cancel ORDER_ID
```

### Stop-Limit Orders

Conditional orders triggered at stop price:

```bash
# Stop-limit BUY: If price rises to $51,000, buy at $51,100
python src/advanced/stop_limit.py BTCUSDT BUY 0.001 51000 51100

# Stop-limit SELL: If price falls to $49,000, sell at $48,900
python src/advanced/stop_limit.py BTCUSDT SELL 0.001 49000 48900

# Stop-loss for long position (reduce only)
python src/advanced/stop_limit.py BTCUSDT SELL 0.001 48000 47900 --reduce-only

# Use mark price instead of contract price
python src/advanced/stop_limit.py BTCUSDT SELL 0.001 49000 48900 --working-type MARK_PRICE
```

### OCO Orders (One-Cancels-the-Other)

Place simultaneous take-profit and stop-loss orders:

```bash
# Close long position with TP at $52,000 and SL at $48,000
python src/advanced/oco.py BTCUSDT SELL 0.001 52000 48000

# Close short position with TP at $48,000 and SL at $52,000
python src/advanced/oco.py BTCUSDT BUY 0.001 48000 52000

# OCO with stop-limit instead of stop-market
python src/advanced/oco.py BTCUSDT SELL 0.001 52000 48000 --stop-limit-price 47900

# Cancel OCO orders
python src/advanced/oco.py BTCUSDT --cancel-tp TP_ORDER_ID --cancel-sl SL_ORDER_ID
```

### TWAP (Time-Weighted Average Price)

Split large orders into smaller chunks executed over time:

```bash
# Buy 0.1 BTC split into 10 orders over 15 minutes (90s interval)
python src/advanced/twap.py BTCUSDT BUY 0.1 10 90

# Sell 1 ETH split into 5 orders over 5 minutes (60s interval)
python src/advanced/twap.py ETHUSDT SELL 1.0 5 60

# TWAP with randomization (vary order sizes and intervals)
python src/advanced/twap.py BTCUSDT BUY 0.1 10 90 --randomize

# TWAP with limit orders
python src/advanced/twap.py BTCUSDT BUY 0.1 10 90 --order-type LIMIT --limit-price 50000
```

### Grid Trading

Automated buy-low/sell-high strategy within a price range:

```bash
# Create a grid between $48,000 and $52,000 with 10 levels, 0.001 BTC per level
python src/advanced/grid_orders.py BTCUSDT 48000 52000 10 0.001

# Create a tighter grid with more levels
python src/advanced/grid_orders.py ETHUSDT 2900 3100 20 0.1

# Cancel all grid orders for a symbol
python src/advanced/grid_orders.py BTCUSDT --cancel
```

---

## Project Structure

```
Aamir_binance_bot/
│
├── src/                          # Source code
│   ├── config.py                 # Configuration and API creds.
│   ├── constants.py              # Constants and enumerations
│   ├── utils.py                  # Utility functions and logging
│   ├── market_orders.py          # Market order execution
│   ├── limit_orders.py           # Limit order execution
│   └── advanced/                 # Advanced trading strategies
│       ├── stop_limit.py         # Stop-limit orders
│       ├── oco.py                # OCO orders
│       ├── twap.py               # TWAP strategy
│       └── grid_orders.py        # Grid trading
│
├── bot.py                        # Interactive CLI menu
├── validate.py                   # Setup validation and health check
├── .env                          # API credentials 
├── bot.log                       # Application logs
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

### Key Files Explained:

**bot.py** - Main Interactive Interface
- User-friendly menu system for trading
- Navigate through options using numbers (0-9)
- Handles all order types with guided prompts
- Displays account balance and open orders
- Best for: Beginners or interactive trading sessions
- Run with: `python bot.py`

**validate.py** - Setup Verification Tool
- Checks Python version (requires 3.8+)
- Verifies all dependencies are installed
- Validates file structure is complete
- Confirms API keys are configured correctly
- Tests API connection to Binance
- Checks logging system functionality
- Run before first use: `python validate.py`
- Provides troubleshooting tips if issues found

**Individual Order Scripts** (in src/)
- Direct command-line execution for specific order types
- Faster for experienced users or automation
- Each script handles one order type
- Example: `python src/market_orders.py BTCUSDT BUY 0.001`

---

## Logging

All trading activities are logged to `bot.log` with timestamps and detailed information:

- API calls and responses
- Order placements and executions
- Errors and exceptions
- Price data and calculations
- Validation results

Example log format:
```
2025-10-03 10:30:45,123 - src.market_orders - INFO - Placing market order: BUY 0.001 BTCUSDT
2025-10-03 10:30:45,234 - src.utils - INFO - Current market price: 50000.00
2025-10-03 10:30:45,567 - src.market_orders - INFO - Market order placed successfully: Order ID 12345678
```

---

## Safety Features

1. Input Validation - All parameters are validated before API calls
2. Testnet Support - Test strategies without risking real funds
3. Reduce-Only Orders - Prevent accidental position increases
4. Error Handling - Comprehensive error catching and logging
5. Retry Logic - Automatic retries for network errors
6. Position Side Management - Explicit position side specification

---



### Trading Parameters (config.py)

- `MAX_POSITION_SIZE`: Maximum position size in USD
- `MIN_ORDER_SIZE`: Minimum order size in USD
- `MAX_LEVERAGE`: Maximum allowed leverage
- `MAX_RETRIES`: Number of retry attempts
- `RETRY_DELAY`: Delay between retries

---

## Testing

### Using Testnet

1. Set `USE_TESTNET=True` in `.env`
2. Use testnet API credentials
3. Test all order types and strategies
4. Verify logs and order execution

### Example Test Workflow

```bash
# 1. Test market order
python src/market_orders.py BTCUSDT BUY 0.001

# 2. Test limit order
python src/limit_orders.py BTCUSDT BUY 0.001 45000

# 3. Test OCO order
python src/advanced/oco.py BTCUSDT SELL 0.001 52000 48000

# 4. Check logs
tail -f bot.log
```

---

## Order Type Comparison

| Order Type | Use Case | Execution |
|------------|----------|-----------|
| Market | Immediate execution | Instant at current price |
| Limit | Specific price entry | When price reaches limit |
| Stop-Limit | Stop loss / breakout | Limit order after stop triggered |
| OCO | Risk management | Two orders, one cancels other |
| TWAP | Large orders / reduce impact | Split over time intervals |
| Grid | Range-bound markets | Multiple orders at price levels |

---

## Troubleshooting

### Common Issues

**1. "Import error: dotenv"**
```bash
pip install python-dotenv
```

**2. "API credentials not set"**
- Check your `.env` file exists
- Verify API key and secret are correct
- Ensure `.env` is in project root

**3. "Invalid symbol"**
- Use USDT pairs (e.g., BTCUSDT, ETHUSDT)
- Check symbol exists on Binance Futures

**4. "Insufficient balance"**
- Check account balance
- Reduce order size
- Fund testnet account if testing

**5. "Network error"**
- Check internet connection
- Verify API endpoint accessibility
- Check Binance status

---

## API Documentation

- Binance Futures API Docs: https://binance-docs.github.io/apidocs/futures/en/
- Testnet: https://testnet.binancefuture.com/

---

## Disclaimer

WARNING: 
- Trading cryptocurrencies involves significant risk.
- Always test on testnet first
- Start with small amounts
- Use proper risk management
- Never invest more than you can afford to lose
- Past performance does not guarantee future results

---

## Support

For issues or questions:
1. Check the logs in `bot.log`
2. Review the documentation above
3. Test on testnet first
4. Verify API credentials and permissions

---
---

## Learning Resources

- Binance Futures Trading Guide: https://www.binance.com/en/support/faq/futures
- Understanding TWAP: https://www.investopedia.com/terms/t/twap.asp
- Grid Trading Strategy: https://www.investopedia.com/terms/g/grid-trading.asp
- OCO Orders Explained: https://www.binance.com/en/support/faq/what-is-a-one-cancels-the-other-oco-order

---

Happy Trading!

# Name: Aamir Hussain lone
# email: aamirlone004@gmail.com
