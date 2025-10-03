"""
OCO (One-Cancels-the-Other) Orders Module
Places simultaneous take-profit and stop-loss orders
"""
import sys
import argparse
from typing import Dict, Any
from src.utils import (
    logger,
    make_request,
    validate_symbol,
    validate_quantity,
    validate_price,
    get_symbol_price
)
from src.constants import OrderSide, PositionSide, TimeInForce, WorkingType


class OCOOrderExecutor:
    """Execute OCO (One-Cancels-the-Other) orders on Binance Futures"""
    
    def __init__(self):
        self.endpoint = '/fapi/v1/order'
    
    def place_oco_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        take_profit_price: float,
        stop_loss_price: float,
        stop_limit_price: float = None,
        position_side: str = PositionSide.BOTH,
        working_type: str = WorkingType.CONTRACT_PRICE
    ) -> Dict[str, Any]:
        """
        Place OCO order (Take Profit + Stop Loss)
        
        Note: Binance Futures doesn't have native OCO, so we simulate it by placing
        two separate orders: a take-profit limit order and a stop-loss order.
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            side: BUY or SELL (for closing position)
            quantity: Order quantity
            take_profit_price: Take profit target price
            stop_loss_price: Stop loss trigger price
            stop_limit_price: Stop limit price (if None, uses stop market)
            position_side: Position side (BOTH, LONG, SHORT)
            working_type: Working type for stop (MARK_PRICE or CONTRACT_PRICE)
            
        Returns:
            Dictionary with both order responses
            
        Raises:
            Exception: If order placement fails
        """
        # Validate inputs
        if not validate_symbol(symbol):
            raise ValueError(f"Invalid symbol: {symbol}")
        
        if not validate_quantity(quantity):
            raise ValueError(f"Invalid quantity: {quantity}")
        
        if not validate_price(take_profit_price):
            raise ValueError(f"Invalid take profit price: {take_profit_price}")
        
        if not validate_price(stop_loss_price):
            raise ValueError(f"Invalid stop loss price: {stop_loss_price}")
        
        if side not in [OrderSide.BUY, OrderSide.SELL]:
            raise ValueError(f"Invalid side: {side}. Must be BUY or SELL")
        
        # Get current price for validation
        current_price = get_symbol_price(symbol)
        logger.info(f"Current market price: {current_price}")
        
        # Validate price levels make sense
        if side == OrderSide.SELL:  # Closing a long position
            if take_profit_price <= current_price:
                logger.warning(f"Take profit price {take_profit_price} is below current price {current_price}")
            if stop_loss_price >= current_price:
                logger.warning(f"Stop loss price {stop_loss_price} is above current price {current_price}")
        else:  # Closing a short position (BUY)
            if take_profit_price >= current_price:
                logger.warning(f"Take profit price {take_profit_price} is above current price {current_price}")
            if stop_loss_price <= current_price:
                logger.warning(f"Stop loss price {stop_loss_price} is below current price {current_price}")
        
        try:
            # Place Take Profit Order (Limit Order)
            tp_params = {
                'symbol': symbol.upper(),
                'side': side,
                'type': 'TAKE_PROFIT',
                'quantity': quantity,
                'stopPrice': take_profit_price,
                'price': take_profit_price,
                'timeInForce': TimeInForce.GTC,
                'positionSide': position_side,
                'workingType': working_type,
                'reduceOnly': 'true'
            }
            
            logger.info(f"Placing take profit order at {take_profit_price}")
            tp_response = make_request('POST', self.endpoint, tp_params, signed=True)
            logger.info(f"Take profit order placed: Order ID {tp_response.get('orderId')}")
            
            # Place Stop Loss Order
            sl_params = {
                'symbol': symbol.upper(),
                'side': side,
                'type': 'STOP_MARKET' if not stop_limit_price else 'STOP',
                'quantity': quantity,
                'stopPrice': stop_loss_price,
                'positionSide': position_side,
                'workingType': working_type,
                'reduceOnly': 'true'
            }
            
            if stop_limit_price:
                sl_params['price'] = stop_limit_price
                sl_params['timeInForce'] = TimeInForce.GTC
            
            logger.info(f"Placing stop loss order at {stop_loss_price}")
            sl_response = make_request('POST', self.endpoint, sl_params, signed=True)
            logger.info(f"Stop loss order placed: Order ID {sl_response.get('orderId')}")
            
            result = {
                'take_profit_order': tp_response,
                'stop_loss_order': sl_response,
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'current_price': current_price,
                'take_profit_price': take_profit_price,
                'stop_loss_price': stop_loss_price
            }
            
            logger.info("OCO orders placed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to place OCO order: {str(e)}")
            # Try to cancel any placed orders if one fails
            try:
                if 'tp_response' in locals():
                    logger.warning("Attempting to cancel take profit order due to error")
                    cancel_params = {
                        'symbol': symbol.upper(),
                        'orderId': tp_response['orderId']
                    }
                    make_request('DELETE', self.endpoint, cancel_params, signed=True)
            except:
                pass
            raise
    
    def cancel_oco_orders(self, symbol: str, tp_order_id: int, sl_order_id: int) -> Dict[str, Any]:
        """
        Cancel both OCO orders
        
        Args:
            symbol: Trading pair
            tp_order_id: Take profit order ID
            sl_order_id: Stop loss order ID
            
        Returns:
            Dictionary with cancellation responses
        """
        logger.info(f"Cancelling OCO orders for {symbol}: TP={tp_order_id}, SL={sl_order_id}")
        
        results = {}
        
        try:
            # Cancel take profit order
            tp_params = {
                'symbol': symbol.upper(),
                'orderId': tp_order_id
            }
            tp_cancel = make_request('DELETE', self.endpoint, tp_params, signed=True)
            results['take_profit_cancelled'] = tp_cancel
            logger.info(f"Take profit order {tp_order_id} cancelled")
        except Exception as e:
            logger.error(f"Failed to cancel take profit order: {str(e)}")
            results['take_profit_error'] = str(e)
        
        try:
            # Cancel stop loss order
            sl_params = {
                'symbol': symbol.upper(),
                'orderId': sl_order_id
            }
            sl_cancel = make_request('DELETE', self.endpoint, sl_params, signed=True)
            results['stop_loss_cancelled'] = sl_cancel
            logger.info(f"Stop loss order {sl_order_id} cancelled")
        except Exception as e:
            logger.error(f"Failed to cancel stop loss order: {str(e)}")
            results['stop_loss_error'] = str(e)
        
        return results


