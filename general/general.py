from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from crypto_manager import CryptoDataManager
from wallet_manager import wallet_manager
from notification_manager import Notification_manager
from user_manager import UserManager
from nft_manager import NFT_manager
from utils import top_cryptos_symbols, top_cryptos_names, NFT_collections, number_most_valuable_cryptos
from utils import max_servers, symbol_to_name, steps, steps_bonus, get_bonus_from_BTC_wallet
from utils import NFTs_sold_steps, NFTs_bought_steps, NFTs_bid_steps, Servers_bought_steps, reward_factor
from utils import get_current_quest_step, user_profile_default_image_path
from models import MiningServer, User, CryptoWalletEvolution, UserQuestsStats, UserQuestRewards, NFT
from mining_server_manager import Mining_server_manager
from functools import lru_cache
import os

BLP_general = Blueprint('BLP_general', __name__,
                        template_folder='templates',
                        static_folder='static')


@BLP_general.before_request
@login_required
def user_updates():
    # Update game wallet if needed
    print("Updating game wallet")
    w_manager = wallet_manager()
    w_manager.update_game_wallet(current_user)
    # Delete old notifications if needed
    print("Deleting old notifications")
    notification_manager = Notification_manager()
    notification_manager.delete_old_notifications(current_user)


@BLP_general.before_request
@login_required
def check_for_maintenance():
    if (os.getenv('MAINTENANCE_MODE') == 'True') and current_user.role != 'ADMIN':
        # call maintenance page
        return render_template('general/error_maintenance.html', user=current_user)


@BLP_general.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    # ===== Mining overview =====
    # Get the number of servers bought, rented and total and the total power
    mining_overview = {}
    mining_server_manager = Mining_server_manager()
    mining_overview['total_servers'] = mining_server_manager.get_total_servers(current_user.id)
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
    # Get the percentage of evolution of the total balance using crypto_wallet_evolution for the last 24h
    crypto_wallet_evolution = CryptoWalletEvolution.query.filter_by(user_id=current_user.id).order_by(
        CryptoWalletEvolution.date.desc()).limit(2).all()
    if len(crypto_wallet_evolution) == 2:
        if crypto_wallet_evolution[1].quantity == 0:
            if crypto_wallet_evolution[0].quantity == 0:
                crypto_wallet_evolution_percent = 0
            else:
                crypto_wallet_evolution_percent = -1
        else:
            coeff = crypto_wallet_evolution[0].quantity / crypto_wallet_evolution[1].quantity
            value_change = round((coeff - 1) * 100, 2)
            crypto_wallet_evolution_percent = value_change
    else:
        crypto_wallet_evolution_percent = 0

    # Get the 5 crypto with the highest value in the wallet
    user_crypto = balance['crypto_balance_by_symbol']
    # looks like this:
    # user_crypto = {
    # "BTC-USD": {quantity: 0, balance: 0},   # Quantity in BTC, Balance in USD
    # "ETH-USD": {quantity: 0, balance: 0},   # Quantity in ETH, Balance in USD
    #                     ...
    # }
    # Get the 5 crypto with the highest value in the wallet
    top_cryptos = sorted(user_crypto.items(),
                         key=lambda x: x[1]['balance'],
                         reverse=True)[:number_most_valuable_cryptos]
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

    # ===== NFT overview =====
    # Number of NFTs owned, number of bids
    nft_manager = NFT_manager()
    number_of_NFTs = nft_manager.get_number_of_NFTs_user(current_user.id)
    number_of_bids = nft_manager.get_number_of_bids_user(current_user.id)

    # ===== Number of opened positions =====
    # Get the number of opened positions
    w_manager = wallet_manager()
    number_of_opened_positions = w_manager.get_number_of_opened_positions(current_user.id)

    print(f"number_of_opened_positions: {number_of_opened_positions}")

    # ===== Classement =====
    # Get the ranking of the user in the platform (show the leaderboard with 1 person after and before)
    user_ranking = UserManager().get_user_in_leaderboard(current_user.id)

    return render_template('general/index.html', user=current_user,
                           mining_overview=mining_overview, crypto_prices_list=crypto_prices_list,
                           crypto_balance_USD=crypto_balance_USD, web3_balance_USD=web3_balance_USD,
                           total_balance_USD=total_balance_USD, crypto_balance_BTC=crypto_balance_BTC,
                           web3_balance_BTC=web3_balance_BTC, total_balance_BTC=total_balance_BTC,
                           top_cryptos=top_cryptos, number_of_bids=number_of_bids, number_of_NFTs=number_of_NFTs,
                           user_ranking=user_ranking, number_most_valuable_cryptos=number_most_valuable_cryptos,
                           crypto_wallet_evolution_percent=crypto_wallet_evolution_percent,
                           number_of_opened_positions=number_of_opened_positions)


