from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from crypto_manager import CryptoDataManager
from wallet_manager import wallet_manager
from notification_manager import Notification_manager
from nft_manager import NFT_manager
from utils import top_cryptos_symbols, top_cryptos_names, NFT_collections
from utils import max_servers_rented, max_servers_bought, MAINTENANCE_MODE, symbol_to_name
from models import MiningServer, User
from mining_server_manager import Mining_server_manager
from functools import lru_cache

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
    # Start payment process for servers
    mining_server_manager = Mining_server_manager()
    mining_server_manager.check_for_server_payment(current_user.id)


@BLP_general.before_request
@login_required
def check_for_maintenance():
    if MAINTENANCE_MODE and current_user.role != 'ADMIN':
        # call maintenance page
        return render_template('general/error_maintenance.html', user=current_user)


@BLP_general.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    # ===== Mining overview =====
    # Get the number of servers bought, rented and total and the total power
    mining_overview = {}
    mining_server_manager = Mining_server_manager()
    mining_overview['total_servers_bought'] = mining_server_manager.get_total_servers_bought(current_user.id)
    mining_overview['total_servers_rented'] = mining_server_manager.get_total_servers_rented(current_user.id)
    mining_overview['total_servers'] = mining_overview['total_servers_bought'] + mining_overview['total_servers_rented']
    mining_overview['total_power'] = round(mining_server_manager.get_total_power(current_user.id), 2)
    # Format total power with comma between thousands
    mining_overview['total_power'] = "{:,}".format(mining_overview['total_power'])

    # ===== Crypto prices overview =====
    # Get the price of all cryptos in the top_cryptos_symbols list
    crypto_manager = CryptoDataManager()
    crypto_prices = crypto_manager.get_crypto_market_info()
    # create a list with all the values of the dict
    crypto_prices_list = list(crypto_prices.values())

    # ===== Crypto wallet overview =====
    # Get the total amount of USD in the wallet (crypto and web3)
    w_manager = wallet_manager()
    balance = w_manager.get_user_balance(current_user)
    crypto_balance_USD = balance['crypto_balance']  # in USD
    web3_balance_USD = balance['web3_balance']  # in USD
    total_balance_USD = crypto_balance_USD + web3_balance_USD  # in USD
    # Convert all balances to BTC
    crypto_balance_BTC = round(crypto_manager.get_crypto_from_USD('BTC-USD', crypto_balance_USD), 4)
    web3_balance_BTC = round(crypto_manager.get_crypto_from_USD('BTC-USD', web3_balance_USD), 4)
    total_balance_BTC = round(crypto_manager.get_crypto_from_USD('BTC-USD', total_balance_USD), 4)
    # Format all balances with comma between thousands
    crypto_balance_USD = "{:,}".format(crypto_balance_USD)
    web3_balance_USD = "{:,}".format(web3_balance_USD)
    total_balance_USD = "{:,}".format(total_balance_USD)
    crypto_balance_BTC = "{:,}".format(crypto_balance_BTC)
    web3_balance_BTC = "{:,}".format(web3_balance_BTC)
    total_balance_BTC = "{:,}".format(total_balance_BTC)

    # Get the 5 crypto with the highest value in the wallet
    user_crypto = balance['crypto_balance_by_symbol']
    # looks like this:
    # user_crypto = {
    # "BTC-USD": {quantity: 0, balance: 0},   # Quantity in BTC, Balance in USD
    # "ETH-USD": {quantity: 0, balance: 0},   # Quantity in ETH, Balance in USD
    #                     ...
    # }
    # Get the 5 crypto with the highest value in the wallet
    top_cryptos = sorted(user_crypto.items(), key=lambda x: x[1]['balance'], reverse=True)[:5]
    # For each, get the percentage of the total crypto balance (balance['crypto_balance'])
    for crypto in top_cryptos.copy():
        # if quantity inferior to 0.0001, write < 0.0001
        if crypto[1]['balance'] == 0:
            # delete the element from the list
            top_cryptos.remove(crypto)
            continue
        elif crypto[1]['balance'] < 0.001:
            crypto[1]['quantity'] = "< 0.001"
        else:
            crypto[1]['quantity'] = round(crypto[1]['quantity'], 2)
            crypto[1]['quantity'] = "{:,}".format(crypto[1]['quantity'])

        crypto[1]['percentage'] = max(round(crypto[1]['balance'] / balance['crypto_balance'] * 100, 2), 1)
        crypto[1]['percentage_int'] = max(int(crypto[1]['balance'] / balance['crypto_balance'] * 100), 1)
        crypto[1]['name'] = symbol_to_name[crypto[0]]
        # Format the balance with comma between thousands
        crypto[1]['balance'] = "{:,}".format(crypto[1]['balance'])

    print(top_cryptos)

    # ===== NFT overview =====
    # Number of NFTs owned, number of bids

    # ===== Classement =====
    # Get the ranking of the user in the platform

    return render_template('general/index.html', user=current_user,
                           mining_overview=mining_overview, crypto_prices_list=crypto_prices_list,
                           crypto_balance_USD=crypto_balance_USD, web3_balance_USD=web3_balance_USD,
                           total_balance_USD=total_balance_USD, crypto_balance_BTC=crypto_balance_BTC,
                           web3_balance_BTC=web3_balance_BTC, total_balance_BTC=total_balance_BTC,
                           top_cryptos=top_cryptos)


