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
    'Art', 'Nuketown', 'Space', 'ethereal-swirls', 'floating-islands', 'frogs',
    'lights', 'playmobs', 'rebel-rootz'
]

min_prix_common_NFT = 0.5
max_prix_common_NFT = 5
min_prix_rare_NFT = 2
max_prix_rare_NFT = 40
min_prix_epic_NFT = 20
max_prix_epic_NFT = 100
min_prix_legendary_NFT = 90
max_prix_legendary_NFT = 200

common_collection = ['Cars', 'Garden', 'Cubes', 'floating-islands', 'frogs']
rare_collection = ['Picasso', 'Cyberpunk', 'Greece', 'Cats', 'Haunted-houses', 'Historic-buildings', 'Art',
                   'lights', 'playmobs']
epic_collection = ['Futuristic-city', 'Penguins', 'Cyber-animals', 'Astronauts', 'ethereal-swirls']
legendary_collection = ['Fantastic-animals', 'Nuketown', 'Space', 'rebel-rootz']

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
    'ethereal-swirls': (min_prix_epic_NFT, max_prix_epic_NFT),
    'floating-islands': (min_prix_common_NFT, max_prix_common_NFT),
    'frogs': (min_prix_common_NFT, max_prix_common_NFT),
    'lights': (min_prix_rare_NFT, max_prix_rare_NFT),
    'playmobs': (min_prix_rare_NFT, max_prix_rare_NFT),
    'rebel-rootz': (min_prix_legendary_NFT, max_prix_legendary_NFT)
}

core_url_NFT = '/images/nft-item/'

number_most_valuable_cryptos = 6

user_profile_default_image_path = "images/avatar/avatar-1.png"

# dict to get name from symbol
symbol_to_name = dict(zip(top_cryptos_symbols, top_cryptos_names))

# dict to get symbol from name
name_to_symbol = dict(zip(top_cryptos_names, top_cryptos_symbols))

# Max number of servers to be bought and rented
max_servers = 50

# User bonus on mining servers
steps = [2, 4, 8, 12, 16, 32, 64, 128, 256, 512, 1024, 2048]
steps_bonus = [0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1, 1.5, 2, 3]

# Quests steps
NFTs_bought_steps = [1] + [i for i in range(5, 101, 5)] + [i for i in range(105, 306, 20)]
NFTs_sold_steps = [1] + [i for i in range(5, 101, 5)] + [i for i in range(105, 306, 20)]
NFTs_bid_steps = [1] + [i for i in range(5, 101, 5)] + [i for i in range(105, 306, 20)]
Servers_bought_steps = [1] + [i for i in range(5, 200, 15)] + [i for i in range(200, 740, 30)]


# reward is 0.05 * index of the step BTC


# ===== Functions


def get_bonus_from_BTC_wallet(BTC_wallet_value):
    for btc, bonus in zip(steps[::-1], [steps_bonus[-1]] + steps_bonus[::-1]):
        if BTC_wallet_value >= btc:
            return bonus
    return 0


def get_current_quest_step(nft_bougth, nft_sold, nft_bid, servers_bought):
    """
    Return the current step of the quest (index of the list of steps)
    /!\ each of the four quests categories has 32 steps
    To go to the next step, the user must have completed the current step and validate a button to get the reward

    To get the number of BTC to be rewarded, the index of the step is used (0.05 * (index + 1)  of the step BTC)
    """
    index_nft_bougth = 31
    index_nft_sold = 31
    index_nft_bid = 31
    index_servers_bought = 31
    for i, step in enumerate(NFTs_bought_steps):
        if nft_bougth < step:
            index_nft_bougth = i - 1
            break
    for i, step in enumerate(NFTs_sold_steps):
        if nft_sold < step:
            index_nft_sold = i - 1
            break
    for i, step in enumerate(NFTs_bid_steps):
        if nft_bid < step:
            index_nft_bid = i - 1
            break
    for i, step in enumerate(Servers_bought_steps):
        if servers_bought < step:
            index_servers_bought = i - 1
            break

    return index_nft_bougth, index_nft_sold, index_nft_bid, index_servers_bought
