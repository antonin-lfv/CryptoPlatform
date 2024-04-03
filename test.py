# test yahoo finance api
import yfinance as yf
from config import top_cryptos_symbols, top_cryptos_names

DATA = yf.download('BTC-USD', start='2021-01-01')
print(DATA.keys())

# count number of nan
print(DATA.isna().sum())
