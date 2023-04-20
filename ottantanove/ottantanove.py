import os
import time
from termcolor import colored
import MetaTrader5 as mt5
from variabili import *
import math

def OnTick():
    while True : 
        # OTTO       
        bars = mt5.copy_rates_from_pos(SYMBOL, timeframe(TIMEFRAME), 0, 2)
        candle = bars[0]
        global lastCandleTime
        
        if candle[0] != lastCandleTime :
            
            # CALCOLO INDICATORE
            calculate_indicator(candle[4],candle[2],candle[3])
            print_candle()
            
            # CALCOLO PALLINO LINEA
            pallino = lastElement(wt2)
            linea = lastElement(tci)
            lastPallino = lastElement(wt2,2)
            lastLinea = lastElement(tci,2)
            
            b = mt5.account_info().balance
            global VOLUME
            VOLUME = round(calculate_risk(b),2)
            
            # SIGNAL LOGIC
            if pallino > linea and lastPallino < lastLinea :
                trade('sell')
            elif pallino < linea  and lastPallino > lastLinea :
                trade('buy')
            
            lastCandleTime = candle[0]
        
        # NOVE 
        for ticketCode in openTrade :
            pos = mt5.positions_get(ticket=ticketCode)
            if len(pos) == 0 :
                print("ordine chiuso :",ticketCode)
                print()
                openTrade.remove(ticketCode)
                continue
            pos = pos[0]
            if pos.type == 0:
                if pos.sl < pos.price_open :
                    if pos.price_current >= pos.price_open + (BREAK_EVEN / 10) :
                        if pos.tp == 0 :
                            modify_order(pos,'up')
                else :
                    if pos.price_current >= pos.sl + (SPOSTAMENTO_STOPLOSS / 10)*2 :
                        modify_order(pos,'up')
            else :
                if pos.sl > pos.price_open :
                    if pos.price_current <= pos.price_open - (BREAK_EVEN / 10) :
                        if pos.tp == 0 :
                            modify_order(pos,'down')
                else :
                    if pos.price_current <= pos.sl - (SPOSTAMENTO_STOPLOSS / 10)*2 :
                        modify_order(pos,'down')
        

def init():   
    os.system("CLS")
    mt5.initialize()

    print('-- OTTANTANOVE -- ',TIMEFRAME)
    print()  
     
    historyCandles = mt5.copy_rates_from_pos(SYMBOL, timeframe(TIMEFRAME), 0, GETDATA)

    # GLOBAL VARIABLES
    global close
    close = []
    global ema
    ema = []
    global hlc3
    hlc3 = []
    global esa
    esa = []
    global d
    d = []
    global tci
    tci = []
    global wt2
    wt2 = []
    global openTrade
    openTrade = []
    global lastCandleTime
    
    lastCandleTime = historyCandles[-2][0]
    for candle in historyCandles[:-1] :
        calculate_indicator(candle[4],candle[2],candle[3])
        
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

def calculate_ci(a, b, c):
    if c == 0 :
        return None
    return ( a - b ) / ( 0.015 * c )
    
def lastElement(a, b = 1):
    if len(a) == 0:
        return None
    else:
        return a[-b]
    
def calculate_risk(balance):
    return  ((((balance/100)*RISCHIO)/(STOPLOSS/10))/N_OPERAZIONI) / 100
    
def currentTime():
    h = time.localtime().tm_hour
    m = time.localtime().tm_min
    s = time.localtime().tm_sec
    if h < 10 :
        h = '0'+str(h)
    if m < 10 :
        m = '0'+str(m)
    if s < 10 :
        s = '0'+str(s)
    return str(h)+':'+str(m)+':'+str(s)

def calculate_indicator(cl, high, low):
    close.append(cl)
    hlc3.append((cl+high+low )/3)
    esa.append(calculate_ema(lastElement(hlc3), lastElement(esa), N1 ))
    d.append(calculate_ema(abs(lastElement(hlc3)-lastElement(esa)), lastElement(d), N1 ))
    ci =  calculate_ci(lastElement(hlc3), lastElement(esa), lastElement(d))
    tci.append(calculate_ema(ci, lastElement(tci), N2))
    wt2.append(calculate_sma(tci,4))
    #ema.append(calculate_ema(lastElement(close), lastElement(ema), 20))
    
def print_candle():
    print('---',currentTime(),'---',len(close)-GETDATA+1)
    print('price:',colored(lastElement(close),'white'))
    #print('ema20:', colored(lastElement(ema),'blue'))
    #print('hlc3:', colored(lastElement(hlc3),'white'))
    #print('esa:', colored(lastElement(esa),'red'))
    #print('d:', colored(lastElement(d),'green'))
    #print('ci:', colored(ci,'magenta'))
    print('linea:', colored(lastElement(tci),'white'))
    print('pallino:', colored(lastElement(wt2),'yellow'))
    print('area blu:',colored(lastElement(tci)-lastElement(wt2),'blue'))
    print()
    
def trade(direction):
    count = 0
    if CHIUSURA_OPERAZIONI_BREAKEVEN > 0 :
        count = math.ceil( (N_OPERAZIONI / 100) * CHIUSURA_OPERAZIONI_BREAKEVEN )
    color = ''
    if direction == 'buy':
        color = 'green'
    else:
        color = 'red'
    for i in range(N_OPERAZIONI):
        market_order(SYMBOL, direction, count > 0)
        count = count - 1
    print(' >> ',colored(direction,color))
    print()
    
def market_order(symbol, order_type, tp):
    tick = mt5.symbol_info_tick(symbol)

    order_dict = {'buy': 0, 'sell': 1}
    price_dict = {'buy': tick.ask, 'sell': tick.bid}
    
    if(order_type == 'buy'):
        stopLoss = price_dict[order_type] - (STOPLOSS / 10)
    else:
        stopLoss = price_dict[order_type] + (STOPLOSS / 10)

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": VOLUME,
        "type": order_dict[order_type],
        "price": price_dict[order_type],
        "deviation": DEVIATION,
        "sl": stopLoss,
        "magic": 100,
        "comment": "Ottantanove - " + TIMEFRAME,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    if tp :
        if order_type == 'buy' :
            request['tp'] = (price_dict[order_type] + (BREAK_EVEN / 10))
        else :
            request['tp'] = (price_dict[order_type] - (BREAK_EVEN / 10))

    order_result = mt5.order_send(request)
    global openTrade
    openTrade.append(order_result.order)
    print(order_result)

    return order_result

def modify_order(pos,dir):
    
    if(dir == 'up'):
        if pos.sl < pos.price_open :
            stopLoss = pos.price_open + 0.1
        else :
            stopLoss = pos.sl + (SPOSTAMENTO_STOPLOSS / 10)
    else:
        if pos.sl > pos.price_open :
            stopLoss = pos.price_open - 0.1
        else :
            stopLoss = pos.sl - (SPOSTAMENTO_STOPLOSS / 10)
    
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "symbol": pos.symbol,
        "position": pos.ticket,
        "symbol": pos.symbol,
        "volume": pos.volume,
        "price_open": pos.price_open,
        "sl": stopLoss,
        "deviation": 20,
        "magic": 100,
        "comment": "modifica ordine",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
        "ENUM_ORDER_STATE": mt5.ORDER_FILLING_RETURN,
    }

    order_result = mt5.order_send(request)
    print(order_result)
    print()

    return order_result

init()
OnTick()