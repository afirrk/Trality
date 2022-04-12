'''
When all the short-term EMAs cross above the long term EMAs + RSI below 30 - Buy
When all the short-term EMAs cross below the long term EMAs - Sell
'''

def initialize(state):
    state.number_offset_trades = 0;

def singla(data):
    ema_short_1 = data.ema(3).last
    ema_short_2 = data.ema(5).last
    ema_short_3 = data.ema(8).last
    ema_short_4 = data.ema(10).last
    ema_short_5 = data.ema(12).last
    ema_short_6 = data.ema(15).last

    ema_long_1 = data.ema(30).last
    ema_long_2 = data.ema(35).last
    ema_long_3 = data.ema(40).last
    ema_long_4 = data.ema(45).last
    ema_long_5 = data.ema(50).last
    ema_long_6 = data.ema(60).last

    if ema_long_6 is None:
        return

    short_list = [ema_short_1, ema_short_2, ema_short_3, ema_short_4, ema_short_5, ema_short_6]
    long_list = [ema_long_1, ema_long_2, ema_long_3, ema_long_4, ema_long_5, ema_long_6] 

    if min(short_list) > max(long_list):
        return 'LONG'
    if max(short_list) < min(long_list):
        return 'SHORT'



@schedule(interval="1h", symbol = "ETHUSDT")
def handler(state, data):
    '''
    1) Compute indicators from data
    '''
    rsi = data.rsi(5).last

    if rsi is None:
        return

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
    if singla(data) == 'LONG' and rsi <= 30 and not has_position:
        print("-------")
        print("Buy Signal: creating market order for {}".format(data.symbol))
        print("Buy value: ", buy_value, " at current market price: ", data.close_last)
        
        order_market_value(symbol=data.symbol, value=buy_value)

    elif singla(data) == 'SHORT' and has_position:
        print("-------")
        logmsg = "Sell Signal: closing {} position with exposure {} at current market price {}"
        print(logmsg.format(data.symbol,float(position.exposure),data.close_last))

        close_position(data.symbol)
