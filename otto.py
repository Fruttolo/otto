import os
import time
from termcolor import colored
import MetaTrader5 as mt5
from variabili import *

# VARIABILI DA NON TOCCARE
GETDATA = 1000
DEVIATION = 20
INCERTEZZA = 0

# function to send a market order
def market_order(symbol, volume, order_type, **kwargs):
    tick = mt5.symbol_info_tick(symbol)

    order_dict = {'buy': 0, 'sell': 1}
    price_dict = {'buy': tick.ask, 'sell': tick.bid}
    
    if(order_type == 'buy'):
        stopLoss = tick.bid - (STOPLOSS / 10)
    else:
        stopLoss = tick.bid + (STOPLOSS / 10)

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_dict[order_type],
        "price": price_dict[order_type],
        "deviation": DEVIATION,
        "sl": stopLoss,
        "magic": 100,
        "comment": "python market order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    order_result = mt5.order_send(request)
    print(order_result)

    return order_result

def trade(direction):
    color = ''
    if direction == 'buy':
        color = 'green'
    else:
        color = 'red'
    for i in range(N_OPERAZIONI):
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
    
def lastElement(a, b = 1):
    if len(a) == 0:
        return None
    else:
        return a[-b]

def currentTime():
    h = time.localtime().tm_hour
    m = time.localtime().tm_min
    if h < 10 :
        h = '0'+str(h)
    if m < 10 :
        m = '0'+str(h)
    return str(h)+':'+str(m)

def wait_min(minutes):
    time.sleep(5)
    if minutes == 1 :
        s = time.localtime().tm_sec
        while s != 1 :
            time.sleep(1)
            s = time.localtime().tm_sec
    elif minutes > 1 and minutes < 59 :
        s = time.localtime().tm_sec
        m = time.localtime().tm_min
        while s != 1 or  m%minutes != 0:
            time.sleep(1)
            s = time.localtime().tm_sec
            m = time.localtime().tm_min
    elif minutes > 59 and minutes < 60*24 :
        s = time.localtime().tm_sec
        m = time.localtime().tm_min
        h = time.localtime().tm_hour
        while s != 1 or  m != 0 or h%(minutes/60)!=0 :
            time.sleep(1)
            s = time.localtime().tm_sec
            m = time.localtime().tm_min
            h = time.localtime().tm_hour
    else : 
        raise Exception("Timeframe not valid")

def waiting(timeframe):
    if timeframe == '1m' :
        wait_min(1)
        return
    elif timeframe == '5m':
        wait_min(5)
        return
    elif timeframe == '15m':
        wait_min(15)
        return
    elif timeframe == '30m':
        wait_min(30)
        return
    elif timeframe == '1h':
        wait_min(60)
        return
    elif timeframe == '2h':
        wait_min(60*2)
        return
    elif timeframe == '4h':
        wait_min(60*4)
        return
    else:
        raise Exception("Timeframe not valid")
    
def timeframe(timeframe):
    if timeframe == '1m' :
        return mt5.TIMEFRAME_M1
    elif timeframe == '5m':
        return mt5.TIMEFRAME_M5
    elif timeframe == '15m':
        return mt5.TIMEFRAME_M15
    elif timeframe == '30m':
        return mt5.TIMEFRAME_M30
    elif timeframe == '1h':
        return mt5.TIMEFRAME_H1
    elif timeframe == '2h':
        return mt5.TIMEFRAME_H2
    elif timeframe == '4h':
        return mt5.TIMEFRAME_H4
    else:
        raise Exception("Timeframe not valid")
         
def calculate_ci(a, b, c):
    if c == 0 :
        return None
    return ( a - b ) / ( 0.015 * c )

def calculate_risk(balance):
    return  (((balance/100)*RISCHIO)/(STOPLOSS/10))/N_OPERAZIONI


data = 0
loaded = True

os.system("CLS")
mt5.initialize()

print('-- OTTO -- ',TIMEFRAME)
print()

while True:
    
    close = []
    ema = []
    hlc3 = []
    esa = []
    d = []
    tci = []
    wt2 = []
    
    data = data + 1
    
    historyCandles = mt5.copy_rates_from_pos(SYMBOL, timeframe(TIMEFRAME), 0, GETDATA)

    for candle in historyCandles[:-1] :
        close.append(candle[4])
        hlc3.append((candle[4]+candle[2]+candle[3] )/3)
        esa.append(calculate_ema(lastElement(hlc3), lastElement(esa), N1 ))
        d.append(calculate_ema(abs(lastElement(hlc3)-lastElement(esa)), lastElement(d), N1 ))
        ci =  calculate_ci(lastElement(hlc3), lastElement(esa), lastElement(d))
        tci.append(calculate_ema(ci, lastElement(tci), N2))
        wt2.append(calculate_sma(tci,4))
        ema.append(calculate_ema(lastElement(close), lastElement(ema), 20))
        
    print('---',currentTime(),'---',data)
    print('price:',colored(lastElement(close),'white'))
    #print('ema20:', colored(lastElement(ema),'blue'))
    #print('hlc3:', colored(lastElement(hlc3),'white'))
    #print('esa:', colored(lastElement(esa),'red'))
    #print('d:', colored(lastElement(d),'green'))
    #print('ci:', colored(ci,'magenta'))
    print('linea:', colored(lastElement(tci),'white'))
    print('pallino:', colored(lastElement(wt2),'yellow'))
    print()
    
    pallino = lastElement(wt2)
    linea = lastElement(tci)
    lastPallino = lastElement(wt2,2)
    lastLinea = lastElement(tci,2)
    
    b = mt5.account_info().balance
    VOLUME = round(calculate_risk(b) / 100,2)
    
    # FIRST TRADE
    if loaded : 
        if pallino > linea + INCERTEZZA:
            trade('sell')
        elif pallino < linea - INCERTEZZA:
            trade('buy')
        loaded = False
    else:
        # ALL OTHER TRADE
        if pallino > linea + INCERTEZZA and lastPallino < lastLinea + INCERTEZZA:
            trade('sell')
        elif pallino < linea - INCERTEZZA and lastPallino > lastLinea - INCERTEZZA:
            trade('buy')
    
    waiting(TIMEFRAME)