@BLP_general.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('general/profile.html', user=current_user)


@BLP_general.route('/leaderboard', methods=['GET', 'POST'])
@login_required
def leaderboard():
    # Data
    data = []
    # Get all user
    users = User.query.all()
    for user in users:
        user_dict = {'username': user.username, 'id': user.id}
        # Get the balance of the user
        w_manager = wallet_manager()
        balance = w_manager.get_user_balance(user)
        user_dict['crypto_balance'] = balance['crypto_balance']
        user_dict['web3_balance'] = balance['web3_balance']
        user_dict['total_balance'] = balance['crypto_balance'] + balance['web3_balance']
        # Convert all balances to BTC
        user_dict['crypto_balance'] = round(CryptoDataManager().get_crypto_from_USD('BTC-USD', user_dict['crypto_balance']), 2)
        user_dict['web3_balance'] = round(CryptoDataManager().get_crypto_from_USD('BTC-USD', user_dict['web3_balance']), 2)
        user_dict['total_balance'] = round(CryptoDataManager().get_crypto_from_USD('BTC-USD', user_dict['total_balance']), 2)
        # Format the balances with comma between thousands
        user_dict['crypto_balance_format'] = "{:,}".format(user_dict['crypto_balance'])
        user_dict['web3_balance_format'] = "{:,}".format(user_dict['web3_balance'])
        user_dict['total_balance_format'] = "{:,}".format(user_dict['total_balance'])
        # Get the number of NFTs owned
        nft_manager = NFT_manager()
        user_dict['number_of_NFTs'] = nft_manager.get_number_of_NFTs_user(user.id)
        # Get the number of servers bought and rented
        mining_server_manager = Mining_server_manager()
        total_servers_bought = mining_server_manager.get_total_servers_bought(user.id)
        total_servers_rented = mining_server_manager.get_total_servers_rented(user.id)
        user_dict['total_servers'] = total_servers_bought + total_servers_rented

        data.append(user_dict)

    # Sort the data by total balance
    data = sorted(data, key=lambda x: x['total_balance'], reverse=True)
    # Add the rank
    for i, user_dict in enumerate(data):
        user_dict['rank'] = i + 1

    return render_template('general/leaderboard.html', user=current_user, data=data)


@BLP_general.route('/public_profile/<user_id>', methods=['GET', 'POST'])
@login_required
def public_profile(user_id):
    user_profile = User.query.filter_by(id=user_id).first()
    current_user_obj = User.query.filter_by(id=current_user.id).first()
    return render_template('general/public_profile.html', user_profile=user_profile,
                           user=current_user_obj)


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


@BLP_general.route('/nft_marketplace', methods=['GET', 'POST'])
@BLP_general.route('/nft_marketplace/<collection>', methods=['GET', 'POST'])
@login_required
def nft_marketplace(collection=None):
    if collection is not None:
        # Check if the collection exists
        if collection not in NFT_collections:
            abort(404)
        return render_template('general/nft_marketplace.html',
                               user=current_user, NFT_collections=NFT_collections,
                               collection=collection)
    return render_template('general/nft_marketplace.html',
                           user=current_user, NFT_collections=NFT_collections)


