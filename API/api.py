from flask import Blueprint, jsonify, session, request
from flask_login import login_required, current_user
from crypto_manager import CryptoDataManager
from wallet_manager import wallet_manager
from notification_manager import Notification_manager
from quests_manager import Quests_manager
from user_manager import UserManager
from nft_manager import NFT_manager
from mining_server_manager import Mining_server_manager
from models import User

BLP_api = Blueprint('BLP_api', __name__)


# Index
# ----------------
# User
# Crypto data
# NFT data
# Mining servers
# Wallet
# Buy crypto
# Notifications
# Quests
# General functions


# ================================
# User
# ================================
@BLP_api.route('/api/change_username', methods=['GET', 'POST'])
@login_required
def change_username():
    """
    Change the username of a user
    """
    new_username = request.form.get('new_username', '')
    response = UserManager().change_username(current_user.id, new_username)

    return jsonify(response)


@BLP_api.route('/api/is_user_notification_active', methods=['GET', 'POST'])
@login_required
def is_user_notification_active():
    """
    Check if the notifications are active for a user
    """
    response = UserManager().is_user_notification_active(current_user.id)
    return jsonify(response)


@BLP_api.route('/api/switch_notifications_active', methods=['GET', 'POST'])
@login_required
def switch_notifications_active():
    """
    Switch the notifications active status of a user
    """
    response = UserManager().switch_notifications_active(current_user.id)
    return jsonify(response)


# ================================
# Crypto data
# ================================
@BLP_api.route('/api/get_specific_crypto_data/<symbol>', methods=['GET', 'POST'])
@login_required
def get_specific_crypto_data(symbol):
    # Get crypto data for specific symbol
    crypto_manager = CryptoDataManager()
    symbol_data = crypto_manager.get_specific_crypto_data(symbol)
    # symbol data looks like this:
    # {
    #   'date': [datetime.datetime(2021, 9, 30, 0, 0), datetime.datetime(2021, 10, 1, 0, 0), ...],
    #   'price': [465.864013671875, 456.8599853515625, ...]
    # }
    # Convert dates to isoformat
    formatted_dates = [date.isoformat() for date in symbol_data['date']]
    symbol_data['date'] = formatted_dates
    return jsonify(symbol_data)


@BLP_api.route('/api/get_all_crypto_data', methods=['GET', 'POST'])
@login_required
def get_all_crypto_data():
    crypto_manager = CryptoDataManager()
    data = crypto_manager.get_all_crypto_data()
    return data


@BLP_api.route('/api/get_USD_from_crypto/<symbol>/<quantity>', methods=['GET', 'POST'])
@login_required
def get_USD_from_crypto(symbol, quantity):
    """
    Get the USD value of a quantity of a specific crypto.

    Return:
        float
    """
    data = CryptoDataManager().get_USD_from_crypto(symbol, quantity)
    return jsonify(data)


@BLP_api.route('/api/get_crypto_from_USD/<symbol>/<USD>', methods=['GET', 'POST'])
@login_required
def get_crypto_from_USD(symbol, USD):
    """
    Get the quantity of a specific crypto from a USD amount.

    Return:
        float
    """
    data = CryptoDataManager().get_crypto_from_USD(symbol, USD)
    return jsonify(data)


@BLP_api.route('/api/get_crypto_from_crypto/<symbol_from>/<symbol_to>/<quantity>', methods=['GET', 'POST'])
@login_required
def get_crypto_from_crypto(symbol_from, symbol_to, quantity):
    """
    Get the quantity of a specific crypto from a USD amount.

    Return:
        float
    """
    data = CryptoDataManager().get_crypto_from_crypto(symbol_from, symbol_to, quantity)
    return jsonify(data)


@BLP_api.route('/api/buy_with_crypto', methods=['GET', 'POST'])
@login_required
def buy_with_crypto():
    """
    Buy a crypto with another crypto
    """
    symbol = request.args.get('symbol', '')
    quantity = request.args.get('quantity', '')
    response = wallet_manager().buy_with_crypto(current_user, symbol, quantity)
    return jsonify(response)


@BLP_api.route('/api/send_BTC_to_user/<user_id>', methods=['GET', 'POST'])
@login_required
def send_BTC_to_user(user_id):
    """
    ADMIN ONLY
    Send BTC to a user
    """
    user = User.query.filter_by(id=user_id).first()
    response = wallet_manager().receive_crypto(user, 'BTC-USD', 1)
    return jsonify(response)


# ================================
# NFT data
# ================================

