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
    'Fantastic-animals', 'Garden', 'Haunted-houses', 'Historic-buildings',
    'Art', 'Nuketown', 'Space'
    ]

min_prix_common_NFT = 0.5
max_prix_common_NFT = 5
min_prix_rare_NFT = 2
max_prix_rare_NFT = 40
min_prix_epic_NFT = 20
max_prix_epic_NFT = 100
min_prix_legendary_NFT = 90
max_prix_legendary_NFT = 200

common_collection = ['Cars', 'Garden', 'Cubes']
rare_collection = ['Picasso', 'Cyberpunk', 'Greece', 'Cats', 'Haunted-houses', 'Historic-buildings', 'Art']
epic_collection = ['Futuristic-city', 'Penguins', 'Cyber-animals', 'Astronauts']
legendary_collection = ['Fantastic-animals', 'Nuketown', 'Space']

# map collection to min and max price
collection_to_min_max_price = {
    'Cars': (min_prix_common_NFT, max_prix_common_NFT),
    'Garden': (min_prix_common_NFT, max_prix_common_NFT),
    'Cubes': (min_prix_common_NFT, max_prix_common_NFT),
    'Picasso': (min_prix_rare_NFT, max_prix_rare_NFT),
    'Cyberpunk': (min_prix_rare_NFT, max_prix_rare_NFT),
    'Greece': (min_prix_rare_NFT, max_prix_rare_NFT),
    'Cats': (min_prix_rare_NFT, max_prix_rare_NFT),
    'Haunted-houses': (min_prix_rare_NFT, max_prix_rare_NFT),
    'Historic-buildings': (min_prix_rare_NFT, max_prix_rare_NFT),
    'Art': (min_prix_rare_NFT, max_prix_rare_NFT),
    'Futuristic-city': (min_prix_epic_NFT, max_prix_epic_NFT),
    'Penguins': (min_prix_epic_NFT, max_prix_epic_NFT),
    'Cyber-animals': (min_prix_epic_NFT, max_prix_epic_NFT),
    'Astronauts': (min_prix_epic_NFT, max_prix_epic_NFT),
    'Fantastic-animals': (min_prix_legendary_NFT, max_prix_legendary_NFT),
    'Nuketown': (min_prix_legendary_NFT, max_prix_legendary_NFT),
    'Space': (min_prix_legendary_NFT, max_prix_legendary_NFT),
}

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

# User bonus on mining servers
steps = [2, 4, 8, 12, 16, 32, 64, 128, 256, 512, 1024, 2048]
steps_bonus = [0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1, 1.5, 2, 3]

# ===== Functions


def get_bonus_from_BTC_wallet(BTC_wallet_value):
    for btc, bonus in zip(steps[::-1], [steps_bonus[-1]]+steps_bonus[::-1]):
        if BTC_wallet_value >= btc:
            print(bonus)
            return bonus
    return 0