@BLP_general.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Get user total balance
    w_manager = wallet_manager()
    user_wallet = w_manager.get_user_balance(current_user)
    user_total_balance = user_wallet['crypto_balance'] + user_wallet['web3_balance']
    # Convert all balances to BTC
    user_total_balance = round(CryptoDataManager().get_crypto_from_USD('BTC-USD', user_total_balance), 2)
    steps_bonus_list = [i * 100 for i in steps_bonus]
    # Get the pourcentage of completion. The bar is full when the user has 2048 BTC (user_total_balance)
    # and 0 if the user has 0 BTC
    # The pourcentage is between 0 and 1200%
    # To get the completion, we had 100% for each step of the steps list, and compute the pourcentage of the last step
    completion = 0
    if user_total_balance >= steps[0]:
        for i, step in enumerate(steps):
            print(i, step, user_total_balance)
            if user_total_balance >= step:
                print("add 100")
                completion += 100
            else:
                completion += 100 * (user_total_balance - steps[i - 1]) / (steps[i] - steps[i - 1])
                print("add", 100 * (user_total_balance - steps[i - 1]) / (steps[i] - steps[i - 1]))
                print(f"steps[i-1]: {steps[i - 1]}, steps[i]: {steps[i]}")
                break
    else:
        completion = 100 * user_total_balance / (steps[0])

    return render_template('general/profile.html',
                           user=current_user,
                           user_total_balance=user_total_balance,
                           steps=steps,
                           steps_bonus_list=steps_bonus_list,
                           zip=zip,
                           completion=completion)


@BLP_general.route('/leaderboard', methods=['GET', 'POST'])
@login_required
def leaderboard():
    # Data
    data = []
    # Get all user
    users = User.query.all()
    for user in users:
        user_dict = {'username': user.username, 'id': user.id}
        if user.last_login:
            user_dict['last_login'] = user.last_login.strftime("%d/%m/%Y %H:%M")
        else:
            user_dict['last_login'] = "Never logged in"
        # Get the balance of the user
        w_manager = wallet_manager()
        balance = w_manager.get_user_balance(user)
        user_dict['crypto_balance'] = balance['crypto_balance']
        user_dict['web3_balance'] = balance['web3_balance']
        user_dict['total_balance'] = balance['crypto_balance'] + balance['web3_balance']
        # Convert all balances to BTC
        user_dict['crypto_balance'] = round(
            CryptoDataManager().get_crypto_from_USD('BTC-USD', user_dict['crypto_balance']), 2)
        user_dict['web3_balance'] = round(CryptoDataManager().get_crypto_from_USD('BTC-USD', user_dict['web3_balance']),
                                          2)
        user_dict['total_balance'] = round(
            CryptoDataManager().get_crypto_from_USD('BTC-USD', user_dict['total_balance']), 2)
        # Format the balances with comma between thousands
        user_dict['crypto_balance_format'] = "{:,}".format(user_dict['crypto_balance'])
        user_dict['web3_balance_format'] = "{:,}".format(user_dict['web3_balance'])
        user_dict['total_balance_format'] = "{:,}".format(user_dict['total_balance'])
        # Get the number of NFTs owned
        nft_manager = NFT_manager()
        user_dict['number_of_NFTs'] = nft_manager.get_number_of_NFTs_user(user.id)
        # Get the number of servers bought and rented
        mining_server_manager = Mining_server_manager()
        total_servers = mining_server_manager.get_total_servers(user.id)
        user_dict['total_servers'] = total_servers

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
    # Get the id of the nft set as profile picture
    nft_img_path = user_profile.profile_img_path
    # Get the id of the NFT where image_path is the image path
    nft = NFT.query.filter_by(image_path=nft_img_path).first()
    if nft:
        # The user has an NFT as profile picture
        nft_id = nft.id
    else:
        nft_id = None
    return render_template('general/public_profile.html', user_profile=user_profile,
                           user=current_user_obj, nft_id=nft_id)


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
    # Check if the symbol exists
    if symbol not in top_cryptos_symbols:
        abort(404)
    return render_template('general/one_crypto_dashboard.html', user=current_user, symbol=symbol)


