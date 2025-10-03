"""
Market Orders Module for Binance Futures Trading Bot
Handles immediate execution of buy/sell orders at current market price
"""
import sys
import argparse
from typing import Dict, Any
from src.utils import (
    logger,
    make_request,
    validate_symbol,
    validate_quantity,
    format_order_response,
    get_symbol_price
)
from src.constants import OrderSide, OrderType, PositionSide


class MarketOrderExecutor:
    """Execute market orders on Binance Futures"""
    
    def __init__(self):
        self.endpoint = '/fapi/v1/order'
    
    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        position_side: str = PositionSide.BOTH,
        reduce_only: bool = False
    ) -> Dict[str, Any]:
        """
        Place a market order
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            side: BUY or SELL
            quantity: Order quantity
            position_side: Position side (BOTH, LONG, SHORT)
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
        
        if side not in [OrderSide.BUY, OrderSide.SELL]:
            raise ValueError(f"Invalid side: {side}. Must be BUY or SELL")
        
        # Prepare order parameters
        params = {
            'symbol': symbol.upper(),
            'side': side,
            'type': OrderType.MARKET,
            'quantity': quantity,
            'positionSide': position_side,
        }
        
        if reduce_only:
            params['reduceOnly'] = 'true'
        
        logger.info(f"Placing market order: {side} {quantity} {symbol}")
        
        try:
            # Get current price for logging
            current_price = get_symbol_price(symbol)
            logger.info(f"Current market price: {current_price}")
            
            # Place order
            response = make_request('POST', self.endpoint, params, signed=True)
            
            logger.info(f"Market order placed successfully: Order ID {response.get('orderId')}")
            logger.info(f"Order details: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to place market order: {str(e)}")
            raise
    
    def buy(self, symbol: str, quantity: float, **kwargs) -> Dict[str, Any]:
        """
        Place a market BUY order
        
        Args:
            symbol: Trading pair
            quantity: Order quantity
            **kwargs: Additional parameters
            
        Returns:
            Order response
        """
        return self.place_order(symbol, OrderSide.BUY, quantity, **kwargs)
    
    def sell(self, symbol: str, quantity: float, **kwargs) -> Dict[str, Any]:
        """
        Place a market SELL order
        
        Args:
            symbol: Trading pair
            quantity: Order quantity
            **kwargs: Additional parameters
            
        Returns:
            Order response
        """
        return self.place_order(symbol, OrderSide.SELL, quantity, **kwargs)


def main():
    """Main CLI interface for market orders"""
    parser = argparse.ArgumentParser(
        description='Execute market orders on Binance Futures',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Buy 0.001 BTC at market price
  python src/market_orders.py BTCUSDT BUY 0.001
  
  # Sell 0.5 ETH at market price
  python src/market_orders.py ETHUSDT SELL 0.5
  
  # Buy with reduce-only flag
  python src/market_orders.py BTCUSDT BUY 0.001 --reduce-only
        """
    )
    
    parser.add_argument('symbol', type=str, help='Trading symbol (e.g., BTCUSDT)')
    parser.add_argument('side', type=str, choices=['BUY', 'SELL'], help='Order side')
    parser.add_argument('quantity', type=float, help='Order quantity')
    parser.add_argument('--position-side', type=str, default='BOTH',
                       choices=['BOTH', 'LONG', 'SHORT'],
                       help='Position side (default: BOTH)')
    parser.add_argument('--reduce-only', action='store_true',
                       help='Reduce position only')
    
    args = parser.parse_args()
    
    try:
        executor = MarketOrderExecutor()
        
        print(f"\n{'='*50}")
        print(f"MARKET ORDER - {args.side} {args.quantity} {args.symbol}")
        print(f"{'='*50}\n")
        
        response = executor.place_order(
            symbol=args.symbol,
            side=args.side,
            quantity=args.quantity,
            position_side=args.position_side,
            reduce_only=args.reduce_only
        )
        
        print(format_order_response(response))
        print(f"{'='*50}\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error executing market order: {str(e)}")
        print(f"\n❌ ERROR: {str(e)}\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
