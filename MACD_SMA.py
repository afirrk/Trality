'''
LONG: Take long MACD signals when price is above the 150 period-moving average
ENTRY: Buy when the MACD crosses over the zero line
EXIT: Sell at a profit or loss when the MACD crosses below the zero line
'''

def initialize(state):
    state.number_offset_trades = 0;

def signal(data):
    macd = data.macd(12, 36, 9)
    sma = data.sma(150)

    if macd is None or sma is None:
        return

    if data.close_last > sma.last and macd['macd_histogram'].last >= 0:
        return 'BUY'
    #elif data.close_last > bbands_upper:
        #return 'OVERBOUGHT'
    elif macd['macd_histogram'].last <= 0:
        return 'SELL'



@schedule(interval="1h", symbol = "ETHUSDT", window_size=200)
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
    if signal(data) == 'BUY' and not has_position:
        print("-------")
        print("Buy Signal: creating market order for {}".format(data.symbol))
        print("Buy value: ", buy_value, " at current market price: ", data.close_last)
        
        order_market_value(symbol=data.symbol, value=buy_value)

    elif signal(data) == 'SELL' and has_position:
        logmsg = "Sell Signal: closing {} position with exposure {} at current market price {}"
        print("-------")
        print(logmsg.format(data.symbol,float(position.exposure),data.close_last))

        close_position(data.symbol)
