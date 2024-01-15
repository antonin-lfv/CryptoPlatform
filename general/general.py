from flask import Blueprint, render_template, jsonify, session, request
from flask_login import login_required, current_user
from crypto_manager import CryptoDataManager
from wallet_manager import wallet_manager
from notification_manager import Notification_manager
from utils import top_cryptos_symbols, top_cryptos_names

BLP_general = Blueprint('BLP_general', __name__,
                        template_folder='templates',
                        static_folder='static')


@BLP_general.before_request
def update_prices():
    # Update prices if needed
    crypto_manager = CryptoDataManager()
    crypto_manager.update_crypto_data()
    # Update game wallet if needed
    w_manager = wallet_manager()
    w_manager.update_game_wallet(current_user)
    # Delete old notifications
    notification_manager = Notification_manager()
    notification_manager.delete_old_notifications(current_user)
    # Update crypto wallet evolution
    w_manager.update_crypto_wallet_evolution(current_user)


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


@BLP_general.route('/crypto_wallet', methods=['GET', 'POST'])
@login_required
def crypto_wallet():
    return render_template('general/crypto_wallets.html', user=current_user,
                           top_cryptos_symbols=top_cryptos_symbols,
                           top_cryptos_names=top_cryptos_names,
                           zip=zip)
