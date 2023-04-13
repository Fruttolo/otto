import MetaTrader5 as mt5
import os
from termcolor import colored

SPOSTAMENTO_STOPLOSS = 20 # pips di spostamento dello stop loss

def modify_order(pos,dir):
    
    if(dir == 'up'):
        stopLoss = pos.sl + (SPOSTAMENTO_STOPLOSS / 10)
    else:
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
        "comment": "python close order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
        "ENUM_ORDER_STATE": mt5.ORDER_FILLING_RETURN,
    }

    order_result = mt5.order_send(request)
    print(order_result)
    print()

    return order_result



def pips(a,b):
    return abs(a-b)*20

mt5.initialize()
os.system("CLS")

while True:
    positions =  mt5.positions_get()

    #market_order('XAUUSD',0.5,'buy')

    for pos in positions :
        if(pips(pos.sl,pos.price_current)>=(SPOSTAMENTO_STOPLOSS * 2)):
            if pos.type == 0:
                modify_order(pos,'up')
            else:
                modify_order(pos,'down')
        



        
        
        
    
    
#TRADE_ACTION_SLTP