@BLP_general.route('/nft_marketplace', methods=['GET', 'POST'])
@BLP_general.route('/nft_marketplace/<collection>', methods=['GET', 'POST'])
@login_required
def nft_marketplace(collection=NFT_collections[0]):
    if collection is None:
        collection = NFT_collections[0]
    # Check if the collection exists
    if collection not in NFT_collections:
        abort(404)
    return render_template('general/nft_marketplace.html',
                           user=current_user, NFT_collections=NFT_collections,
                           collection=collection)


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
                           user=current_user, nft_data=nft_data, eth_amount=eth_amount,
                           user_profile_default_image_path=user_profile_default_image_path)


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
    # Get the user
    user = User.query.filter_by(id=current_user.id).first()
    # Get the total BTC value of the user's wallet (NFTs and crypto)
    w_manager = wallet_manager()
    user_wallet = w_manager.get_user_balance(user)
    user_total_balance = user_wallet['crypto_balance'] + user_wallet['web3_balance']
    # Convert all balances to BTC
    user_total_balance = round(CryptoDataManager().get_crypto_from_USD('BTC-USD', user_total_balance), 2)
    # Get the bonus for the user
    BONUS_FROM_BTC_WALLET = get_bonus_from_BTC_wallet(user_total_balance)
    return render_template('general/mining_place.html', user=current_user,
                           max_servers=max_servers, BONUS_FROM_BTC_WALLET=BONUS_FROM_BTC_WALLET)


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
        return CryptoDataManager().get_USD_from_crypto(currency_pair + '-USD', amount)

    # Get the overall server data
    server_data = {
        'id': server.id,
        'name': server.name,
        'symbol': server.symbol,
        'buy_amount': server.buy_amount,
        'buy_amount_USD': round(cached_convert_fct(server.symbol, server.buy_amount), 3),
        'power': round(server.power, 3),
        'power_USD': round(cached_convert_fct(server.symbol, server.power), 2),
        'logo_path': server.logo_path,
        'category': server.category,
    }

    # Get the user
    user = User.query.filter_by(id=current_user.id).first()
    # Get the total BTC value of the user's wallet (NFTs and crypto)
    w_manager = wallet_manager()
    user_wallet = w_manager.get_user_balance(user)
    user_total_balance = user_wallet['crypto_balance'] + user_wallet['web3_balance']
    # Convert all balances to BTC
    user_total_balance = round(CryptoDataManager().get_crypto_from_USD('BTC-USD', user_total_balance), 2)
    # Get the bonus for the user
    BONUS_FROM_BTC_WALLET = get_bonus_from_BTC_wallet(user_total_balance)

    return render_template('general/mining_manage_server.html', user=current_user,
                           server_data=server_data, BONUS_FROM_BTC_WALLET=BONUS_FROM_BTC_WALLET)


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


