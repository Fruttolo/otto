from tradingview_ta import TA_Handler
import os
import time
from termcolor import colored
import MetaTrader5 as mt5

N1 = 10
N2 = 21
LOAD = 20
SYMBOL = "XAUUSD"
VOLUME = 1.0
DEVIATION = 20
INCERTEZZA = 5
TIMEFRAME = "5m"

# Crea un oggetto TA_Handler per la coppia di trading e l'intervallo di tempo specificati
ta_handler = TA_Handler(
    symbol=SYMBOL,
    exchange="OANDA",
    screener="cfd",
    interval=TIMEFRAME,
    timeout=None
)

# function to send a market order
def market_order(symbol, volume, order_type, **kwargs):
    tick = mt5.symbol_info_tick(symbol)

    order_dict = {'buy': 0, 'sell': 1}
    price_dict = {'buy': tick.ask, 'sell': tick.bid}

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_dict[order_type],
        "price": price_dict[order_type],
        "deviation": DEVIATION,
        "magic": 100,
        "comment": "python market order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    order_result = mt5.order_send(request)
    print(order_result)

    return order_result


# function to close an order base don ticket id
def close_order(ticket):
    positions = mt5.positions_get()

    for pos in positions:
        tick = mt5.symbol_info_tick(pos.symbol)
        type_dict = {0: 1, 1: 0}  # 0 represents buy, 1 represents sell - inverting order_type to close the position
        price_dict = {0: tick.ask, 1: tick.bid}

        if pos.ticket == ticket:
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "position": pos.ticket,
                "symbol": pos.symbol,
                "volume": pos.volume,
                "type": type_dict[pos.type],
                "price": price_dict[pos.type],
                "deviation": DEVIATION,
                "magic": 100,
                "comment": "python close order",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            order_result = mt5.order_send(request)
            print(order_result)

            return order_result

    return 'Ticket does not exist'

def trade(direction):
    color = ''
    # trading logic
    if direction == 'buy':
        color = 'green'
        # if we have a BUY signal, close all short positions
        for pos in mt5.positions_get():
            if pos.type == 1:  # pos.type == 1 represent a sell order
                close_order(pos.ticket)

        # if there are no open positions, open a new long position
        if not mt5.positions_total():
            market_order(SYMBOL, VOLUME, direction)

    elif direction == 'sell':
        color = 'red'
        # if we have a SELL signal, close all short positions
        for pos in mt5.positions_get():
            if pos.type == 0:  # pos.type == 0 represent a buy order
                close_order(pos.ticket)

        # if there are no open positions, open a new short position
        if not mt5.positions_total():
            market_order(SYMBOL, VOLUME, direction)
            
    print(' >> ',colored(direction,color))
    print()

def calculate_ema(price, lastEma , window):
    alpha = 2 / (window + 1)
    if lastEma is None:
        return price
    else:
        return alpha * price + (1 - alpha) * lastEma
    
def calculate_sma(x, y):
    if len(x) < y+2:
        return None
    sum = 0
    for i in range(len(x)-y,len(x)):
        sum = sum + ( x[i] / y )
    return sum
    
def lastElement(a):
    if len(a) == 0:
        return None
    else:
        return a[-1]

def calculate_hlc3(market_data):
    return ( market_data.indicators['close'] + market_data.indicators['high'] + market_data.indicators['low'] ) / 3

def currentTime():
    return str(time.localtime().tm_hour)+':'+str(time.localtime().tm_min)+':'+str(time.localtime().tm_sec)

def wait_min(minutes):
    for i in range(minutes):
        s = time.localtime().tm_sec
        while not (s < 60 and s > 55):
            time.sleep(1)
            s = time.localtime().tm_sec
        if i < minutes - 1:
            time.sleep(5)
        else:
            return

def waiting(timeframe):
    if data == 0  :
        print('- SYNCRONIZYNG -','TIMEFRAME:',TIMEFRAME,' -')
        sec = time.localtime().tm_sec
        while not (sec < 60 and sec > 55):
            time.sleep(1)
            sec = time.localtime().tm_sec
        return
    print('- WAITING NEXT CANDLE -')
    if timeframe == '1m' :
        wait_min(1)
    elif timeframe == '5m':
        wait_min(60*5)
    elif timeframe == '15m':
        wait_min(60*15)
    elif timeframe == '30m':
        wait_min(60*30)
    elif timeframe == '1h':
        wait_min(60*60)
    elif timeframe == '2h':
        wait_min(60*60*2)
    elif timeframe == '4h':
        wait_min(60*60*4)
    elif timeframe == '1d':
        wait_min(60*60*24)
    elif timeframe == '1W':
        wait_min(60*60*24*7)
    else:
        raise Exception("Timeframe not valid")
         

def calculate_ci(a, b, c):
    if c == 0 :
        return None
    return ( a - b ) / ( 0.015 * c )

close = []
ema = []
hlc3 = []
esa = []
d = []
tci = []
wt2 = []
flag = 0
data = 0

os.system("CLS")
mt5.initialize()

while True :

    waiting(TIMEFRAME)

    #if ( sec < 60 and sec > 55 ) :
        #if flag == 0 :

    # FETCH MARKET DATA
    market_data = ta_handler.get_analysis()

    close.append(market_data.indicators['close'])
    hlc3.append(calculate_hlc3(market_data))
    esa.append(calculate_ema(lastElement(hlc3), lastElement(esa), N1 ))
    d.append(calculate_ema(abs(lastElement(hlc3)-lastElement(esa)), lastElement(d), N1 ))
    ci =  calculate_ci(lastElement(hlc3), lastElement(esa), lastElement(d))
    tci.append(calculate_ema(ci, lastElement(tci), N2))
    wt2.append(calculate_sma(tci,4))

    ema.append(calculate_ema(lastElement(close), lastElement(ema), 20))

    data = data + 1

    print('---',currentTime(),'---',data)
    print('current price:',colored(lastElement(close),'white'))
    print('ema20:', colored(lastElement(ema),'blue'))
    print('hlc3:', colored(lastElement(hlc3),'white'))
    print('esa:', colored(lastElement(esa),'red'))
    print('d:', colored(lastElement(d),'green'))
    print('ci:', colored(ci,'magenta'))
    print('tci:', colored(lastElement(tci),'white'))
    print('wt2:', colored(lastElement(wt2),'yellow'))
    print()

    pallino = lastElement(wt2)
    linea = lastElement(tci)

    if data > LOAD :
        if pallino > linea + INCERTEZZA :
            signal = 'sell'
        elif pallino < linea - INCERTEZZA :
            signal = 'buy'
            
        trade(signal)
    
    time.sleep(4)

            #flag = 1
    #else: 
        #flag = 0

    #or ( sec < 60 and sec > 55 )
    #or ( sec < 30 and sec > 25 )