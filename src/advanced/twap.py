"""
TWAP (Time-Weighted Average Price) Strategy Module
Splits large orders into smaller chunks executed over time
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
    validate_quantity,
    get_symbol_price
)
from src.constants import OrderSide, OrderType, PositionSide


class TWAPExecutor:
    """Execute TWAP (Time-Weighted Average Price) strategy"""
    
    def __init__(self):
        self.endpoint = '/fapi/v1/order'
    
    def execute_twap(
        self,
        symbol: str,
        side: str,
        total_quantity: float,
        num_orders: int,
        time_interval: int,
        order_type: str = OrderType.MARKET,
        limit_price: float = None,
        position_side: str = PositionSide.BOTH,
        randomize: bool = False
    ) -> Dict[str, Any]:
        """
        Execute TWAP strategy by splitting order into chunks
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            side: BUY or SELL
            total_quantity: Total quantity to trade
            num_orders: Number of orders to split into
            time_interval: Seconds between each order
            order_type: MARKET or LIMIT
            limit_price: Price for limit orders
            position_side: Position side (BOTH, LONG, SHORT)
            randomize: Add randomness to order sizes and intervals
            
        Returns:
            Dictionary with execution summary and all order responses
            
        Raises:
            Exception: If execution fails
        """
        # Validate inputs
        if not validate_symbol(symbol):
            raise ValueError(f"Invalid symbol: {symbol}")
        
        if not validate_quantity(total_quantity):
            raise ValueError(f"Invalid quantity: {total_quantity}")
        
        if num_orders <= 0:
            raise ValueError(f"Number of orders must be positive")
        
        if time_interval < 0:
            raise ValueError(f"Time interval must be non-negative")
        
        if side not in [OrderSide.BUY, OrderSide.SELL]:
            raise ValueError(f"Invalid side: {side}. Must be BUY or SELL")
        
        if order_type == OrderType.LIMIT and not limit_price:
            raise ValueError("Limit price required for LIMIT orders")
        
        # Calculate order sizes
        base_quantity = total_quantity / num_orders
        quantities = []
        
        if randomize:
            import random
            # Add randomness (±20%)
            for i in range(num_orders):
                random_factor = random.uniform(0.8, 1.2)
                quantities.append(base_quantity * random_factor)
            
            # Normalize to match total quantity
            total_random = sum(quantities)
            quantities = [q * (total_quantity / total_random) for q in quantities]
        else:
            quantities = [base_quantity] * num_orders
        
        # Round quantities to reasonable precision
        quantities = [round(q, 8) for q in quantities]
        
        # Adjust last order to account for rounding
        quantities[-1] = round(total_quantity - sum(quantities[:-1]), 8)
        
        logger.info(f"Starting TWAP execution: {side} {total_quantity} {symbol}")
        logger.info(f"Split into {num_orders} orders over {time_interval * (num_orders - 1)} seconds")
        logger.info(f"Order sizes: {quantities}")
        
        orders = []
        execution_prices = []
        start_time = datetime.now()
        
        try:
            for i, quantity in enumerate(quantities):
                order_num = i + 1
                logger.info(f"Executing order {order_num}/{num_orders}: {side} {quantity} {symbol}")
                
                # Prepare order parameters
                params = {
                    'symbol': symbol.upper(),
                    'side': side,
                    'type': order_type,
                    'quantity': quantity,
                    'positionSide': position_side,
                }
                
                if order_type == OrderType.LIMIT:
                    params['price'] = limit_price
                    params['timeInForce'] = 'GTC'
                
                # Get current price
                current_price = get_symbol_price(symbol)
                execution_prices.append(current_price)
                
                # Place order
                try:
                    response = make_request('POST', self.endpoint, params, signed=True)
                    
                    order_info = {
                        'order_number': order_num,
                        'order_id': response.get('orderId'),
                        'quantity': quantity,
                        'price': current_price,
                        'status': response.get('status'),
                        'timestamp': datetime.now().isoformat(),
                        'response': response
                    }
                    
                    orders.append(order_info)
                    logger.info(f"Order {order_num} placed successfully: Order ID {response.get('orderId')}")
                    
                    print(f"✅ Order {order_num}/{num_orders} executed: {quantity} @ {current_price}")
                    
                except Exception as e:
                    logger.error(f"Failed to place order {order_num}: {str(e)}")
                    order_info = {
                        'order_number': order_num,
                        'quantity': quantity,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    }
                    orders.append(order_info)
                    print(f"❌ Order {order_num}/{num_orders} failed: {str(e)}")
                
                # Wait before next order (except for last order)
                if i < num_orders - 1:
                    wait_time = time_interval
                    if randomize:
                        import random
                        wait_time = int(time_interval * random.uniform(0.8, 1.2))
                    
                    logger.info(f"Waiting {wait_time} seconds before next order...")
                    print(f"⏳ Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Calculate statistics
            successful_orders = [o for o in orders if 'order_id' in o]
            failed_orders = [o for o in orders if 'error' in o]
            total_executed = sum(o['quantity'] for o in successful_orders)
            
            avg_price = sum(execution_prices) / len(execution_prices) if execution_prices else 0
            
            result = {
                'symbol': symbol,
                'side': side,
                'total_quantity': total_quantity,
                'total_executed': total_executed,
                'num_orders': num_orders,
                'successful_orders': len(successful_orders),
                'failed_orders': len(failed_orders),
                'average_price': avg_price,
                'duration_seconds': duration,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'orders': orders
            }
            
            logger.info("TWAP execution completed")
            logger.info(f"Executed {total_executed}/{total_quantity} ({len(successful_orders)}/{num_orders} orders)")
            logger.info(f"Average price: {avg_price}")
            
            return result
            
        except KeyboardInterrupt:
            logger.warning("TWAP execution interrupted by user")
            print("\n⚠️  TWAP execution interrupted!")
            raise
        except Exception as e:
            logger.error(f"TWAP execution failed: {str(e)}")
            raise


def main():
    """Main CLI interface for TWAP execution"""
    parser = argparse.ArgumentParser(
        description='Execute TWAP (Time-Weighted Average Price) strategy on Binance Futures',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Buy 0.1 BTC split into 10 orders over 900 seconds (15 minutes)
  python src/advanced/twap.py BTCUSDT BUY 0.1 10 90
  
  # Sell 1 ETH split into 5 orders over 300 seconds (5 minutes)
  python src/advanced/twap.py ETHUSDT SELL 1.0 5 60
  
  # TWAP with randomization
  python src/advanced/twap.py BTCUSDT BUY 0.1 10 90 --randomize
  
  # TWAP with limit orders
  python src/advanced/twap.py BTCUSDT BUY 0.1 10 90 --order-type LIMIT --limit-price 50000
        """
    )
    
    parser.add_argument('symbol', type=str, help='Trading symbol (e.g., BTCUSDT)')
    parser.add_argument('side', type=str, choices=['BUY', 'SELL'], help='Order side')
    parser.add_argument('quantity', type=float, help='Total quantity to trade')
    parser.add_argument('num_orders', type=int, help='Number of orders to split into')
    parser.add_argument('interval', type=int, help='Seconds between each order')
    parser.add_argument('--order-type', type=str, default='MARKET',
                       choices=['MARKET', 'LIMIT'],
                       help='Order type (default: MARKET)')
    parser.add_argument('--limit-price', type=float,
                       help='Price for limit orders')
    parser.add_argument('--position-side', type=str, default='BOTH',
                       choices=['BOTH', 'LONG', 'SHORT'],
                       help='Position side (default: BOTH)')
    parser.add_argument('--randomize', action='store_true',
                       help='Add randomness to order sizes and intervals')
    
    args = parser.parse_args()
    
    try:
        executor = TWAPExecutor()
        
        total_time = args.interval * (args.num_orders - 1)
        
        print(f"\n{'='*60}")
        print(f"TWAP EXECUTION - {args.side} {args.quantity} {args.symbol}")
        print(f"{'='*60}")
        print(f"Orders: {args.num_orders}")
        print(f"Interval: {args.interval} seconds")
        print(f"Total Duration: {total_time} seconds (~{total_time/60:.1f} minutes)")
        print(f"Order Type: {args.order_type}")
        if args.randomize:
            print(f"Mode: Randomized")
        print(f"{'='*60}\n")
        
        result = executor.execute_twap(
            symbol=args.symbol,
            side=args.side,
            total_quantity=args.quantity,
            num_orders=args.num_orders,
            time_interval=args.interval,
            order_type=args.order_type,
            limit_price=args.limit_price,
            position_side=args.position_side,
            randomize=args.randomize
        )
        
        print(f"\n{'='*60}")
        print(f"TWAP EXECUTION SUMMARY")
        print(f"{'='*60}")
        print(f"Total Executed: {result['total_executed']}/{result['total_quantity']}")
        print(f"Successful Orders: {result['successful_orders']}/{result['num_orders']}")
        print(f"Failed Orders: {result['failed_orders']}")
        print(f"Average Price: {result['average_price']:.2f}")
        print(f"Duration: {result['duration_seconds']:.1f} seconds")
        print(f"\nOrder Details:")
        for order in result['orders']:
            if 'order_id' in order:
                print(f"  #{order['order_number']}: ✅ ID={order['order_id']}, "
                      f"Qty={order['quantity']}, Price={order['price']:.2f}")
            else:
                print(f"  #{order['order_number']}: ❌ Error: {order.get('error', 'Unknown')}")
        print(f"{'='*60}\n")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Execution stopped by user\n")
        return 130
    except Exception as e:
        logger.error(f"Error executing TWAP: {str(e)}")
        print(f"\n❌ ERROR: {str(e)}\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