@BLP_general.route('/player_quests', methods=['GET', 'POST'])
@login_required
def player_quests():
    # Get the user quests stats
    quests_stats = UserQuestsStats.query.filter_by(user_id=current_user.id).first()
    if quests_stats is None:
        step_nft_bought, step_nft_sold, step_nft_bid, step_servers_bought = 0, 0, 0, 0
        user_nfts_bought = 0
        user_nfts_sold = 0
        user_bids_made = 0
        user_servers_bought = 0
    else:
        user_nfts_bought = quests_stats.nfts_bought
        user_nfts_sold = quests_stats.nfts_sold
        user_bids_made = quests_stats.bids_made
        user_servers_bought = quests_stats.servers_bought
        # Get the current step of the quest
        (step_nft_bought, step_nft_sold,
         step_nft_bid, step_servers_bought) = get_current_quest_step(user_nfts_bought, user_nfts_sold,
                                                                     user_bids_made, user_servers_bought)

    print(f"step_nft_bought: {step_nft_bought}, step_nft_sold: {step_nft_sold}, "
          f"step_nft_bid: {step_nft_bid}, step_servers_bought: {step_servers_bought}")

    # Get all recovered steps
    quest_rewards = UserQuestRewards.query.filter_by(user_id=current_user.id).all()
    # For each type of quest, get the steps that have been recovered
    step_nft_bought_recovered = [reward.step for reward in quest_rewards if reward.quest_type == 'nfts_bought']
    step_nft_sold_recovered = [reward.step for reward in quest_rewards if reward.quest_type == 'nfts_sold']
    step_nft_bid_recovered = [reward.step for reward in quest_rewards if reward.quest_type == 'bids_made']
    step_servers_bought_recovered = [reward.step for reward in quest_rewards if reward.quest_type == 'servers_bought']

    print(
        f"step_nft_bought_recovered: {step_nft_bought_recovered}, step_nft_sold_recovered: {step_nft_sold_recovered}, "
        f"step_nft_bid_recovered: {step_nft_bid_recovered}, step_servers_bought_recovered: {step_servers_bought_recovered}")

    return render_template('general/quests.html', user=current_user,
                           NFTs_bought_steps=NFTs_bought_steps, NFTs_sold_steps=NFTs_sold_steps,
                           NFTs_bid_steps=NFTs_bid_steps, Servers_bought_steps=Servers_bought_steps,
                           reward_factor=reward_factor,
                           step_nft_bought=step_nft_bought, step_nft_sold=step_nft_sold,
                           step_nft_bid=step_nft_bid, step_servers_bought=step_servers_bought,
                           step_nft_bought_recovered=step_nft_bought_recovered,
                           step_nft_sold_recovered=step_nft_sold_recovered,
                           step_nft_bid_recovered=step_nft_bid_recovered,
                           step_servers_bought_recovered=step_servers_bought_recovered,
                           quests_stats_nfts_bought=user_nfts_bought,
                           quests_stats_nfts_sold=user_nfts_sold,
                           quests_stats_bids_made=user_bids_made,
                           quests_stats_servers_bought=user_servers_bought)


@BLP_general.route('/trading_place', methods=['GET', 'POST'])
@login_required
def trading_place():
    # Get all crypto data
    crypto_manager = CryptoDataManager()
    market_data = crypto_manager.get_crypto_market_info()
    # Get the number of opened positions per symbol
    w_manager = wallet_manager()
    opened_positions = w_manager.get_number_of_opened_positions_per_symbol(current_user.id)
    return render_template('general/trading_place.html', user=current_user, market_data=market_data,
                           opened_positions=opened_positions)


@BLP_general.route('/trading_place/<symbol>', methods=['GET', 'POST'])
@login_required
def trading_one_crypto(symbol):
    # Check if the symbol exists
    if symbol not in top_cryptos_symbols:
        abort(404)
    return render_template('general/trading_one_crypto.html', user=current_user, symbol=symbol)