@BLP_general.route('/nft_details/<nft_id>', methods=['GET', 'POST'])
@login_required
def nft_details(nft_id):
    # check if the nft_id exists in the database
    # if not, return an error page
    all_nfts = NFT_manager().get_NFTs(current_user.id)
    nft_ids = [str(nft['id']) for nft in all_nfts]
    if nft_id not in nft_ids:
        abort(404)

    # Get the NFT data
    nft_data = NFT_manager().get_NFT(nft_id, current_user.id)

    # Get the amount of ETH in the wallet of the user
    w_manager = wallet_manager()
    user = User.query.filter_by(id=current_user.id).first()
    # eth_amount is a dict with tokens and USD fields
    eth_amount = w_manager.get_user_specific_balance(user, 'ETH-USD')
    eth_amount['tokens'] = round(eth_amount['tokens'], 3)
    eth_amount['USD'] = round(eth_amount['USD'], 2)

    return render_template('general/nft_details.html',
                           user=current_user, nft_data=nft_data, eth_amount=eth_amount)


@BLP_general.route('/crypto_wallet', methods=['GET', 'POST'])
@login_required
def crypto_wallet():
    return render_template('general/crypto_wallets.html', user=current_user,
                           top_cryptos_symbols=top_cryptos_symbols,
                           top_cryptos_names=top_cryptos_names,
                           zip=zip)


@BLP_general.route('/mining_place', methods=['GET', 'POST'])
@login_required
def mining_place():
    """
    Grid with all types of mining servers
    """
    return render_template('general/mining_place.html', user=current_user,
                           max_servers_bought=max_servers_bought,
                           max_servers_rented=max_servers_rented)


@BLP_general.route('/mining_manage_server/<server_name>', methods=['GET', 'POST'])
@login_required
def mining_manage_server(server_name):
    """
    Details of a specific mining server type
    """
    # Vérifier si le serveur existe dans la base de données
    server = MiningServer.query.filter_by(name=server_name).first()

    # Si le serveur n'existe pas, renvoyer une page d'erreur ou une réponse appropriée
    if server is None:
        abort(404)  # ou vous pouvez renvoyer à une page d'erreur personnalisée

    # Use caching for currency conversion
    @lru_cache(maxsize=None)
    def cached_convert_fct(currency_pair, amount):
        return round(CryptoDataManager().get_USD_from_crypto(currency_pair + '-USD', amount), 1)

    # Get the overall server data
    server_data = {
        'id': server.id,
        'name': server.name,
        'symbol': server.symbol,
        'rent_amount_per_week': server.rent_amount_per_week,
        'rent_amount_per_week_USD': round(cached_convert_fct(server.symbol, server.rent_amount_per_week), 3),
        'buy_amount': server.buy_amount,
        'buy_amount_USD': round(cached_convert_fct(server.symbol, server.buy_amount), 3),
        'power': server.power,
        'power_USD': cached_convert_fct(server.symbol, server.power),
        'maintenance_cost_per_week': server.maintenance_cost_per_week,
        'maintenance_cost_per_week_USD': round(cached_convert_fct(server.symbol, server.maintenance_cost_per_week), 3),
        'logo_path': server.logo_path,
        'category': server.category,
    }

    return render_template('general/mining_manage_server.html', user=current_user,
                           server_data=server_data)


@BLP_general.route('/mining_server_invoices/<server_name>', methods=['GET', 'POST'])
@login_required
def mining_server_invoices(server_name):
    """
    Invoices of a specific mining server type
    """
    # Vérifier si le serveur existe dans la base de données
    server = MiningServer.query.filter_by(name=server_name).first()

    # Si le serveur n'existe pas, renvoyer une page d'erreur ou une réponse appropriée
    if server is None:
        abort(404)  # ou vous pouvez renvoyer à une page d'erreur personnalisée

    server_symbol = server.symbol

    return render_template('general/mining_server_invoices.html', user=current_user,
                           server_name=server_name, server_symbol=server_symbol)