@BLP_api.route('/api/refresh_NFT_base', methods=['GET', 'POST'])
@login_required
def refresh_NFT_base():
    """
    ADMIN ONLY
    Refresh the NFT base
    """
    refresh = NFT_manager().refresh_NFT_base(current_user.id)
    return jsonify(refresh)


@BLP_api.route('/api/get_NFT_marketplace', methods=['GET', 'POST'])
@BLP_api.route('/api/get_NFT_marketplace/<collection>', methods=['GET', 'POST'])
@login_required
def get_NFT_marketplace(collection=None):
    """
    Get all NFTs from the marketplace
    """
    NFTs = NFT_manager().get_NFTs(current_user.id, collection=collection)
    return jsonify(NFTs)


@BLP_api.route('/api/get_collection_details/<collection>', methods=['GET', 'POST'])
@login_required
def get_collection_details(collection):
    """
    Get details of an NFT collection
    """
    collection_details = NFT_manager().get_collection_details(collection)
    return jsonify(collection_details)


@BLP_api.route('/api/get_NFT_collections_preview/<collection>/<nft_id>', methods=['GET', 'POST'])
@login_required
def get_NFT_collections_preview(collection, nft_id):
    """
    Get all NFT collections preview
    """
    collections = NFT_manager().get_NFTS_preview(collection, nft_id)
    return jsonify(collections)


@BLP_api.route('/api/get_liked_NFTs', methods=['GET', 'POST'])
@login_required
def get_liked_NFTs():
    """
    Get all NFTs liked by the user
    """
    liked_NFTs = NFT_manager().get_liked_NFTs(current_user.id)
    return jsonify(liked_NFTs)


@BLP_api.route('/api/get_owned_NFTs', methods=['GET', 'POST'])
@login_required
def get_owned_NFTs():
    """
    Get all NFTs owned by the user
    """
    owned_NFTs = NFT_manager().get_owned_NFTs(current_user.id)
    return jsonify(owned_NFTs)


@BLP_api.route('/api/get_bids_NFTs', methods=['GET', 'POST'])
@login_required
def get_bids_NFTs():
    """
    Get all NFTs on which the user has placed a bid
    """
    bids_NFTs = NFT_manager().get_bids_NFTs(current_user.id)
    return jsonify(bids_NFTs)


@BLP_api.route('/api/get_user_NFTs/<user_id>', methods=['GET', 'POST'])
@login_required
def get_user_NFTs(user_id):
    """
    Get all NFTs of a specific user
    """
    NFTs = NFT_manager().get_user_NFTs(user_id, current_user.id)
    return jsonify(NFTs)


@BLP_api.route('/api/like_NFT/<nft_id>', methods=['GET', 'POST'])
@login_required
def like_NFT(nft_id):
    """
    Like an NFT
    """
    response = NFT_manager().like_NFT(current_user.id, nft_id)
    return jsonify(response)


@BLP_api.route('/api/buy_NFT/<nft_id>', methods=['GET', 'POST'])
@login_required
def buy_NFT(nft_id):
    """
    Buy an NFT
    """
    response = NFT_manager().buy_NFT(current_user.id, nft_id)
    return jsonify(response)


@BLP_api.route('/api/owned_status/<nft_id>', methods=['GET', 'POST'])
@login_required
def owned_status(nft_id):
    """
    Get the owned status of an NFT
    """
    response = NFT_manager().owned_status(current_user.id, nft_id)
    return jsonify(response)


@BLP_api.route('/api/get_NFT_details/<nft_id>', methods=['GET', 'POST'])
@login_required
def get_NFT_details(nft_id):
    """
    Get details of an NFT
    """
    response = NFT_manager().get_NFT(nft_id, current_user.id)
    return jsonify(response)


@BLP_api.route('/api/get_NFT_history/<nft_id>', methods=['GET', 'POST'])
@login_required
def get_NFT_history(nft_id):
    """
    Get history of an NFT
    """
    history = NFT_manager().get_NFT_history(nft_id)
    return jsonify(history)


@BLP_api.route('/api/set_as_profile_picture/<nft_id>', methods=['GET', 'POST'])
@login_required
def set_as_profile_picture(nft_id):
    """
    Set an NFT as profile picture
    """
    response = NFT_manager().set_as_profile_picture(current_user.id, nft_id)
    return jsonify(response)


@BLP_api.route('/api/get_bids/<nft_id>', methods=['GET', 'POST'])
@login_required
def get_bids(nft_id):
    """
    Get all bids for an NFT
    """
    bids = NFT_manager().get_bids(nft_id)
    return jsonify(bids)


