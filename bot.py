#!/usr/bin/env python3
"""
Main entry point for Binance Futures Trading Bot
Provides interactive CLI menu for all trading functions
"""
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils import logger, get_symbol_price, get_account_balance
from src.market_orders import MarketOrderExecutor
from src.limit_orders import LimitOrderExecutor
from src.advanced.stop_limit import StopLimitOrderExecutor
from src.advanced.oco import OCOOrderExecutor
from src.advanced.twap import TWAPExecutor
from src.advanced.grid_orders import GridTradingExecutor


def print_banner():
    """Print welcome banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║     BINANCE FUTURES TRADING BOT                          ║
    ║     Advanced Order Execution System                      ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_menu():
    """Print main menu"""
    menu = """
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
    """
    print(menu)


def get_input(prompt, input_type=str, required=True):
    """Get and validate user input"""
    while True:
        try:
            value = input(prompt).strip()
            if not value and required:
                print("❌ This field is required!")
                continue
            if not value and not required:
                return None
            return input_type(value)
        except ValueError:
            print(f"❌ Invalid input! Expected {input_type.__name__}")


def market_order_menu():
    """Handle market order placement"""
    print("\n" + "="*60)
    print("MARKET ORDER")
    print("="*60)
    
    symbol = get_input("Symbol (e.g., BTCUSDT): ", str).upper()
    side = get_input("Side (BUY/SELL): ", str).upper()
    quantity = get_input("Quantity: ", float)
    
    if side not in ['BUY', 'SELL']:
        print("❌ Invalid side! Must be BUY or SELL")
        return
    
    try:
        executor = MarketOrderExecutor()
        response = executor.place_order(symbol, side, quantity)
        print(f"\n✅ Market order placed successfully!")
        print(f"Order ID: {response.get('orderId')}")
        print(f"Status: {response.get('status')}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def limit_order_menu():
    """Handle limit order placement"""
    print("\n" + "="*60)
    print("LIMIT ORDER")
    print("="*60)
    
    symbol = get_input("Symbol (e.g., BTCUSDT): ", str).upper()
    side = get_input("Side (BUY/SELL): ", str).upper()
    quantity = get_input("Quantity: ", float)
    price = get_input("Limit Price: ", float)
    
    if side not in ['BUY', 'SELL']:
        print("❌ Invalid side! Must be BUY or SELL")
        return
    
    try:
        executor = LimitOrderExecutor()
        response = executor.place_order(symbol, side, quantity, price)
        print(f"\n✅ Limit order placed successfully!")
        print(f"Order ID: {response.get('orderId')}")
        print(f"Status: {response.get('status')}")
        print(f"Price: {response.get('price')}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def stop_limit_menu():
    """Handle stop-limit order placement"""
    print("\n" + "="*60)
    print("STOP-LIMIT ORDER")
    print("="*60)
    
    symbol = get_input("Symbol (e.g., BTCUSDT): ", str).upper()
    side = get_input("Side (BUY/SELL): ", str).upper()
    quantity = get_input("Quantity: ", float)
    stop_price = get_input("Stop Trigger Price: ", float)
    limit_price = get_input("Limit Execution Price: ", float)
    
    if side not in ['BUY', 'SELL']:
        print("❌ Invalid side! Must be BUY or SELL")
        return
    
    try:
        executor = StopLimitOrderExecutor()
        response = executor.place_order(symbol, side, quantity, stop_price, limit_price)
        print(f"\n✅ Stop-limit order placed successfully!")
        print(f"Order ID: {response.get('orderId')}")
        print(f"Status: {response.get('status')}")
        print(f"Stop Price: {stop_price}")
        print(f"Limit Price: {limit_price}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def oco_menu():
    """Handle OCO order placement"""
    print("\n" + "="*60)
    print("OCO ORDER (One-Cancels-the-Other)")
    print("="*60)
    
    symbol = get_input("Symbol (e.g., BTCUSDT): ", str).upper()
    side = get_input("Side (BUY to close short, SELL to close long): ", str).upper()
    quantity = get_input("Quantity: ", float)
    take_profit = get_input("Take Profit Price: ", float)
    stop_loss = get_input("Stop Loss Price: ", float)
    
    if side not in ['BUY', 'SELL']:
        print("❌ Invalid side! Must be BUY or SELL")
        return
    
    try:
        executor = OCOOrderExecutor()
        response = executor.place_oco_order(symbol, side, quantity, take_profit, stop_loss)
        print(f"\n✅ OCO orders placed successfully!")
        print(f"Take Profit Order ID: {response['take_profit_order']['orderId']}")
        print(f"Stop Loss Order ID: {response['stop_loss_order']['orderId']}")
        print(f"Current Price: {response['current_price']}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def twap_menu():
    """Handle TWAP execution"""
    print("\n" + "="*60)
    print("TWAP STRATEGY (Time-Weighted Average Price)")
    print("="*60)
    
    symbol = get_input("Symbol (e.g., BTCUSDT): ", str).upper()
    side = get_input("Side (BUY/SELL): ", str).upper()
    total_quantity = get_input("Total Quantity: ", float)
    num_orders = get_input("Number of Orders: ", int)
    interval = get_input("Interval between orders (seconds): ", int)
    
    if side not in ['BUY', 'SELL']:
        print("❌ Invalid side! Must be BUY or SELL")
        return
    
    print(f"\n⏳ Executing TWAP: {num_orders} orders over {interval * (num_orders - 1)} seconds...")
    print("Press Ctrl+C to cancel\n")
    
    try:
        executor = TWAPExecutor()
        response = executor.execute_twap(symbol, side, total_quantity, num_orders, interval)
        print(f"\n✅ TWAP execution completed!")
        print(f"Total Executed: {response['total_executed']}/{response['total_quantity']}")
        print(f"Successful Orders: {response['successful_orders']}/{response['num_orders']}")
        print(f"Average Price: {response['average_price']:.2f}")
    except KeyboardInterrupt:
        print("\n⚠️  TWAP execution cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def grid_menu():
    """Handle grid trading setup"""
    print("\n" + "="*60)
    print("GRID TRADING STRATEGY")
    print("="*60)
    
    symbol = get_input("Symbol (e.g., BTCUSDT): ", str).upper()
    lower_price = get_input("Lower Price Bound: ", float)
    upper_price = get_input("Upper Price Bound: ", float)
    num_grids = get_input("Number of Grid Levels: ", int)
    quantity = get_input("Quantity per Grid: ", float)
    
    print(f"\n⏳ Creating grid with {num_grids} levels...")
    
    try:
        executor = GridTradingExecutor()
        response = executor.create_grid(symbol, lower_price, upper_price, num_grids, quantity)
        print(f"\n✅ Grid created successfully!")
        print(f"Current Price: {response['current_price']:.2f}")
        print(f"Price Range: {response['lower_price']} - {response['upper_price']}")
        print(f"Total Orders: {response['total_orders']}")
        print(f"  - BUY Orders: {len(response['buy_orders'])}")
        print(f"  - SELL Orders: {len(response['sell_orders'])}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def check_balance():
    """Check account balance"""
    print("\n" + "="*60)
    print("ACCOUNT BALANCE")
    print("="*60)
    
    try:
        balance = get_account_balance()
        
        # Separate assets with balance from those without
        assets_with_balance = []
        assets_zero_balance = []
        
        for asset in balance:
            balance_val = float(asset.get('balance', 0))
            available_val = float(asset.get('availableBalance', 0))
            
            if balance_val > 0 or available_val > 0:
                assets_with_balance.append(asset)
            else:
                assets_zero_balance.append(asset)
        
        # Show assets with balance first
        if assets_with_balance:
            print("\n💰 Assets with Balance:")
            print("-" * 60)
            for asset in assets_with_balance:
                print(f"\n{asset['asset']}:")
                print(f"  Balance:             {float(asset['balance']):,.8f}")
                print(f"  Available:           {float(asset['availableBalance']):,.8f}")
                print(f"  Cross Wallet:        {float(asset.get('crossWalletBalance', 0)):,.8f}")
                
                # Calculate USD value for common pairs
                usd_value = float(asset['balance'])
                if usd_value > 0 and asset['asset'] in ['USDT', 'BUSD', 'USDC', 'FDUSD']:
                    print(f"  ≈ ${usd_value:,.2f} USD")
        
        # Show summary table for all assets (including zeros)
        print("\n📊 Complete Balance Summary:")
        print("-" * 60)
        print(f"{'Asset':<10} {'Balance':>20} {'Available':>20}")
        print("-" * 60)
        
        # Show non-zero first
        for asset in assets_with_balance:
            bal = float(asset['balance'])
            avail = float(asset['availableBalance'])
            print(f"{asset['asset']:<10} {bal:>20,.8f} {avail:>20,.8f}")
        
        # Show important zero balances
        important_assets = ['USDT', 'BTC', 'ETH', 'BNB', 'BUSD']
        for asset in assets_zero_balance:
            if asset['asset'] in important_assets:
                bal = float(asset['balance'])
                avail = float(asset['availableBalance'])
                print(f"{asset['asset']:<10} {bal:>20,.8f} {avail:>20,.8f}")
        
        print("-" * 60)
        
        # Show helpful message if no balance
        if not assets_with_balance:
            print("\n⚠️  No funds in account (all balances are 0.00)")
        else:
            # Calculate total value in USDT
            total_usdt = sum(
                float(a['balance']) for a in assets_with_balance 
                if a['asset'] in ['USDT', 'BUSD', 'USDC', 'FDUSD']
            )
            if total_usdt > 0:
                print(f"\n💵 Total Value: ≈ ${total_usdt:,.2f} USD")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def check_price():
    """Check symbol price"""
    print("\n" + "="*60)
    print("SYMBOL PRICE")
    print("="*60)
    
    symbol = get_input("Symbol (e.g., BTCUSDT): ", str).upper()
    
    try:
        price = get_symbol_price(symbol)
        print(f"\n💰 Current price of {symbol}: {price}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def view_open_orders():
    """View open orders"""
    print("\n" + "="*60)
    print("OPEN ORDERS")
    print("="*60)
    
    symbol = get_input("Symbol (e.g., BTCUSDT, or press Enter for all): ", str, required=False)
    if symbol:
        symbol = symbol.upper()
    
    try:
        executor = LimitOrderExecutor()
        orders = executor.get_open_orders(symbol)
        
        if not orders:
            print("\n✅ No open orders found.")
        else:
            print(f"\n📊 Found {len(orders)} open order(s):\n")
            for order in orders:
                print(f"Order ID: {order['orderId']}")
                print(f"  Symbol: {order['symbol']}")
                print(f"  Side: {order['side']}")
                print(f"  Type: {order['type']}")
                print(f"  Price: {order.get('price', 'N/A')}")
                print(f"  Quantity: {order['origQty']}")
                print(f"  Filled: {order['executedQty']}")
                print(f"  Status: {order['status']}")
                print()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def main():
    """Main program loop"""
    print_banner()
    
    # Check configuration
    from src.config import API_KEY, TESTNET
    if not API_KEY:
        print("⚠️  WARNING: API credentials not configured!")
        print("Please set up your .env file with API keys.")
        print("See .env.example for template.\n")
    
    if TESTNET:
        print("🧪 TESTNET MODE - Using Binance Futures Testnet")
    else:
        print("⚠️  LIVE MODE - Using Real Binance Futures")
    
    print(f"\n📝 Logs are written to: bot.log\n")
    
    while True:
        print_menu()
        
        try:
            choice = get_input("\nSelect an option (0-9): ", str)
            
            if choice == '0':
                print("\n👋 Goodbye! Happy trading!\n")
                break
            elif choice == '1':
                market_order_menu()
            elif choice == '2':
                limit_order_menu()
            elif choice == '3':
                stop_limit_menu()
            elif choice == '4':
                oco_menu()
            elif choice == '5':
                twap_menu()
            elif choice == '6':
                grid_menu()
            elif choice == '7':
                check_balance()
            elif choice == '8':
                check_price()
            elif choice == '9':
                view_open_orders()
            else:
                print("\n❌ Invalid option! Please select 0-9")
            
            input("\nPress Enter to continue...")
            print("\n" * 2)  # Clear screen
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Happy trading!\n")
            break
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {str(e)}")
            print(f"\n❌ Unexpected error: {str(e)}")
            input("\nPress Enter to continue...")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        print(f"\n❌ Fatal error: {str(e)}\n")
        sys.exit(1)
