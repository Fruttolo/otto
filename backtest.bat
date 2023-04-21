echo off
cls
pip install -r requirements.txt
cd backtest
start notepad backtestvar.py
cls
pause
start python backtest.py