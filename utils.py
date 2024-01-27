# ===== Constants
top_cryptos_symbols = [
    "BTC-USD",  # Bitcoin
    "ETH-USD",  # Ethereum
    "LTC-USD",  # Litecoin
    "USDT-USD",  # Tether
    "ADA-USD",  # Cardano
    "XRP-USD",  # XRP
    "DOGE-USD",  # Dogecoin
    "QTUM-USD",  # Qtum
    "BAT-USD",  # Basic Attention Token
    "NEO-USD",  # NEO
]
top_cryptos_names = [
    "Bitcoin",
    "Ethereum",
    "Litecoin",
    "Tether",
    "Cardano",
    "XRP",
    "Dogecoin",
    "Qtum",
    "Basic Attention Token",
    "NEO",
]

mini_wallet = 1000
bank_wallet = 10000

NFT_collections = ['Cyberpunk', 'Greece', 'Cars', 'Cats', 'Picasso', 'Penguins', 'Cubes']

# dict to get name from symbol
symbol_to_name = dict(zip(top_cryptos_symbols, top_cryptos_names))

# dict to get symbol from name
name_to_symbol = dict(zip(top_cryptos_names, top_cryptos_symbols))

# Max number of servers to be bought and rented
max_servers_bought = 50
max_servers_rented = 50


# ===== Functions
