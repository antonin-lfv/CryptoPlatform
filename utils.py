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
    "XTZ-USD",  # Tezos
    "XPM-USD",  # Primecoin
    "XAI-USD",  # XAI
    "STEEM-USD",  # Steem
    "SLS-USD",  # SaluS
    "OMG-USD",  # OMG Network
    "PPC-USD",  # Peercoin
    "KOBO-USD",  # Kobocoin
    "DMD-USD",  # Diamond
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
    "Tezos",
    "Primecoin",
    "SideShift Token",
    "Steem",
    "SaluS",
    "OMG Network",
    "Peercoin",
    "Kobocoin",
    "Diamond",
]

mini_wallet = 1000
bank_wallet = 10000

NFT_collections = [
    'Picasso', 'Cyberpunk', 'Greece', 'Cars', 'Futuristic-city',
    'Cats', 'Penguins', 'Cubes', 'Cyber-animals', 'Astronauts',
    'Fantastic-animals', 'Garden', 'Haunted-house', 'Historic-buildings',
    'Art', 'Nuketown', 'Space'
    ]
min_prix_NFT = 0.5
max_prix_NFT = 100
core_url_NFT = '/images/nft-item/'

number_most_valuable_cryptos = 6

user_profile_default_image_path = "images/avatar/avatar-1.png"

MAINTENANCE_MODE = False

# dict to get name from symbol
symbol_to_name = dict(zip(top_cryptos_symbols, top_cryptos_names))

# dict to get symbol from name
name_to_symbol = dict(zip(top_cryptos_names, top_cryptos_symbols))

# Max number of servers to be bought and rented
max_servers = 50


# ===== Functions
