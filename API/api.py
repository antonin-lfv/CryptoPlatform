from flask import Blueprint, render_template, jsonify, session, request
from flask_login import login_required, current_user
from crypto_manager import CryptoDataManager
from wallet_manager import wallet_manager

BLP_api = Blueprint('BLP_api', __name__)


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
    if quantity_type == 'crypto':
        response = wallet_manager().buy_crypto_with_USD(current_user, symbol, From, quantity_crypto=quantity)
    else:
        response = wallet_manager().buy_crypto_with_USD(current_user, symbol, From, quantity_USD=quantity)
    return jsonify(response)


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


@BLP_api.route('/api/get_wallet_history', methods=['GET', 'POST'])
@login_required
def get_wallet_history():
    """
    Get wallet history of user
    """
    wallet_history = wallet_manager().get_wallet_history(current_user)
    return jsonify(wallet_history)


@BLP_api.route('/set_theme')
def set_theme():
    theme = request.args.get('theme', 'light')
    session['theme'] = theme
    return '', 204