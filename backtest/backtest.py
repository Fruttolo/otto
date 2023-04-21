import os
from datetime import datetime
from termcolor import colored
import MetaTrader5 as mt5
from backtestvar import *
import math

class trade_position :
    
    order_keys = 0
    winning_orders = 0
    zero_order = 0
    
    def __init__(self, symbol, volume, type, open_price, sl, tp):
        self.ticket = trade_position.order_keys
        self.symbol = symbol
        self.volume = volume
        self.type = type
        self.open_price = open_price
        self.sl = sl
        self.tp = tp
    
    def __str__(self):
        return "{ "+str(self.ticket)+" "+self.symbol+" "+str(self.volume)+" "+str(self.type)+" "+str(self.open_price)+" "+str(self.sl)+" "+str(self.tp)+" }"


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
    
def stamp(t_frame) :
    if t_frame == '1m' :
        return 60
    elif t_frame == '5m':
        return 60*5 
    elif t_frame == '15m':
        return 60*15 
    elif t_frame == '30m':
        return 60*30 
    elif t_frame == '1h':
        return 60*60 
    elif t_frame == '2h':
        return 60*60*2 
    elif t_frame == '4h':
        return 60*60*4 
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
    print('--- CANDLE ---',len(close)-GETDATA+1)
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
    
def order_send(order):
    if balance <= 0 :
        raise Exception("Bilancio non sufficente per completare l'operazione")
    for i in range(len(openTrade)) :
        if openTrade[i].ticket == order.ticket :
            openTrade[i] = order
            print(order)
            return "ordine modificato :" + str(order.ticket)
    openTrade.append(order)
    trade_position.order_keys = trade_position.order_keys + 1
    return order
    
def market_order(symbol, order_type, tp):
    order_dict = {'buy': 0, 'sell': 1}
    price_dict = {'buy': lastElement(close), 'sell': lastElement(close)}
    
    if(order_type == 'buy'):
        stopLoss = price_dict[order_type] - (STOPLOSS / 10)
    else:
        stopLoss = price_dict[order_type] + (STOPLOSS / 10)
    
    takeProfit = 0
    if tp :
        if order_type == 'buy' :
            takeProfit = (price_dict[order_type] + (BREAK_EVEN / 10))
        else :
            takeProfit = (price_dict[order_type] - (BREAK_EVEN / 10))
            
    request = trade_position(
        symbol,
        VOLUME,
        order_dict[order_type],
        price_dict[order_type],
        stopLoss,
        takeProfit
    )

    order_result = order_send(request)
    print(order_result)

def modify_order(pos,dir):
    
    if(dir == 'up'):
        if pos.sl < pos.open_price :
            stopLoss = pos.open_price + 0.1
        else :
            stopLoss = pos.sl + (SPOSTAMENTO_STOPLOSS / 10)
    else:
        if pos.sl > pos.open_price :
            stopLoss = pos.open_price - 0.1
        else :
            stopLoss = pos.sl - (SPOSTAMENTO_STOPLOSS / 10)
    
    pos.sl = stopLoss

    order_result = order_send(pos)
    print(order_result)
    print()
    if DEBUG :
        os.system('pause')
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
    if DEBUG :
        os.system('pause')
        print()
    
def calculate_risk(b):
    return  ((((b/100)*RISCHIO)/(STOPLOSS/10))/N_OPERAZIONI) / 100

def close_order(pos,price) :    
    profit=mt5.order_calc_profit(pos.type,pos.symbol,pos.volume,pos.open_price,price)
    
    if profit > 0 :
        trade_position.winning_orders = trade_position.winning_orders + 1
    if profit == 0 :
        trade_position.zero_order = trade_position.zero_order + 1
    
    global balance
    balance = balance + profit
    
    if balance < 0 :
        raise Exception('NON HAI PIU SOLDI !!')
    
    print("ordine chiuso :",pos.ticket)
    print()
    openTrade.remove(pos)
    if DEBUG :
        os.system('pause')
        print()

