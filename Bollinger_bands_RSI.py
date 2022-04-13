'''
When price gets below lower band and RSI 30 - Buy
When price gets above middle (or upper band) - Sell
'''

def initialize(state):
    state.number_offset_trades = 0;

def signal(data):
    bbands = data.bbands(20, 2)
    # on erronous data return early (indicators are of NoneType)
    if bbands is None:
        return

    bbands_lower = bbands["bbands_lower"].last
    bbands_upper = bbands["bbands_upper"].last
    bbands_middle = bbands["bbands_middle"].last

    rsi = data.rsi(14).last

    if data.close_last < bbands_lower and rsi < 30:
        return 'OVERSOLD'
    #elif data.close_last > bbands_upper:
        #return 'OVERBOUGHT'
    elif data.close_last > bbands_middle:
        return 'OVERBOUGHT'



@schedule(interval="1h", symbol = "ETHUSDT")
def handler(state, data):
    '''
    1) Compute indicators from data
    '''
    
    # on erronous data return early (indicators are of NoneType)

    current_price = data.close_last
    
    '''
    2) Fetch portfolio
        > check liquidity (in quoted currency)
        > resolve buy value
    '''
    
    portfolio = query_portfolio()
    balance_quoted = portfolio.excess_liquidity_quoted
    # we invest only 80% of available liquidity
    buy_value = float(balance_quoted) * 0.80
    
    
    '''
    3) Fetch position for symbol
        > has open position
        > check exposure (in base currency)
    '''

    position = query_open_position_by_symbol(data.symbol,include_dust=False)
    has_position = position is not None

    '''
    4) Resolve buy or sell signals
        > create orders using the order api
        > print position information
        
    '''
    if signal(data) == 'OVERSOLD' and not has_position:
        print("-------")
        print("Buy Signal: creating market order for {}".format(data.symbol))
        print("Buy value: ", buy_value, " at current market price: ", data.close_last)
        
        order_market_value(symbol=data.symbol, value=buy_value)

    elif signal(data) == 'OVERBOUGHT' and has_position:
        logmsg = "Sell Signal: closing {} position with exposure {} at current market price {}"
        print("-------")
        print(logmsg.format(data.symbol,float(position.exposure),data.close_last))

        close_position(data.symbol)
