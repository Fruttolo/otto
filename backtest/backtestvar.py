N1 = 10 # ----- parametro indicatore channel length
N2 = 21 # ----- parametro indicatore average length
SYMBOL = "XAUEUR" # ----- simbolo stock
TIMEFRAME = "15m" # ----- timeframe (1m, 5m, 15m, 30m, 1h, 2h, 4h)
N_OPERAZIONI = 2 # ----- numero di operazioni da aprire quando arriva il signal
CHIUSURA_OPERAZIONI_BREAKEVEN = 50 # ----- numero di operazioni in percentuale da chiudere quando scatta il break even (50 = 50 %)
RISCHIO = 3 # ----- capitale di rischio per ogni operazione (per tutte le operazioni aperte in un signal) (0.5 = 0.5 %)
STOPLOSS = 30 # ----- pips di stop loss iniziale
SPOSTAMENTO_STOPLOSS = 25 # ----- quando il prezzo sale di +40 pips sposto il take profit a +20 pips
BREAK_EVEN = 30 # ----- quando il prezzo sale di 15 pips dal prezzo di apertura metto a brake even
GETDATA = 1000 # ----- numero di candele passate sul quale calcolare l'indicatore
BALANCE = 200 # ----- bilancio iniziale del conto
DEBUG = False # ----- attivare debug (False , True)
DATESTART = "10/04/23 07:00" # ----- data di inizio backtesting
DATEEND = "14/04/23 20:00" # ----- data di inizio backtesting