import MetaTrader5 as mt5

def pips(a,b):
    return abs(a-b)

mt5.initialize()

positions =  mt5.positions_get()
for pos in positions :
    print(pos)
    if(pips(pos.sl,pos.price_current)>=20):
        print('da spostare')
        
        
    
    
#TRADE_ACTION_SLTP