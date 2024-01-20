from flask import Blueprint, jsonify, session, request
from flask_login import login_required, current_user
from crypto_manager import CryptoDataManager
from wallet_manager import wallet_manager
from notification_manager import Notification_manager
from nft_manager import NFT_manager
from mining_server_manager import Mining_server_manager

BLP_api = Blueprint('BLP_api', __name__)

# Index
# ----------------
# Crypto data
# NFT data
# Wallet
# Buy crypto
# Notifications
# General functions


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


# ================================
# NFT data
# ================================

@BLP_api.route('/api/get_NFT_marketplace', methods=['GET', 'POST'])
@BLP_api.route('/api/get_NFT_marketplace/<collection>', methods=['GET', 'POST'])
@login_required
def get_NFT_marketplace(collection=None):
    """
    Get all NFTs from the marketplace
    """
    NFTs = NFT_manager().get_NFTs(collection)
    return jsonify(NFTs)


# ================================
# Mining servers
# ================================


@BLP_api.route('/api/get_all_mining_servers', methods=['GET', 'POST'])
@login_required
def get_all_mining_servers():
    """
    Get all mining servers from the database
    """
    servers = Mining_server_manager().get_all_servers()
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
    - total_rent_amount_per_week
    - total_maintenance_cost_per_week (bought servers only)
    """
    server_details = Mining_server_manager().get_user_mining_server_details(server_id, user_id)
    return jsonify(server_details)


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


# ================================
# General functions
# ================================

@BLP_api.route('/set_theme')
def set_theme():
    theme = request.args.get('theme', 'light')
    session['theme'] = theme
    return '', 204
