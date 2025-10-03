"""
Grid Trading Strategy Module
Automated buy-low/sell-high strategy within a price range
"""
import sys
import argparse
import time
from typing import Dict, Any, List
from datetime import datetime
from src.utils import (
    logger,
    make_request,
    validate_symbol,
    validate_price,
    get_symbol_price
)
from src.constants import OrderSide, OrderType, TimeInForce, PositionSide


class GridTradingExecutor:
    """Execute Grid Trading strategy on Binance Futures"""
    
    def __init__(self):
        self.endpoint = '/fapi/v1/order'
        self.active_grids = []
    
    def create_grid(
        self,
        symbol: str,
        lower_price: float,
        upper_price: float,
        num_grids: int,
        quantity_per_grid: float,
        position_side: str = PositionSide.BOTH
    ) -> Dict[str, Any]:
        """
        Create a grid trading strategy
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            lower_price: Lower bound of price range
            upper_price: Upper bound of price range
            num_grids: Number of grid levels
            quantity_per_grid: Quantity for each grid order
            position_side: Position side (BOTH, LONG, SHORT)
            
        Returns:
            Dictionary with grid configuration and placed orders
            
        Raises:
            Exception: If grid creation fails
        """
        # Validate inputs
        if not validate_symbol(symbol):
            raise ValueError(f"Invalid symbol: {symbol}")
        
        if not validate_price(lower_price):
            raise ValueError(f"Invalid lower price: {lower_price}")
        
        if not validate_price(upper_price):
            raise ValueError(f"Invalid upper price: {upper_price}")
        
        if lower_price >= upper_price:
            raise ValueError(f"Lower price must be less than upper price")
        
        if num_grids < 2:
            raise ValueError(f"Number of grids must be at least 2")
        
        if quantity_per_grid <= 0:
            raise ValueError(f"Quantity per grid must be positive")
        
        # Get current price
        current_price = get_symbol_price(symbol)
        logger.info(f"Current market price: {current_price}")
        
        if current_price < lower_price or current_price > upper_price:
            logger.warning(f"Current price {current_price} is outside grid range [{lower_price}, {upper_price}]")
        
        # Calculate grid levels
        price_step = (upper_price - lower_price) / (num_grids - 1)
        grid_levels = [lower_price + (i * price_step) for i in range(num_grids)]
        
        logger.info(f"Creating grid with {num_grids} levels from {lower_price} to {upper_price}")
        logger.info(f"Grid levels: {grid_levels}")
        logger.info(f"Price step: {price_step}")
        
        buy_orders = []
        sell_orders = []
        
        try:
            # Place buy orders below current price
            for i, price in enumerate(grid_levels):
                if price < current_price:
                    logger.info(f"Placing BUY order at grid level {i+1}: {price}")
                    
                    try:
                        params = {
                            'symbol': symbol.upper(),
                            'side': OrderSide.BUY,
                            'type': OrderType.LIMIT,
                            'quantity': quantity_per_grid,
                            'price': round(price, 2),
                            'timeInForce': TimeInForce.GTC,
                            'positionSide': position_side,
                        }
                        
                        response = make_request('POST', self.endpoint, params, signed=True)
                        
                        buy_orders.append({
                            'grid_level': i + 1,
                            'price': price,
                            'order_id': response.get('orderId'),
                            'status': response.get('status'),
                            'side': 'BUY'
                        })
                        
                        logger.info(f"BUY order placed at {price}: Order ID {response.get('orderId')}")
                        print(f"✅ BUY order placed at {price:.2f}")
                        
                    except Exception as e:
                        logger.error(f"Failed to place BUY order at {price}: {str(e)}")
                        print(f"❌ Failed to place BUY order at {price:.2f}: {str(e)}")
            
            # Place sell orders above current price
            for i, price in enumerate(grid_levels):
                if price > current_price:
                    logger.info(f"Placing SELL order at grid level {i+1}: {price}")
                    
                    try:
                        params = {
                            'symbol': symbol.upper(),
                            'side': OrderSide.SELL,
                            'type': OrderType.LIMIT,
                            'quantity': quantity_per_grid,
                            'price': round(price, 2),
                            'timeInForce': TimeInForce.GTC,
                            'positionSide': position_side,
                        }
                        
                        response = make_request('POST', self.endpoint, params, signed=True)
                        
                        sell_orders.append({
                            'grid_level': i + 1,
                            'price': price,
                            'order_id': response.get('orderId'),
                            'status': response.get('status'),
                            'side': 'SELL'
                        })
                        
                        logger.info(f"SELL order placed at {price}: Order ID {response.get('orderId')}")
                        print(f"✅ SELL order placed at {price:.2f}")
                        
                    except Exception as e:
                        logger.error(f"Failed to place SELL order at {price}: {str(e)}")
                        print(f"❌ Failed to place SELL order at {price:.2f}: {str(e)}")
            
            result = {
                'symbol': symbol,
                'lower_price': lower_price,
                'upper_price': upper_price,
                'current_price': current_price,
                'num_grids': num_grids,
                'quantity_per_grid': quantity_per_grid,
                'price_step': price_step,
                'grid_levels': grid_levels,
                'buy_orders': buy_orders,
                'sell_orders': sell_orders,
                'total_orders': len(buy_orders) + len(sell_orders),
                'created_at': datetime.now().isoformat()
            }
            
            self.active_grids.append(result)
            logger.info(f"Grid created successfully: {len(buy_orders)} BUY orders, {len(sell_orders)} SELL orders")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create grid: {str(e)}")
            raise
    
    def cancel_grid(self, symbol: str) -> Dict[str, Any]:
        """
        Cancel all open orders for a symbol (grid teardown)
        
        Args:
            symbol: Trading pair
            
        Returns:
            Dictionary with cancellation results
        """
        logger.info(f"Cancelling all orders for {symbol}")
        
        try:
            # Get all open orders
            params = {'symbol': symbol.upper()}
            open_orders = make_request('GET', '/fapi/v1/openOrders', params, signed=True)
            
            if not open_orders:
                logger.info("No open orders to cancel")
                return {'cancelled': 0, 'orders': []}
            
            logger.info(f"Found {len(open_orders)} open orders to cancel")
            
            cancelled_orders = []
            
            for order in open_orders:
                try:
                    cancel_params = {
                        'symbol': symbol.upper(),
                        'orderId': order['orderId']
                    }
                    
                    response = make_request('DELETE', self.endpoint, cancel_params, signed=True)
                    
                    cancelled_orders.append({
                        'order_id': order['orderId'],
                        'side': order['side'],
                        'price': order.get('price'),
                        'status': 'cancelled'
                    })
                    
                    logger.info(f"Cancelled order {order['orderId']}")
                    print(f"✅ Cancelled {order['side']} order at {order.get('price')}")
                    
                except Exception as e:
                    logger.error(f"Failed to cancel order {order['orderId']}: {str(e)}")
                    print(f"❌ Failed to cancel order {order['orderId']}: {str(e)}")
            
            result = {
                'symbol': symbol,
                'cancelled': len(cancelled_orders),
                'orders': cancelled_orders,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Grid cancellation completed: {len(cancelled_orders)} orders cancelled")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to cancel grid: {str(e)}")
            raise


