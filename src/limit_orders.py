"""
Limit Orders Module for Binance Futures Trading Bot
Handles limit orders at specific price levels
"""
import sys
import argparse
from typing import Dict, Any, Optional
from src.utils import (
    logger,
    make_request,
    validate_symbol,
    validate_quantity,
    validate_price,
    format_order_response,
    get_symbol_price
)
from src.constants import OrderSide, OrderType, TimeInForce, PositionSide


class LimitOrderExecutor:
    """Execute limit orders on Binance Futures"""
    
    def __init__(self):
        self.endpoint = '/fapi/v1/order'
    
    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        time_in_force: str = TimeInForce.GTC,
        position_side: str = PositionSide.BOTH,
        reduce_only: bool = False,
        post_only: bool = False
    ) -> Dict[str, Any]:
        """
        Place a limit order
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            side: BUY or SELL
            quantity: Order quantity
            price: Limit price
            time_in_force: Time in force (GTC, IOC, FOK, GTX)
            position_side: Position side (BOTH, LONG, SHORT)
            reduce_only: Whether to reduce position only
            post_only: Whether to use post-only mode (GTX)
            
        Returns:
            Order response from API
            
        Raises:
            Exception: If order placement fails
        """
        # Validate inputs
        if not validate_symbol(symbol):
            raise ValueError(f"Invalid symbol: {symbol}")
        
        if not validate_quantity(quantity):
            raise ValueError(f"Invalid quantity: {quantity}")
        
        if not validate_price(price):
            raise ValueError(f"Invalid price: {price}")
        
        if side not in [OrderSide.BUY, OrderSide.SELL]:
            raise ValueError(f"Invalid side: {side}. Must be BUY or SELL")
        
        # Use GTX for post-only mode
        if post_only:
            time_in_force = TimeInForce.GTX
        
        # Prepare order parameters
        params = {
            'symbol': symbol.upper(),
            'side': side,
            'type': OrderType.LIMIT,
            'quantity': quantity,
            'price': price,
            'timeInForce': time_in_force,
            'positionSide': position_side,
        }
        
        if reduce_only:
            params['reduceOnly'] = 'true'
        
        logger.info(f"Placing limit order: {side} {quantity} {symbol} @ {price}")
        
        try:
            # Get current price for comparison
            current_price = get_symbol_price(symbol)
            price_diff = ((price - current_price) / current_price) * 100
            
            logger.info(f"Current market price: {current_price}")
            logger.info(f"Limit price: {price} ({price_diff:+.2f}% from market)")
            
            # Place order
            response = make_request('POST', self.endpoint, params, signed=True)
            
            logger.info(f"Limit order placed successfully: Order ID {response.get('orderId')}")
            logger.info(f"Order details: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to place limit order: {str(e)}")
            raise
    
    def buy(self, symbol: str, quantity: float, price: float, **kwargs) -> Dict[str, Any]:
        """
        Place a limit BUY order
        
        Args:
            symbol: Trading pair
            quantity: Order quantity
            price: Limit price
            **kwargs: Additional parameters
            
        Returns:
            Order response
        """
        return self.place_order(symbol, OrderSide.BUY, quantity, price, **kwargs)
    
    def sell(self, symbol: str, quantity: float, price: float, **kwargs) -> Dict[str, Any]:
        """
        Place a limit SELL order
        
        Args:
            symbol: Trading pair
            quantity: Order quantity
            price: Limit price
            **kwargs: Additional parameters
            
        Returns:
            Order response
        """
        return self.place_order(symbol, OrderSide.SELL, quantity, price, **kwargs)
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Cancel an existing order
        
        Args:
            symbol: Trading pair
            order_id: Order ID to cancel
            
        Returns:
            Cancellation response
        """
        params = {
            'symbol': symbol.upper(),
            'orderId': order_id
        }
        
        logger.info(f"Cancelling order {order_id} for {symbol}")
        
        try:
            response = make_request('DELETE', self.endpoint, params, signed=True)
            logger.info(f"Order cancelled successfully: {response}")
            return response
        except Exception as e:
            logger.error(f"Failed to cancel order: {str(e)}")
            raise
    
    def get_open_orders(self, symbol: Optional[str] = None) -> list:
        """
        Get all open orders
        
        Args:
            symbol: Trading pair (optional, if None returns all)
            
        Returns:
            List of open orders
        """
        params = {}
        if symbol:
            params['symbol'] = symbol.upper()
        
        logger.info(f"Fetching open orders for {symbol if symbol else 'all symbols'}")
        
        try:
            response = make_request('GET', '/fapi/v1/openOrders', params, signed=True)
            logger.info(f"Found {len(response)} open orders")
            return response
        except Exception as e:
            logger.error(f"Failed to get open orders: {str(e)}")
            raise


def main():
    """Main CLI interface for limit orders"""
    parser = argparse.ArgumentParser(
        description='Execute limit orders on Binance Futures',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Buy 0.001 BTC at $50,000
  python src/limit_orders.py BTCUSDT BUY 0.001 50000
  
  # Sell 0.5 ETH at $3,000
  python src/limit_orders.py ETHUSDT SELL 0.5 3000
  
  # Buy with post-only mode (maker order)
  python src/limit_orders.py BTCUSDT BUY 0.001 50000 --post-only
  
  # Cancel an order
  python src/limit_orders.py BTCUSDT --cancel ORDER_ID
  
  # View open orders
  python src/limit_orders.py BTCUSDT --list
        """
    )
    
    parser.add_argument('symbol', type=str, help='Trading symbol (e.g., BTCUSDT)')
    parser.add_argument('side', type=str, nargs='?', choices=['BUY', 'SELL'],
                       help='Order side')
    parser.add_argument('quantity', type=float, nargs='?', help='Order quantity')
    parser.add_argument('price', type=float, nargs='?', help='Limit price')
    parser.add_argument('--time-in-force', type=str, default='GTC',
                       choices=['GTC', 'IOC', 'FOK', 'GTX'],
                       help='Time in force (default: GTC)')
    parser.add_argument('--position-side', type=str, default='BOTH',
                       choices=['BOTH', 'LONG', 'SHORT'],
                       help='Position side (default: BOTH)')
    parser.add_argument('--reduce-only', action='store_true',
                       help='Reduce position only')
    parser.add_argument('--post-only', action='store_true',
                       help='Post-only mode (maker order)')
    parser.add_argument('--cancel', type=int, metavar='ORDER_ID',
                       help='Cancel order by ID')
    parser.add_argument('--list', action='store_true',
                       help='List all open orders')
    
    args = parser.parse_args()
    
    try:
        executor = LimitOrderExecutor()
        
        # Cancel order
        if args.cancel:
            print(f"\n{'='*50}")
            print(f"CANCELLING ORDER {args.cancel} for {args.symbol}")
            print(f"{'='*50}\n")
            
            response = executor.cancel_order(args.symbol, args.cancel)
            print(f"✅ Order cancelled successfully")
            print(f"Order ID: {response.get('orderId')}")
            print(f"Status: {response.get('status')}\n")
            return 0
        
        # List open orders
        if args.list:
            print(f"\n{'='*50}")
            print(f"OPEN ORDERS for {args.symbol}")
            print(f"{'='*50}\n")
            
            orders = executor.get_open_orders(args.symbol)
            
            if not orders:
                print("No open orders found.\n")
            else:
                for order in orders:
                    print(f"Order ID: {order['orderId']}")
                    print(f"  Symbol: {order['symbol']}")
                    print(f"  Side: {order['side']}")
                    print(f"  Type: {order['type']}")
                    print(f"  Price: {order.get('price', 'N/A')}")
                    print(f"  Quantity: {order['origQty']}")
                    print(f"  Filled: {order['executedQty']}")
                    print(f"  Status: {order['status']}")
                    print(f"  Time: {order['time']}\n")
            return 0
        
        # Place limit order
        if not all([args.side, args.quantity, args.price]):
            parser.error("side, quantity, and price are required for placing orders")
        
        print(f"\n{'='*50}")
        print(f"LIMIT ORDER - {args.side} {args.quantity} {args.symbol} @ {args.price}")
        print(f"{'='*50}\n")
        
        response = executor.place_order(
            symbol=args.symbol,
            side=args.side,
            quantity=args.quantity,
            price=args.price,
            time_in_force=args.time_in_force,
            position_side=args.position_side,
            reduce_only=args.reduce_only,
            post_only=args.post_only
        )
        
        print(format_order_response(response))
        print(f"{'='*50}\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error executing limit order: {str(e)}")
        print(f"\n❌ ERROR: {str(e)}\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
