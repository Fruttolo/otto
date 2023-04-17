import MetaTrader5 as mt5
import os
from termcolor import colored
from variabili import SPOSTAMENTO_STOPLOSS, BREAK_EVEN

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

mt5.initialize()
os.system("CLS")

print('-- NOVE -- ')
print()

while True:
    positions =  mt5.positions_get()

    for pos in positions :
        if pos.type == 0:
            if pos.sl < pos.price_open :
                if pos.price_current >= pos.price_open + (BREAK_EVEN / 10) :
                    modify_order(pos,'up')
            else :
                if pos.price_current >= pos.sl + (SPOSTAMENTO_STOPLOSS / 10)*2 :
                    modify_order(pos,'up')
        else :
            if pos.sl > pos.price_open :
                if pos.price_current <= pos.price_open - (BREAK_EVEN / 10) :
                    modify_order(pos,'down')
            else :
                if pos.price_current <= pos.sl - (SPOSTAMENTO_STOPLOSS / 10)*2 :
                    modify_order(pos,'down')
                    