@BLP_api.route('/api/place_bid/<nft_id>', methods=['POST'])
@login_required
def place_bid(nft_id):
    """
    Place a bid on an NFT
    """
    data = request.json
    bid_amount = data.get('bid_amount')
    if bid_amount is None:
        return jsonify({"status": "error", "message": "No bid amount provided"})
    bid_amount = float(bid_amount)
    response = NFT_manager().place_bid(current_user.id, nft_id, bid_amount)
    return jsonify(response)


@BLP_api.route('/api/accept_bid/<bid_id>', methods=['GET', 'POST'])
@login_required
def accept_bid(bid_id):
    """
    Accept a bid on an NFT
    """
    response = NFT_manager().accept_bid(bid_id, current_user.id)
    return jsonify(response)


@BLP_api.route('/api/delete_bid/<bid_id>', methods=['GET', 'POST'])
@login_required
def delete_bid(bid_id):
    """
    Delete a bid on an NFT
    """
    response = NFT_manager().delete_bid(bid_id, current_user.id)
    return jsonify(response)


@BLP_api.route('/api/increment_views/<nft_id>', methods=['GET', 'POST'])
@login_required
def increment_views(nft_id):
    """
    Increment the views of an NFT
    """
    response = NFT_manager().increment_views(nft_id)
    return jsonify(response)


# ================================
# Mining servers
# ================================


@BLP_api.route('/api/restart_mining_servers_price', methods=['GET', 'POST'])
@login_required
def restart_mining_servers_price():
    """
    ADMIN ONLY
    Restart the mining servers price
    """
    response = Mining_server_manager().restart_mining_servers_price(current_user.id)
    return jsonify(response)


@BLP_api.route('/api/get_all_mining_servers', methods=['GET', 'POST'])
@login_required
def get_all_mining_servers():
    """
    Get all mining servers from the database
    """
    servers = Mining_server_manager().get_all_servers(current_user.id)
    return jsonify(servers)


@BLP_api.route('/api/get_user_mining_server_details/<server_id>/<user_id>', methods=['GET', 'POST'])
@login_required
def get_user_mining_server_details(server_id, user_id):
    """
    Get details of a mining server for a specific user (He can have multiple servers)

    Fields:
    - number_of_servers_bought
    - number_of_servers_rented
    - total_buy_amount
    - total_rent_amount_per_day
    - total_maintenance_cost_per_day (bought servers only)
    """
    server_details = Mining_server_manager().get_user_mining_server_details(server_id, user_id)
    return jsonify(server_details)


@BLP_api.route('/api/buy_mining_server/<server_id>/<user_id>/<number_of_servers_to_buy>', methods=['GET', 'POST'])
@login_required
def buy_mining_server(server_id, user_id, number_of_servers_to_buy):
    """
    Buy a mining server
    """
    response = Mining_server_manager().buy_server(server_id, user_id, number_of_servers_to_buy)
    # Payment process for servers
    mining_server_manager = Mining_server_manager()
    mining_server_manager.check_for_server_payment(current_user.id)
    return jsonify(response)


@BLP_api.route('/api/sell_mining_server/<server_id>/<user_id>/<number_of_servers_to_sell>', methods=['GET', 'POST'])
@login_required
def sell_mining_server(server_id, user_id, number_of_servers_to_sell):
    """
    Sell a mining server
    """
    response = Mining_server_manager().sell_server(server_id, user_id, number_of_servers_to_sell)
    return jsonify(response)


@BLP_api.route('/api/get_user_mining_servers_invoices/<server_name>', methods=['GET', 'POST'])
@login_required
def get_user_mining_servers_invoices(server_name):
    """
    Get invoices for all mining servers of the user
    """
    invoices = Mining_server_manager().get_user_mining_servers_invoices(current_user, server_name)
    return jsonify(invoices)


# ================================
# Wallet
# ================================

@BLP_api.route('/api/get_user_balance', methods=['GET', 'POST'])
@login_required
def get_user_balance():
    """
    Get user balance. (crypto + web3)
    """
    user_balance = wallet_manager().get_user_balance(current_user)
    return jsonify(user_balance)


@BLP_api.route('/api/get_user_specific_balance/<symbol>', methods=['GET', 'POST'])
@login_required
def get_user_specific_balance(symbol):
    """
    Get user balance for a specific crypto
    """
    user_balance = wallet_manager().get_user_specific_balance(current_user, symbol)
    return jsonify(user_balance)


@BLP_api.route('/api/get_game_wallet', methods=['GET', 'POST'])
@login_required
def get_game_wallet():
    """
    Get game wallet of user
    """
    game_wallet = wallet_manager().get_game_wallet(current_user)
    return jsonify(game_wallet)


