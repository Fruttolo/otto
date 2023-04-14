import MetaTrader5 as mt5
import os
import time

def wait_min(minutes):
    time.sleep(1)
    if minutes == 1 :
        s = time.localtime().tm_sec
        while s != 00 :
            time.sleep(1)
            s = time.localtime().tm_sec
    elif minutes > 1 and minutes < 59 :
        s = time.localtime().tm_sec
        m = time.localtime().tm_min
        while s != 00 or  m%minutes != 0:
            print('sec:',s)
            print('min:',m)
            time.sleep(1)
            s = time.localtime().tm_sec
            m = time.localtime().tm_min
    elif minutes > 59 and minutes < 60*24 :
        s = time.localtime().tm_sec
        m = time.localtime().tm_min
        h = time.localtime().tm_hour
        while s != 00 or  m != 0 or h%(minutes/60)!=0 :
            time.sleep(1)
            s = time.localtime().tm_sec
            m = time.localtime().tm_min
            h = time.localtime().tm_hour
    else : 
        raise Exception("Timeframe not valid")

mt5.initialize()
os.system("CLS")

array = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_M15, 0, 10)
print(array)
for i in array[:-1] :
    print(i[4])
    wait_min(5)