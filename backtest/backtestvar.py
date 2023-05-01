N1 = 10 # ----- parametro indicatore channel length
N2 = 21 # ----- parametro indicatore average length
SYMBOL = "XAUUSD" # ----- simbolo stock
TIMEFRAME = "15m" # ----- timeframe (1m, 5m, 15m, 30m, 1h, 2h, 4h)
N_OPERAZIONI = 2 # ----- numero di operazioni da aprire quando arriva il signal
CHIUSURA_OPERAZIONI_BREAKEVEN = 50 # ----- numero di operazioni in percentuale da chiudere quando scatta il break even (50 = 50 %)
RISCHIO = 3 # ----- capitale di rischio per ogni operazione (per tutte le operazioni aperte in un signal) (0.5 = 0.5 %)
STOPLOSS = 50 # ----- pips di stop loss iniziale
SPOSTAMENTO_STOPLOSS = 3 # ----- quando il prezzo sale di +40 pips sposto il take profit a +20 pips
BREAK_EVEN = 75 # ----- quando il prezzo sale di 15 pips dal prezzo di apertura metto a brake even
GETDATA = 2000 # ----- numero di candele passate sul quale calcolare l'indicatore
BALANCE = 9760 # ----- bilancio iniziale del conto
DEBUG = False # ----- attivare debug (False , True)
DATESTART = "24/04/23 00:00" # ----- data di inizio backtesting
DATEEND = "01/05/23 23:00" # ----- data di fine backtesting
INCERTEZZA = 4
GOAL = 0
LOSE = 10