@BLP_api.route('/api/get_wallet_crypto_transactions_history', methods=['GET', 'POST'])
@login_required
def get_wallet_crypto_transactions_history():
    """
    Get wallet history of user
    """
    wallet_history = wallet_manager().get_wallet_crypto_transactions_history(current_user)
    return jsonify(wallet_history)


@BLP_api.route('/api/get_crypto_wallet_evolution', methods=['GET', 'POST'])
@login_required
def get_crypto_wallet_evolution():
    """
    Get wallet evolution of user
    """
    wallet_evolution = wallet_manager().get_crypto_wallet_evolution(current_user)
    wallet_daily_snapshot = wallet_manager().get_crypto_wallet_daily_snapshot(current_user)
    return jsonify(wallet_evolution, wallet_daily_snapshot)


# ================================
# Buy crypto
# ================================

@BLP_api.route('/api/buy_crypto_with_USD/<symbol>/<From>/<quantity>/<quantity_type>', methods=['GET', 'POST'])
@login_required
def buy_crypto_with_USD(symbol, From, quantity, quantity_type):
    """
    Buy crypto with USD

    Parameters:
        symbol: str
            Symbol of the crypto to buy
        From: str
            'mini_wallet' or 'bank_wallet'
        quantity: float
            Quantity of crypto to buy (usd or crypto depending on quantity_type)
        quantity_type: str
            'crypto' or 'USD'
    """
    assert quantity_type in ['crypto', 'USD']
    if quantity_type == 'crypto':
        response = wallet_manager().buy_crypto_with_USD(current_user, symbol, From, quantity_crypto=quantity)
    else:
        response = wallet_manager().buy_crypto_with_USD(current_user, symbol, From, quantity_USD=quantity)
    return jsonify(response)


@BLP_api.route('/api/buy_crypto_with_crypto/<symbol_to_sell>/<symbol_to_buy>/<quantity>/<action_on_quantity>',
               methods=['GET', 'POST'])
@login_required
def buy_crypto_with_crypto(symbol_to_sell, symbol_to_buy, quantity, action_on_quantity):
    """
    Parameters:
        symbol_to_sell: str
            Symbol of the crypto to sell
        symbol_to_buy: str
            Symbol of the crypto to buy
        quantity: float
            Quantity of crypto
        action_on_quantity: str
            'sell' or 'buy', if 'sell' then quantity is the quantity of crypto to sell, if 'buy' then quantity is the
            quantity of crypto to buy
    """
    assert action_on_quantity in ['sell', 'buy']
    if action_on_quantity == 'sell':
        response = wallet_manager().buy_crypto_with_crypto(current_user, symbol_to_sell,
                                                           symbol_to_buy, quantity_to_sell=quantity)
    else:
        response = wallet_manager().buy_crypto_with_crypto(current_user, symbol_to_sell,
                                                           symbol_to_buy, quantity_to_buy=quantity)
    return jsonify(response)


# ================================
# Notifications
# ================================


@BLP_api.route('/api/get_notifications', methods=['GET', 'POST'])
@login_required
def get_notifications():
    """
    Get all notifications of the user
    """
    notifications = Notification_manager().get_notifications(current_user)
    if not notifications:
        notifications = []
    return jsonify(notifications)


@BLP_api.route('/api/add_notification', methods=['GET', 'POST'])
@login_required
def add_notification():
    """
    Add a notification to the database
    """
    text = request.args.get('text', '')
    icon = request.args.get('icon', 'user')
    Notification_manager().add_notification(current_user.id, text, icon)
    return {'status': 'success'}


@BLP_api.route('/api/delete_all_notifications', methods=['GET', 'POST'])
@login_required
def delete_all_notifications():
    """
    Delete all notifications from the database
    """
    Notification_manager().delete_all_notifications(current_user)
    return {'status': 'success'}


@BLP_api.route('/api/send_notification_to_all_users', methods=['GET', 'POST'])
@login_required
def send_notification_to_all_users():
    """
    Send a notification to all users
    """
    text = request.args.get('text', '')
    print(f"Sending notification to all users: {text}")
    Notification_manager().send_notification_to_all_users(text, 'user')
    return {'status': 'success'}


# ================================
# Quests
# ================================

@BLP_api.route('/api/recover_quest', methods=['GET', 'POST'])
@login_required
def recover_quest():
    """
    Recover the quest of the user
    """
    step = request.args.get('step')
    quest_type = request.args.get('quest_type')
    response = Quests_manager().recover_quest(current_user.id, step, quest_type)
    return jsonify(response)


# ================================
# General functions
# ================================

@BLP_api.route('/set_theme')
def set_theme():
    theme = request.args.get('theme', 'light')
    session['theme'] = theme
    return '', 204