def main():
    """Main CLI interface for grid trading"""
    parser = argparse.ArgumentParser(
        description='Execute Grid Trading strategy on Binance Futures',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a grid between $48,000 and $52,000 with 10 levels
  python src/advanced/grid_orders.py BTCUSDT 48000 52000 10 0.001
  
  # Create a tighter grid with more levels
  python src/advanced/grid_orders.py ETHUSDT 2900 3100 20 0.1
  
  # Cancel all grid orders for a symbol
  python src/advanced/grid_orders.py BTCUSDT --cancel
  
Note: Grid trading places limit orders at different price levels.
      Buy orders are placed below current price, sell orders above.
      Profits come from price oscillations within the range.
        """
    )
    
    parser.add_argument('symbol', type=str, help='Trading symbol (e.g., BTCUSDT)')
    parser.add_argument('lower_price', type=float, nargs='?',
                       help='Lower bound of grid range')
    parser.add_argument('upper_price', type=float, nargs='?',
                       help='Upper bound of grid range')
    parser.add_argument('num_grids', type=int, nargs='?',
                       help='Number of grid levels')
    parser.add_argument('quantity', type=float, nargs='?',
                       help='Quantity per grid level')
    parser.add_argument('--position-side', type=str, default='BOTH',
                       choices=['BOTH', 'LONG', 'SHORT'],
                       help='Position side (default: BOTH)')
    parser.add_argument('--cancel', action='store_true',
                       help='Cancel all grid orders for symbol')
    
    args = parser.parse_args()
    
    try:
        executor = GridTradingExecutor()
        
        # Cancel grid
        if args.cancel:
            print(f"\n{'='*60}")
            print(f"CANCELLING GRID ORDERS for {args.symbol}")
            print(f"{'='*60}\n")
            
            result = executor.cancel_grid(args.symbol)
            
            print(f"\n{'='*60}")
            print(f"CANCELLATION SUMMARY")
            print(f"{'='*60}")
            print(f"Orders Cancelled: {result['cancelled']}")
            print(f"{'='*60}\n")
            
            return 0
        
        # Create grid
        if not all([args.lower_price, args.upper_price, args.num_grids, args.quantity]):
            parser.error("lower_price, upper_price, num_grids, and quantity are required for creating grid")
        
        print(f"\n{'='*60}")
        print(f"GRID TRADING STRATEGY - {args.symbol}")
        print(f"{'='*60}")
        print(f"Price Range: {args.lower_price} - {args.upper_price}")
        print(f"Grid Levels: {args.num_grids}")
        print(f"Quantity per Level: {args.quantity}")
        print(f"{'='*60}\n")
        
        result = executor.create_grid(
            symbol=args.symbol,
            lower_price=args.lower_price,
            upper_price=args.upper_price,
            num_grids=args.num_grids,
            quantity_per_grid=args.quantity,
            position_side=args.position_side
        )
        
        print(f"\n{'='*60}")
        print(f"GRID CREATED SUCCESSFULLY")
        print(f"{'='*60}")
        print(f"Current Price: {result['current_price']:.2f}")
        print(f"Price Range: {result['lower_price']} - {result['upper_price']}")
        print(f"Price Step: {result['price_step']:.2f}")
        print(f"Total Orders Placed: {result['total_orders']}")
        print(f"  - BUY Orders: {len(result['buy_orders'])}")
        print(f"  - SELL Orders: {len(result['sell_orders'])}")
        print(f"\nGrid Levels:")
        for level in result['grid_levels']:
            marker = " ← Current" if abs(level - result['current_price']) < result['price_step']/2 else ""
            print(f"  {level:.2f}{marker}")
        print(f"{'='*60}\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error executing grid trading: {str(e)}")
        print(f"\n❌ ERROR: {str(e)}\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
