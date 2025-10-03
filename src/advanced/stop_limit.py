"""
Stop-Limit Orders Module
Conditional limit orders triggered when a stop price is hit
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
from src.constants import OrderSide, TimeInForce, PositionSide, WorkingType


class StopLimitOrderExecutor:
    """Execute stop-limit orders on Binance Futures"""
    
    def __init__(self):
        self.endpoint = '/fapi/v1/order'
    
    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: float,
        limit_price: float,
        position_side: str = PositionSide.BOTH,
        time_in_force: str = TimeInForce.GTC,
        working_type: str = WorkingType.CONTRACT_PRICE,
        reduce_only: bool = False
    ) -> Dict[str, Any]:
        """
        Place a stop-limit order
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            side: BUY or SELL
            quantity: Order quantity
            stop_price: Price that triggers the limit order
            limit_price: Limit price for the order execution
            position_side: Position side (BOTH, LONG, SHORT)
            time_in_force: Time in force (GTC, IOC, FOK, GTX)
            working_type: Price type for trigger (CONTRACT_PRICE or MARK_PRICE)
            reduce_only: Whether to reduce position only
            
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
        
        if not validate_price(stop_price):
            raise ValueError(f"Invalid stop price: {stop_price}")
        
        if not validate_price(limit_price):
            raise ValueError(f"Invalid limit price: {limit_price}")
        
        if side not in [OrderSide.BUY, OrderSide.SELL]:
            raise ValueError(f"Invalid side: {side}. Must be BUY or SELL")
        
        # Prepare order parameters
        params = {
            'symbol': symbol.upper(),
            'side': side,
            'type': 'STOP',  # STOP order type for stop-limit
            'quantity': quantity,
            'stopPrice': stop_price,
            'price': limit_price,
            'timeInForce': time_in_force,
            'positionSide': position_side,
            'workingType': working_type
        }
        
        if reduce_only:
            params['reduceOnly'] = 'true'
        
        logger.info(f"Placing stop-limit order: {side} {quantity} {symbol}")
        logger.info(f"Stop Price: {stop_price}, Limit Price: {limit_price}")
        
        try:
            # Get current price for reference
            current_price = get_symbol_price(symbol)
            logger.info(f"Current market price: {current_price}")
            
            # Validate stop price placement
            if side == OrderSide.BUY:
                if stop_price <= current_price:
                    logger.warning(f"Stop price {stop_price} is below current price {current_price} for BUY order")
            else:  # SELL
                if stop_price >= current_price:
                    logger.warning(f"Stop price {stop_price} is above current price {current_price} for SELL order")
            
            # Place order
            response = make_request('POST', self.endpoint, params, signed=True)
            
            logger.info(f"Stop-limit order placed successfully: Order ID {response.get('orderId')}")
            logger.info(f"Order details: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to place stop-limit order: {str(e)}")
            raise
    
    def place_stop_loss(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: float,
        limit_price: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Place a stop-loss order (convenience method)
        
        Args:
            symbol: Trading pair
            side: BUY (for short position) or SELL (for long position)
            quantity: Order quantity
            stop_price: Stop price trigger
            limit_price: Limit price (if None, uses stop_price - 0.1%)
            **kwargs: Additional parameters
            
        Returns:
            Order response
        """
        if limit_price is None:
            # Set limit price slightly below stop for SELL, above for BUY
            if side == OrderSide.SELL:
                limit_price = stop_price * 0.999  # 0.1% below
            else:
                limit_price = stop_price * 1.001  # 0.1% above
            
            logger.info(f"Auto-calculated limit price: {limit_price}")
        
        kwargs['reduce_only'] = True  # Stop loss should always reduce position
        
        return self.place_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            stop_price=stop_price,
            limit_price=limit_price,
            **kwargs
        )


def main():
    """Main CLI interface for stop-limit orders"""
    parser = argparse.ArgumentParser(
        description='Execute stop-limit orders on Binance Futures',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Stop-limit BUY: If price rises to $51,000, buy at limit $51,100
  python src/advanced/stop_limit.py BTCUSDT BUY 0.001 51000 51100
  
  # Stop-limit SELL: If price falls to $49,000, sell at limit $48,900
  python src/advanced/stop_limit.py BTCUSDT SELL 0.001 49000 48900
  
  # Stop-loss for long position (reduce only)
  python src/advanced/stop_limit.py BTCUSDT SELL 0.001 48000 47900 --reduce-only
  
  # Using mark price instead of contract price
  python src/advanced/stop_limit.py BTCUSDT SELL 0.001 49000 48900 --working-type MARK_PRICE
        """
    )
    
    parser.add_argument('symbol', type=str, help='Trading symbol (e.g., BTCUSDT)')
    parser.add_argument('side', type=str, choices=['BUY', 'SELL'], help='Order side')
    parser.add_argument('quantity', type=float, help='Order quantity')
    parser.add_argument('stop_price', type=float, help='Stop trigger price')
    parser.add_argument('limit_price', type=float, help='Limit execution price')
    parser.add_argument('--time-in-force', type=str, default='GTC',
                       choices=['GTC', 'IOC', 'FOK', 'GTX'],
                       help='Time in force (default: GTC)')
    parser.add_argument('--position-side', type=str, default='BOTH',
                       choices=['BOTH', 'LONG', 'SHORT'],
                       help='Position side (default: BOTH)')
    parser.add_argument('--working-type', type=str, default='CONTRACT_PRICE',
                       choices=['CONTRACT_PRICE', 'MARK_PRICE'],
                       help='Price type for trigger (default: CONTRACT_PRICE)')
    parser.add_argument('--reduce-only', action='store_true',
                       help='Reduce position only (for stop-loss)')
    
    args = parser.parse_args()
    
    try:
        executor = StopLimitOrderExecutor()
        
        print(f"\n{'='*50}")
        print(f"STOP-LIMIT ORDER - {args.side} {args.quantity} {args.symbol}")
        print(f"Stop Price: {args.stop_price}")
        print(f"Limit Price: {args.limit_price}")
        print(f"{'='*50}\n")
        
        response = executor.place_order(
            symbol=args.symbol,
            side=args.side,
            quantity=args.quantity,
            stop_price=args.stop_price,
            limit_price=args.limit_price,
            position_side=args.position_side,
            time_in_force=args.time_in_force,
            working_type=args.working_type,
            reduce_only=args.reduce_only
        )
        
        print(format_order_response(response))
        print(f"Stop Price: {args.stop_price}")
        print(f"Working Type: {args.working_type}")
        print(f"{'='*50}\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error executing stop-limit order: {str(e)}")
        print(f"\n❌ ERROR: {str(e)}\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
