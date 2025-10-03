"""
Constants and enumerations for the trading bot
"""

# Order Types
class OrderType:
    MARKET = 'MARKET'
    LIMIT = 'LIMIT'
    STOP = 'STOP'
    STOP_MARKET = 'STOP_MARKET'
    TAKE_PROFIT = 'TAKE_PROFIT'
    TAKE_PROFIT_MARKET = 'TAKE_PROFIT_MARKET'
    TRAILING_STOP_MARKET = 'TRAILING_STOP_MARKET'

# Order Sides
class OrderSide:
    BUY = 'BUY'
    SELL = 'SELL'

# Position Sides
class PositionSide:
    BOTH = 'BOTH'
    LONG = 'LONG'
    SHORT = 'SHORT'

# Time in Force
class TimeInForce:
    GTC = 'GTC'  # Good Till Cancel
    IOC = 'IOC'  # Immediate or Cancel
    FOK = 'FOK'  # Fill or Kill
    GTX = 'GTX'  # Good Till Crossing (Post Only)

# Order Status
class OrderStatus:
    NEW = 'NEW'
    PARTIALLY_FILLED = 'PARTIALLY_FILLED'
    FILLED = 'FILLED'
    CANCELED = 'CANCELED'
    PENDING_CANCEL = 'PENDING_CANCEL'
    REJECTED = 'REJECTED'
    EXPIRED = 'EXPIRED'

# Response Types
class ResponseType:
    ACK = 'ACK'
    RESULT = 'RESULT'

# Working Types
class WorkingType:
    MARK_PRICE = 'MARK_PRICE'
    CONTRACT_PRICE = 'CONTRACT_PRICE'

# Error Messages
ERROR_MESSAGES = {
    'INVALID_SYMBOL': 'Invalid trading symbol',
    'INVALID_QUANTITY': 'Invalid quantity. Must be positive number',
    'INVALID_PRICE': 'Invalid price. Must be positive number',
    'INSUFFICIENT_BALANCE': 'Insufficient balance for order',
    'API_ERROR': 'Binance API error occurred',
    'NETWORK_ERROR': 'Network connection error',
    'INVALID_PARAMS': 'Invalid parameters provided',
}