def detailed_check(pos, timestamp) :
    ticks = mt5.copy_ticks_range(SYMBOL, int(timestamp), int(timestamp+stamp(TIMEFRAME)), mt5.COPY_TICKS_INFO)
    
    for tick in ticks[:-1] :
        if pos.type :
            # SELL
            if pos.tp != 0 :
                # HA TAKE PROFIT
                if tick[2] <= pos.tp :
                    # TP
                    close_order(pos, pos.tp)
                    return
                if tick[2] >= pos.sl :
                    # SL
                    close_order(pos, pos.sl)
                    return
            else :
                # NON HA TP
                if pos.sl > pos.open_price :
                    # NON HA ANCORA RAGGIUNTO BE
                    if tick[2] <= pos.open_price - (BREAK_EVEN / 10) :
                        # ONLY BE
                        modify_order(pos, 'down')
                    if tick[2] >= pos.sl :
                        # ONLY SL
                        close_order(pos, pos.sl)
                        return
                else:
                    # HA GIA RAGGIUNTO BE
                    if tick[2] <= pos.sl - (SPOSTAMENTO_STOPLOSS / 10)*2 :
                        # ONLY BE
                        modify_order(pos, 'down')
                    if tick[2] >= pos.sl :
                        # ONLY SL
                        close_order(pos, pos.sl)
                        return
                
        else :
            # BUY
            if pos.tp != 0 :
                # HA TAKE PROFIT
                if tick[1] >= pos.tp :
                    # TP
                    close_order(pos, pos.tp)
                    return
                if tick[1] <= pos.sl :
                    # SL
                    close_order(pos, pos.sl)
                    return
            else :
                # NON HA TP
                if pos.sl < pos.open_price :
                    # NON HA ANCORA RAGGIUNTO BE
                    if tick[1] >= pos.open_price + (BREAK_EVEN / 10) :
                        # ONLY BE
                        modify_order(pos, 'up')
                    if tick[1] <= pos.sl :
                        # ONLY SL
                        close_order(pos, pos.sl)
                        return
                else:
                    # HA GIA RAGGIUNTO BE
                    if tick[1] >= pos.sl + (SPOSTAMENTO_STOPLOSS / 10)*2 :
                        # ONLY BE
                        modify_order(pos, 'up')
                    if tick[1] <= pos.sl :
                        # ONLY SL
                        close_order(pos, pos.sl)
                        return

mt5.initialize()
os.system("CLS")

print('--- BACKTEST ---',TIMEFRAME)
print()

#start = datetime.strptime(input('Imposta data di inizio ( gg/mm/aa hh:mm ) : '), '%d/%m/%y %H:%M')
#end = datetime.strptime(input('Imposta data di fine ( gg/mm/aa hh:mm ) : '), '%d/%m/%y %H:%M')
start = datetime.strptime(DATESTART, '%d/%m/%y %H:%M')
end = datetime.strptime(DATEEND, '%d/%m/%y %H:%M')
print()


utc_to =datetime.timestamp(end)
utc_from =datetime.timestamp(start)
utc_to = utc_to + 10800
utc_from = utc_from + 10800

rates = mt5.copy_rates_range(SYMBOL, timeframe(TIMEFRAME), utc_from, utc_to)
init = mt5.copy_rates_from(SYMBOL, timeframe(TIMEFRAME), utc_from, GETDATA)

close = []
ema = []
hlc3 = []
esa = []
d = []
tci = []
wt2 = []
openTrade = []

global balance
balance = BALANCE

for candle in init[:-1] :
        calculate_indicator(candle[4],candle[2],candle[3])

