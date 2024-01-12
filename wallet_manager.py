from datetime import datetime, timedelta
import yfinance as yf
from functools import wraps
from utils import top_cryptos_symbols, top_cryptos_names
from configuration.config import Config
from models import CryptoPrice, User, Wallet, WalletHistory, WalletDailySnapshot
from app import db
from crypto_manager import CryptoDataManager


class wallet_manager:
    """
    Manage the wallets of the users
    """
    def __init__(self):
        self.top_cryptos_symbols = top_cryptos_symbols
        self.top_cryptos_names = top_cryptos_names
        self.crypto_manager = CryptoDataManager()

    def get_user_balance(self, user):
        """
        Get user balance. (crypto + web3)

        Return:
            {
                "crypto_balance": 0, # all crypto balance in USD,
                "web3_balance": 0,  # all web3 balance in USD,
                "crypto_balance_by_symbol": {
                    "BTC-USD": {quantity: 0, balance: 0},   # Quantity in BTC, Balance in USD
                    "ETH-USD": {quantity: 0, balance: 0},   # Quantity in ETH, Balance in USD
                    ...
                }
            }
        """
        user_balance = {"crypto_balance": 0,
                        "web3_balance": 0,
                        "crypto_balance_by_symbol": {}
                        }
        # Add balance by symbol
        for symbol in self.top_cryptos_symbols:
            user_balance["crypto_balance_by_symbol"][symbol] = {
                "quantity": 0,
                "balance": 0
            }
        # Get user wallets
        wallets = user.wallets
        # Loop over wallets
        for wallet in wallets:
            # Get latest price
            balance = self.crypto_manager.get_USD_from_crypto(wallet.symbol, wallet.quantity)
            # Add to total balance
            user_balance["crypto_balance"] += balance
            # Add to balance by symbol
            user_balance["crypto_balance_by_symbol"][wallet.symbol] = {
                "quantity": wallet.quantity,
                "balance": balance
            }
            # Round balance to 2 decimals
            user_balance["crypto_balance"] = round(user_balance["crypto_balance"], 2)
            user_balance["crypto_balance_by_symbol"][wallet.symbol]["balance"] = (
                round(user_balance["crypto_balance_by_symbol"][wallet.symbol]["balance"], 2))

        return user_balance

    @staticmethod
    def get_game_wallet(user):
        """
        Get game wallet of user

        Return:
            {
                "mini_wallet": ...,
                "bank_wallet": ...
            }
        """
        if user.game_wallet:  # check if user has a game wallet
            game_wallet = user.game_wallet[0]  # get game wallet (there is only one)
            return {
                "mini_wallet": game_wallet.mini_wallet,
                "bank_wallet": game_wallet.bank_wallet
            }
        else:
            return {
                "mini_wallet": 0,
                "bank_wallet": 0
            }

    @staticmethod
    def get_wallet_history(user):
        """
        Get wallet history of user

        Return:
            {
                "wallet_history": [
                    {
                        "symbol": ...,
                        "transaction_type": ...,
                        "quantity": ...,
                        "date": ...
                    },
                    ...
                ]
            }
        """
        wallet_history = []
        if not user.wallets:
            # If user has no wallet, return empty history
            return {
                "wallet_history": wallet_history
            }
        for i in range(len(user.wallets)):
            history_wallet = WalletHistory.query.filter_by(wallet_id=user.wallets[i].id).all()
            for transaction in history_wallet:
                wallet_history.append({
                    "symbol": transaction.symbol.split('-')[0],
                    "transaction_type": transaction.transaction_type,
                    "quantity": transaction.quantity,
                    "date": transaction.date
                })

        # sort wallet history by date
        wallet_history.sort(key=lambda x: x["date"], reverse=False)

        return {
            "wallet_history": wallet_history
        }

    def buy_crypto_with_USD(self, user, symbol, From, quantity_crypto=None, quantity_USD=None):
        """
        Buy crypto with USD
        This situation only happens when the user buys crypto with USD in the game wallet.
        The check of the balance is done in the front-end.

        Parameters:
            - user: User object, the user who buys crypto
            - symbol: str, symbol of the crypto to buy
            - From: str, 'mini_wallet' or 'bank_wallet' to specify where the USD come from
            - quantity_crypto: float, quantity of crypto to buy
            - quantity_USD: float, quantity of USD to spend

        There is either a quantity_crypto or a quantity_USD, not both.
        """
        assert quantity_crypto or quantity_USD
        # Get game wallet
        game_wallet = user.game_wallet[0]
        # Update game wallet
        if quantity_crypto:
            # convert quantity_crypto to USD
            quantity_USD = self.crypto_manager.get_USD_from_crypto(symbol, quantity_crypto)

        # convert quantity_USD to float if needed
        if isinstance(quantity_USD, str):
            # try to convert to float, if not just return None
            try:
                quantity_USD = float(quantity_USD)
            except ValueError:
                return {'error': 'Not a valid quantity'}

        # Update game wallet
        if From == 'mini_wallet':
            game_wallet.mini_wallet -= quantity_USD
            game_wallet.mini_wallet_last_update = datetime.utcnow()
            # test if mini_wallet is negative, and return an error if it is
            if game_wallet.mini_wallet < 0:
                return {'error': 'Not enough money in wallet'}
        else:
            game_wallet.bank_wallet -= quantity_USD
            game_wallet.bank_wallet_last_update = datetime.utcnow()
            # test if bank_wallet is negative, and return an error if it is
            if game_wallet.bank_wallet < 0:
                return {'error': 'Not enough money in bank'}

        # Update user wallet
        wallet = Wallet.query.filter_by(user_id=user.id, symbol=symbol).first()
        # If wallet does not exist, create it
        if not wallet:
            wallet = Wallet()
            wallet.user_id = user.id
            wallet.symbol = symbol
            wallet.quantity = 0
            db.session.add(wallet)

        # Update wallet
        if quantity_USD:
            wallet.quantity += self.crypto_manager.get_crypto_from_USD(symbol, quantity_USD)
        else:
            wallet.quantity += quantity_crypto

        # Add transaction to wallet history
        if quantity_USD:
            self.add_transaction_to_wallet_history(wallet, 'buy',
                                                   self.crypto_manager.get_crypto_from_USD(symbol, quantity_USD))
        else:
            self.add_transaction_to_wallet_history(wallet, 'buy', quantity_crypto)

        # Update wallet daily snapshot with the usd value of the transaction
        if quantity_USD:
            self.update_wallet_daily_snapshot(user, quantity_USD)
        else:
            self.update_wallet_daily_snapshot(user,
                                              self.crypto_manager.get_USD_from_crypto(symbol, quantity_crypto))

        # Commit changes
        db.session.commit()

        return {'success': 'Transaction successful'}

    def buy_crypto_with_crypto(self, user, symbol_to_sell, symbol_to_buy, quantity_to_sell=None, quantity_to_buy=None):
        """
        Buy crypto with crypto
        Using the wallet of the user, the user can buy crypto with crypto.

        Parameters:
            - user: User object, the user who buys crypto
            - symbol_to_sell: str, symbol of the crypto to sell
            - symbol_to_buy: str, symbol of the crypto to buy
            - quantity_to_sell: float, quantity of crypto to sell
            - quantity_to_buy: float, quantity of crypto to buy

        """
        # Get user wallet
        wallet_crypto_to_sell = Wallet.query.filter_by(user_id=user.id, symbol=symbol_to_sell).first()
        # If wallet does not exist, the user does not have this crypto, so return an error
        if not wallet_crypto_to_sell:
            return {'error': 'You do not have this crypto'}

        # If we have quantity_to_sell, convert it to quantity_to_buy
        if quantity_to_sell:
            quantity_to_sell = float(quantity_to_sell)
            quantity_to_buy = self.crypto_manager.get_crypto_from_crypto(symbol_to_sell, symbol_to_buy,
                                                                         quantity_to_sell)
        # If we have quantity_to_buy, convert it to quantity_to_sell
        else:
            quantity_to_buy = float(quantity_to_buy)
            quantity_to_sell = self.crypto_manager.get_crypto_from_crypto(symbol_to_buy, symbol_to_sell,
                                                                          quantity_to_buy)

        # If user does not have enough crypto, return an error
        if wallet_crypto_to_sell.quantity < quantity_to_sell:
            return {'error': 'Not enough crypto in wallet'}

        # Check if the amount to sell or to buy is not 0, if it is, return an error
        if quantity_to_sell == 0 or quantity_to_buy == 0:
            return {'error': 'Can\'t sell or buy 0 crypto'}

        # Update wallets (avoid negative quantity with approximations)
        wallet_crypto_to_sell.quantity = max(wallet_crypto_to_sell.quantity-quantity_to_sell, 0)

        # Get user wallet for symbol_to_buy
        wallet_crypto_to_buy = Wallet.query.filter_by(user_id=user.id, symbol=symbol_to_buy).first()
        # If wallet does not exist, create it
        if not wallet_crypto_to_buy:
            wallet = Wallet()
            wallet.user_id = user.id
            wallet.symbol = symbol_to_buy
            wallet.quantity = 0
            db.session.add(wallet)
            # Commit changes
            db.session.commit()
            # Get user wallet for symbol_to_buy
            wallet_crypto_to_buy = Wallet.query.filter_by(user_id=user.id, symbol=symbol_to_buy).first()

        # Update wallet
        wallet_crypto_to_buy.quantity += quantity_to_buy

        # Add transaction to wallet history sell and buy
        self.add_transaction_to_wallet_history(wallet_crypto_to_sell, 'sell', quantity_to_sell)
        self.add_transaction_to_wallet_history(wallet_crypto_to_buy, 'buy', quantity_to_buy)

        # wallet daily snapshot is not updated because there is no upcomming transaction from outside the wallet
        # it's just a transfer inside the wallet

        return {'success': 'Transaction successful'}

    @staticmethod
    def add_transaction_to_wallet_history(wallet, transaction_type, quantity):
        """
        Add transaction to wallet history

        Parameters:
            - wallet: Wallet object, the wallet where the transaction is made
            - transaction_type: str, 'buy' or 'sell'
            - quantity: float, quantity of crypto bought/sold
        """
        transaction = WalletHistory()
        transaction.wallet_id = wallet.id
        transaction.transaction_type = transaction_type
        transaction.quantity = quantity
        transaction.symbol = wallet.symbol
        transaction.date = datetime.utcnow()
        db.session.add(transaction)
        db.session.commit()

    @staticmethod
    def update_wallet_daily_snapshot(user, quantity):
        """
        Update wallet daily snapshot

        Parameters:
            - user: User object, the user who buys crypto
            - quantity: float, quantity of crypto bought/sold
        """
        # Get latest snapshot
        latest_snapshot = WalletDailySnapshot.query.filter_by(user_id=user.id).order_by(
            WalletDailySnapshot.date.desc()).first()
        # If latest snapshot is not today, add new snapshot
        if not latest_snapshot or latest_snapshot.date != datetime.utcnow().date():
            new_snapshot = WalletDailySnapshot()
            new_snapshot.user_id = user.id
            new_snapshot.date = datetime.utcnow().date()
            new_snapshot.quantity = quantity
            db.session.add(new_snapshot)
            db.session.commit()
        else:
            # Update latest snapshot by adding the quantity of the transaction
            latest_snapshot.quantity += quantity
            db.session.commit()
