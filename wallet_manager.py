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
                    "BTC": {Quantity: 0, Balance: 0},   # Quantity in BTC, Balance in USD
                    "ETH": {Quantity: 0, Balance: 0},   # Quantity in ETH, Balance in USD
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
        if quantity_USD:
            game_wallet[From] -= quantity_USD
        else:
            # convert quantity_crypto to USD
            quantity_USD = self.crypto_manager.get_USD_from_crypto(symbol, quantity_crypto)
            game_wallet[From] -= quantity_USD

        # Update user wallet
        wallet = user.wallets.filter_by(symbol=symbol).first()
        if quantity_USD:
            wallet.quantity += self.crypto_manager.get_crypto_from_USD(symbol, quantity_USD)
        else:
            wallet.quantity += quantity_crypto

        # Add transaction to wallet history
        if quantity_USD:
            self.add_transaction_to_wallet_history(wallet, 'buy', self.crypto_manager.get_crypto_from_USD(symbol, quantity_USD))
        else:
            self.add_transaction_to_wallet_history(wallet, 'buy', quantity_crypto)

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
        db.session.add(transaction)
        db.session.commit()