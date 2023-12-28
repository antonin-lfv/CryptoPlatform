from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from crypto_manager import CryptoDataManager

BLP_general = Blueprint('BLP_general', __name__,
                        template_folder='templates',
                        static_folder='static')


# Decorator to update prices before each route if needed
@BLP_general.before_request
def update_prices():
    crypto_manager = CryptoDataManager()
    crypto_manager.update_crypto_data()


@BLP_general.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    return render_template('general/index.html', user=current_user)


@BLP_general.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('general/profile.html', user=current_user)


@BLP_general.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    return render_template('general/setting.html', user=current_user)


@BLP_general.route('/faq', methods=['GET', 'POST'])
@login_required
def faq():
    return render_template('general/faq.html', user=current_user)


@BLP_general.route('/crypto_dashboard', methods=['GET', 'POST'])
@login_required
def crypto_dashboard():
    # Get all crypto data
    crypto_manager = CryptoDataManager()
    market_data = crypto_manager.get_crypto_market_info()
    return render_template('general/crypto_dashboard.html', user=current_user, market_data=market_data)


@BLP_general.route('/one_crypto_dashboard/<symbol>', methods=['GET', 'POST'])
@login_required
def one_crypto_dashboard(symbol):
    return render_template('general/one_crypto_dashboard.html', user=current_user, symbol=symbol)


@BLP_general.route('/nft_dashboard', methods=['GET', 'POST'])
@login_required
def nft_dashboard():
    return render_template('general/nft_dashboard.html', user=current_user)


@BLP_general.route('/wallet', methods=['GET', 'POST'])
@login_required
def wallet():
    return render_template('general/wallets.html', user=current_user)


# ===== API

@BLP_general.route('/api/get_specific_crypto_data/<symbol>', methods=['GET', 'POST'])
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


@BLP_general.route('/api/get_all_crypto_data', methods=['GET', 'POST'])
@login_required
def get_all_crypto_data():
    crypto_manager = CryptoDataManager()
    data = crypto_manager.get_all_crypto_data()
    return data