def main():
    """Main CLI interface for OCO orders"""
    parser = argparse.ArgumentParser(
        description='Execute OCO (One-Cancels-the-Other) orders on Binance Futures',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Close long position with TP at $52,000 and SL at $48,000
  python src/advanced/oco.py BTCUSDT SELL 0.001 52000 48000
  
  # Close short position with TP at $48,000 and SL at $52,000
  python src/advanced/oco.py BTCUSDT BUY 0.001 48000 52000
  
  # OCO with stop-limit instead of stop-market
  python src/advanced/oco.py BTCUSDT SELL 0.001 52000 48000 --stop-limit-price 47900
  
  # Cancel OCO orders
  python src/advanced/oco.py BTCUSDT --cancel-tp TP_ORDER_ID --cancel-sl SL_ORDER_ID
        """
    )
    
    parser.add_argument('symbol', type=str, help='Trading symbol (e.g., BTCUSDT)')
    parser.add_argument('side', type=str, nargs='?', choices=['BUY', 'SELL'],
                       help='Order side (BUY to close short, SELL to close long)')
    parser.add_argument('quantity', type=float, nargs='?', help='Order quantity')
    parser.add_argument('take_profit', type=float, nargs='?',
                       help='Take profit price')
    parser.add_argument('stop_loss', type=float, nargs='?',
                       help='Stop loss trigger price')
    parser.add_argument('--stop-limit-price', type=float,
                       help='Stop limit price (if not set, uses stop market)')
    parser.add_argument('--position-side', type=str, default='BOTH',
                       choices=['BOTH', 'LONG', 'SHORT'],
                       help='Position side (default: BOTH)')
    parser.add_argument('--working-type', type=str, default='CONTRACT_PRICE',
                       choices=['CONTRACT_PRICE', 'MARK_PRICE'],
                       help='Working type for stop orders (default: CONTRACT_PRICE)')
    parser.add_argument('--cancel-tp', type=int, metavar='ORDER_ID',
                       help='Cancel take profit order by ID')
    parser.add_argument('--cancel-sl', type=int, metavar='ORDER_ID',
                       help='Cancel stop loss order by ID')
    
    args = parser.parse_args()
    
    try:
        executor = OCOOrderExecutor()
        
        # Cancel OCO orders
        if args.cancel_tp and args.cancel_sl:
            print(f"\n{'='*50}")
            print(f"CANCELLING OCO ORDERS for {args.symbol}")
            print(f"{'='*50}\n")
            
            result = executor.cancel_oco_orders(args.symbol, args.cancel_tp, args.cancel_sl)
            
            if 'take_profit_cancelled' in result:
                print(f"✅ Take Profit order {args.cancel_tp} cancelled")
            else:
                print(f"❌ Take Profit cancellation failed: {result.get('take_profit_error')}")
            
            if 'stop_loss_cancelled' in result:
                print(f"✅ Stop Loss order {args.cancel_sl} cancelled")
            else:
                print(f"❌ Stop Loss cancellation failed: {result.get('stop_loss_error')}")
            
            print(f"\n{'='*50}\n")
            return 0
        
        # Place OCO order
        if not all([args.side, args.quantity, args.take_profit, args.stop_loss]):
            parser.error("side, quantity, take_profit, and stop_loss are required for placing OCO orders")
        
        print(f"\n{'='*50}")
        print(f"OCO ORDER - {args.side} {args.quantity} {args.symbol}")
        print(f"Take Profit: {args.take_profit}")
        print(f"Stop Loss: {args.stop_loss}")
        print(f"{'='*50}\n")
        
        response = executor.place_oco_order(
            symbol=args.symbol,
            side=args.side,
            quantity=args.quantity,
            take_profit_price=args.take_profit,
            stop_loss_price=args.stop_loss,
            stop_limit_price=args.stop_limit_price,
            position_side=args.position_side,
            working_type=args.working_type
        )
        
        print(f"✅ OCO Orders Placed Successfully")
        print(f"\nCurrent Price: {response['current_price']}")
        print(f"\nTake Profit Order:")
        print(f"  Order ID: {response['take_profit_order']['orderId']}")
        print(f"  Price: {response['take_profit_price']}")
        print(f"  Status: {response['take_profit_order']['status']}")
        print(f"\nStop Loss Order:")
        print(f"  Order ID: {response['stop_loss_order']['orderId']}")
        print(f"  Trigger Price: {response['stop_loss_price']}")
        print(f"  Status: {response['stop_loss_order']['status']}")
        print(f"\n{'='*50}\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error executing OCO order: {str(e)}")
        print(f"\n❌ ERROR: {str(e)}\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
