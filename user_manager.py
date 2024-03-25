from models import User
from app import db
from wallet_manager import wallet_manager
from crypto_manager import CryptoDataManager
from nft_manager import NFT_manager
from mining_server_manager import Mining_server_manager


class UserManager:
    def __init__(self):
        ...

    @staticmethod
    def change_username(user_id, new_username):
        try:
            user = User.query.filter_by(id=user_id).first()
            user.username = new_username
            db.session.commit()
            return {'message': 'Username changed successfully'}
        except Exception as e:
            return {'message': str(e)}

    @staticmethod
    def switch_notifications_active(user_id):
        try:
            user = User.query.filter_by(id=user_id).first()
            user.notifications_active = not user.notifications_active
            db.session.commit()
            return {'message': 'Notifications turned off successfully', 'active': user.notifications_active}
        except Exception as e:
            return {'message': str(e), 'active': False}

    @staticmethod
    def is_user_notification_active(user_id):
        user = User.query.filter_by(id=user_id).first()
        return {'active': user.notifications_active}

    @staticmethod
    def get_user_in_leaderboard(user_id):
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
            user_dict['crypto_balance'] = round(
                CryptoDataManager().get_crypto_from_USD('BTC-USD', user_dict['crypto_balance']), 2)
            user_dict['web3_balance'] = round(
                CryptoDataManager().get_crypto_from_USD('BTC-USD', user_dict['web3_balance']), 2)
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
            total_servers_bought = mining_server_manager.get_total_servers_bought(user.id)
            total_servers_rented = mining_server_manager.get_total_servers_rented(user.id)
            user_dict['total_servers'] = total_servers_bought + total_servers_rented

            data.append(user_dict)

        # Sort the data by total balance
        data = sorted(data, key=lambda x: x['total_balance'], reverse=True)
        # Add the rank
        for i, user_dict in enumerate(data):
            user_dict['rank'] = i + 1

        # Only keep one user before and one user after the user in the leaderboard
        user_index = None
        for i, user_dict in enumerate(data):
            if user_dict['id'] == user_id:
                user_index = i
                break

        if user_index is not None:
            if user_index > 0:
                data = data[user_index - 1: user_index + 2]
            else:
                data = data[user_index: user_index + 2]

        return data