for candle in rates :
    
    # MODIFICO ORDINI
    for pos in openTrade :
        if pos.type :
            # SELL
            if pos.tp != 0 :
                # HA TAKE PROFIT
                if candle[2] < pos.sl and candle[3] >= pos.tp :
                    # ONLY TP
                    close_order(pos, pos.tp)
                if candle[2] >= pos.sl and candle[3] > pos.tp :
                    # ONLY SL
                    close_order(pos, pos.sl)
                if candle[2] >= pos.sl and candle[3] <= pos.tp :
                    # BOTH
                    detailed_check(pos, candle[0])
            else :
                # NON HA TP
                if pos.sl > pos.open_price :
                    # NON HA ANCORA RAGGIUNTO BE
                    if candle[2] < pos.sl and candle[3] >= pos.open_price - (BREAK_EVEN / 10) :
                        # ONLY BE
                        modify_order(pos, 'down')
                    if candle[2] >= pos.sl and candle[3] > pos.open_price - (BREAK_EVEN / 10) :
                        # ONLY SL
                        close_order(pos, pos.sl)
                    if candle[2] >= pos.sl and candle[3] <= pos.open_price - (BREAK_EVEN / 10) :
                        # BOTH
                        detailed_check(pos, candle[0])
                else:
                    # HA GIA RAGGIUNTO BE
                    if candle[2] < pos.sl and candle[3] >= pos.sl - (SPOSTAMENTO_STOPLOSS / 10)*2 :
                        # ONLY BE
                        modify_order(pos, 'down')
                    if candle[2] >= pos.sl and candle[3] > pos.sl - (SPOSTAMENTO_STOPLOSS / 10)*2 :
                        # ONLY SL
                        close_order(pos, pos.sl)
                    if candle[2] >= pos.sl and candle[3] <= pos.sl - (SPOSTAMENTO_STOPLOSS / 10)*2 :
                        # BOTH
                        detailed_check(pos, candle[0])
                
        else :
            # BUY
            if pos.tp != 0 :
                # HA TAKE PROFIT
                if candle[2] >= pos.tp and candle[3] > pos.sl :
                    # ONLY TP
                    close_order(pos, pos.tp)
                if candle[2] < pos.tp and candle[3] <= pos.sl :
                    # ONLY SL
                    close_order(pos, pos.sl)
                if candle[2] >= pos.tp and candle[3] <= pos.sl :
                    # BOTH
                    detailed_check(pos, candle[0])
            else :
                # NON HA TP
                if pos.sl < pos.open_price :
                    # NON HA ANCORA RAGGIUNTO BE
                    if candle[2] >= pos.open_price + (BREAK_EVEN / 10) and candle[3] > pos.sl :
                        # ONLY BE
                        modify_order(pos, 'up')
                    if candle[2] < pos.open_price + (BREAK_EVEN / 10) and candle[3] <= pos.sl :
                        # ONLY SL
                        close_order(pos, pos.sl)
                    if candle[2] >= pos.open_price + (BREAK_EVEN / 10) and candle[3] <= pos.sl :
                        # BOTH
                        detailed_check(pos, candle[0])
                else:
                    # HA GIA RAGGIUNTO BE
                    if candle[2] >= pos.sl + (SPOSTAMENTO_STOPLOSS / 10)*2 and candle[3] > pos.sl :
                        # ONLY S_SL
                        modify_order(pos, 'up')
                    if candle[2] < pos.sl + (SPOSTAMENTO_STOPLOSS / 10)*2 and candle[3] <= pos.sl :
                        # ONLY SL
                        close_order(pos, pos.sl)
                    if candle[2] >= pos.sl + (SPOSTAMENTO_STOPLOSS / 10)*2 and candle[3] <= pos.sl :
                        # BOTH
                        detailed_check(pos, candle[0])
    
    calculate_indicator(candle[4],candle[2],candle[3])
    print_candle()
    
    # CALCOLO PALLINO LINEA
    pallino = lastElement(wt2)
    linea = lastElement(tci)
    lastPallino = lastElement(wt2,2)
    lastLinea = lastElement(tci,2)
    
    VOLUME = round(calculate_risk(balance),2)
    
    # SIGNAL LOGIC
    if pallino > linea and lastPallino < lastLinea :
        trade('sell')
    elif pallino < linea  and lastPallino > lastLinea :
        trade('buy')

os.system('cls')

print()     
print('--- END BACKTEST ---',TIMEFRAME)
print()
print('-- OPEN TRADES --')
for i in openTrade :
    print(i)
print()

print('-- BALANCE --')
print('bilancio restante :',round(balance,2))
if balance < BALANCE :
    print('drowdown :',colored(round(balance - BALANCE,2),'red'))
else:
    print('profit :',colored(round(balance - BALANCE,2),'green'))
print()

print('-- WINRATE --')
print('ordini totali :',trade_position.order_keys)
print('ordini chiusi in positivo :',colored(trade_position.winning_orders,'green'))
print('ordini chiusi in negativo :',colored(trade_position.order_keys-trade_position.winning_orders-trade_position.zero_order,'red'))
print('ordini chiusi a zero :',colored(trade_position.zero_order,'white'))
print()
percent = (trade_position.winning_orders/trade_position.order_keys)*100
if percent > 50 :
    print('PERCENTUALE DI WINRATE :',colored(round(percent,2),'green'),'%')
else:
    print('PERCENTUALE DI WINRATE :',colored(round(percent,2),'red'),'%')
    
os.system('pause')