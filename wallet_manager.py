from datetime import datetime, timedelta
from utils import top_cryptos_symbols, top_cryptos_names
from models import (CryptoWallet, CryptoTransactionHistory, CryptoWalletDailySnapshot,
                    CryptoWalletEvolution, UserNFT, NFT)
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

        # Get web3 balance
        nfts = UserNFT.query.filter_by(user_id=user.id).all()
        for nft in nfts:
            nft_id = nft.nft_id
            NFT_item = NFT.query.filter_by(id=nft_id).first()
            USD_price = CryptoDataManager().get_USD_from_crypto('ETH-USD', NFT_item.price)
            user_balance["web3_balance"] += USD_price

        # Round balance to 2 decimals
        user_balance["web3_balance"] = round(user_balance["web3_balance"], 2)

        return user_balance

    def get_user_specific_balance(self, user, symbol):
        """
        Get user balance for a specific crypto. (tokens + USD conversion)

        Return:
            {
                "tokens": 0,
                "USD": 0
            }
        """
        user_balance = {
            "tokens": 0,
            "USD": 0
        }
        # Get user wallets
        wallets = user.wallets
        # Loop over wallets
        for wallet in wallets:
            if wallet.symbol == symbol:
                user_balance["tokens"] += wallet.quantity
                user_balance["USD"] += self.crypto_manager.get_USD_from_crypto(wallet.symbol, wallet.quantity)
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
    def update_game_wallet(user):
        """
        Update game wallet of user

        if col mini_wallet_last_update is older than 1 day, set mini_wallet to 1000
        if col bank_wallet_last_update is older than 2 days, set bank_wallet to 10000
        """
        game_wallet = user.game_wallet[0]
        if game_wallet.mini_wallet_last_update < datetime.utcnow() - timedelta(days=1):
            game_wallet.mini_wallet = 1000
            game_wallet.mini_wallet_last_update = datetime.utcnow()
        if game_wallet.bank_wallet_last_update < datetime.utcnow() - timedelta(days=2):
            game_wallet.bank_wallet = 10000
            game_wallet.bank_wallet_last_update = datetime.utcnow()
        db.session.commit()

    @staticmethod
    def get_crypto_wallet_evolution(user):
        """
        Get wallet evolution of user (USD value of the whole wallet per day)

        Return:
            {
                "wallet_evolution": [
                    {
                        "quantity": ...,
                        "date": ...
                    },
                    ...
                ]
            }
        """
        wallet_evolution = []
        # Get wallet evolution of user sorted by date
        crypto_wallet_evolution = CryptoWalletEvolution.query.filter_by(user_id=user.id).order_by(
            CryptoWalletEvolution.date.desc()).all()

        # If user has no wallet evolution, create one with today's date and 0 quantity
        if not crypto_wallet_evolution:
            new_evolution = CryptoWalletEvolution()
            new_evolution.user_id = user.id
            new_evolution.date = datetime.utcnow().date()
            new_evolution.quantity = 0
            db.session.add(new_evolution)
            db.session.commit()
            # Get wallet evolution of user sorted by date
            crypto_wallet_evolution = CryptoWalletEvolution.query.filter_by(user_id=user.id).order_by(
                CryptoWalletEvolution.date.desc()).all()

        for evolution in crypto_wallet_evolution:
            wallet_evolution.append({
                "date": evolution.date,
                "value": evolution.quantity
            })

        # sort wallet evolution by date
        wallet_evolution.sort(key=lambda x: x["date"], reverse=False)

        # Format date to look like this: "2021-10-01"
        for evolution in wallet_evolution:
            evolution["date"] = evolution["date"].isoformat()

        return wallet_evolution

    def update_crypto_wallet_evolution(self, user):
        """
        Update wallet evolution of user (USD value of the whole wallet per day)
        Go through all wallets of the user and sum the USD value of each crypto
        If there is no wallet evolution for today, create one, else update the quantity
        """
        # Get wallet evolution of user sorted by date
        crypto_wallet_evolution = CryptoWalletEvolution.query.filter_by(user_id=user.id).order_by(
            CryptoWalletEvolution.date.desc()).all()

        # If user has no wallet evolution, create one with today's date and 0 quantity
        if not crypto_wallet_evolution:
            new_evolution = CryptoWalletEvolution()
            new_evolution.user_id = user.id
            new_evolution.date = datetime.utcnow().date()
            new_evolution.quantity = 0
            db.session.add(new_evolution)
            db.session.commit()
            # Get wallet evolution of user sorted by date
            crypto_wallet_evolution = CryptoWalletEvolution.query.filter_by(user_id=user.id).order_by(
                CryptoWalletEvolution.date.desc()).all()

        # Get user wallets
        wallets = user.wallets
        # Loop over wallets
        quantity = 0
        for wallet in wallets:
            # Get latest price
            balance = self.crypto_manager.get_USD_from_crypto(wallet.symbol, wallet.quantity)
            # Add to total balance
            quantity += balance
            # Round balance to 2 decimals
            quantity = round(quantity, 3)

        # Check if there is a wallet evolution for today
        if crypto_wallet_evolution[0].date == datetime.utcnow().date():
            # If there is, update the quantity
            crypto_wallet_evolution[0].quantity = quantity

        else:
            # If there is not, create one
            new_evolution = CryptoWalletEvolution()
            new_evolution.user_id = user.id
            new_evolution.date = datetime.utcnow().date()
            new_evolution.quantity = quantity
            db.session.add(new_evolution)

        db.session.commit()

    @staticmethod
    def update_wallet_daily_snapshot(user, quantity):
        """
        Update wallet daily snapshot (USD spent in the game wallet during the day)

        Parameters:
            - user: User object, the user who buys crypto
            - quantity: float, quantity of crypto bought
        """
        # Get latest snapshot
        latest_snapshot = CryptoWalletDailySnapshot.query.filter_by(user_id=user.id).order_by(
            CryptoWalletDailySnapshot.date.desc()).first()
        # If latest snapshot is not today, add new snapshot
        if not latest_snapshot or latest_snapshot.date != datetime.utcnow().date():
            new_snapshot = CryptoWalletDailySnapshot()
            new_snapshot.user_id = user.id
            new_snapshot.date = datetime.utcnow().date()
            new_snapshot.quantity = quantity
            db.session.add(new_snapshot)
            db.session.commit()
        else:
            # Update latest snapshot by adding the quantity of the transaction
            latest_snapshot.quantity += quantity
            db.session.commit()

    @staticmethod
    def get_wallet_crypto_transactions_history(user):
        """
        Get wallet history of user (transactions)

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
            history_wallet = CryptoTransactionHistory.query.filter_by(wallet_id=user.wallets[i].id).all()
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

    @staticmethod
    def get_crypto_wallet_daily_snapshot(user):
        """
        Get wallet daily snapshot of user
        Each value needs to be cumulated with the previous one
        Because it's a snapshot of all USD spent in the game wallet during the day

        Return:
            {
                "wallet_daily_snapshot": [
                    {
                        "date": ...,
                        "quantity": ...
                    },
                    ...
                ]
            }
        """
        wallet_daily_snapshot = []
        daily_snapshot_wallet = CryptoWalletDailySnapshot.query.filter_by(user_id=user.id).all()

        if not daily_snapshot_wallet:
            # If user has no wallet daily snapshot, create one with today's date and 0 quantity
            new_snapshot = CryptoWalletDailySnapshot()
            new_snapshot.user_id = user.id
            new_snapshot.date = datetime.utcnow().date()
            new_snapshot.quantity = 0
            db.session.add(new_snapshot)
            db.session.commit()

        for snapshot in daily_snapshot_wallet:
            wallet_daily_snapshot.append({
                "date": snapshot.date,
                "value": snapshot.quantity
            })

        # sort wallet history by date
        wallet_daily_snapshot.sort(key=lambda x: x["date"], reverse=False)

        # cumulate quantity
        for i in range(len(wallet_daily_snapshot)):
            if i > 0:
                wallet_daily_snapshot[i]["value"] += wallet_daily_snapshot[i - 1]["value"]

        # fill missing dates between first and today
        if wallet_daily_snapshot[0]["date"] != datetime.utcnow().date():
            # get first date
            first_date = wallet_daily_snapshot[0]["date"]
            # get today's date
            today = datetime.utcnow().date()
            # loop over dates between first and today
            for i in range((today - first_date).days + 1):
                # get date
                date = first_date + timedelta(days=i)
                # check if date is in wallet daily snapshot
                if date not in [snapshot["date"] for snapshot in wallet_daily_snapshot]:
                    # if not, add it with the value of the previous day
                    wallet_daily_snapshot.append({
                        "date": date,
                        "value": wallet_daily_snapshot[-1]["value"]
                    })

        # Format date to look like this: "2021-10-01"
        for snapshot in wallet_daily_snapshot:
            snapshot["date"] = snapshot["date"].isoformat()

        return wallet_daily_snapshot

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
        wallet = CryptoWallet.query.filter_by(user_id=user.id, symbol=symbol).first()
        # If wallet does not exist, create it
        if not wallet:
            wallet = CryptoWallet()
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

        # Update wallet evolution
        self.update_crypto_wallet_evolution(user)

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
        wallet_crypto_to_sell = CryptoWallet.query.filter_by(user_id=user.id, symbol=symbol_to_sell).first()
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
        wallet_crypto_to_sell.quantity = max(wallet_crypto_to_sell.quantity - quantity_to_sell, 0)

        # Get user wallet for symbol_to_buy
        wallet_crypto_to_buy = CryptoWallet.query.filter_by(user_id=user.id, symbol=symbol_to_buy).first()
        # If wallet does not exist, create it
        if not wallet_crypto_to_buy:
            wallet = CryptoWallet()
            wallet.user_id = user.id
            wallet.symbol = symbol_to_buy
            wallet.quantity = 0
            db.session.add(wallet)
            # Commit changes
            db.session.commit()
            # Get user wallet for symbol_to_buy
            wallet_crypto_to_buy = CryptoWallet.query.filter_by(user_id=user.id, symbol=symbol_to_buy).first()

        # Update wallet
        wallet_crypto_to_buy.quantity += quantity_to_buy

        # Add transaction to wallet history sell and buy
        self.add_transaction_to_wallet_history(wallet_crypto_to_sell, 'sell', quantity_to_sell)
        self.add_transaction_to_wallet_history(wallet_crypto_to_buy, 'buy', quantity_to_buy)

        # Update wallet USD value evolution
        self.update_crypto_wallet_evolution(user)

        # wallet daily snapshot is not updated because there is no upcomming transaction from outside the wallet
        # it's just a transfer inside the wallet

        return {'success': 'Transaction successful'}

    @staticmethod
    def buy_with_crypto(user, symbol, quantity):
        """
        Buy a service or a product with crypto like:
        - Mining server
        - NFT
        ...
        """
        # get the user wallet for the crypto and check if the user has enough crypto
        # if yes, update the wallet and return success
        # if not, return an error
        user_wallet = CryptoWallet.query.filter_by(user_id=user.id, symbol=symbol).first()
        if user_wallet.quantity >= quantity:
            # use max to avoid negative quantity with approximations
            user_wallet.quantity = max(user_wallet.quantity - quantity, 0)
            db.session.commit()

            # Update wallet evolution
            w_manager = wallet_manager()
            w_manager.update_crypto_wallet_evolution(user)

            return {'success': 'Transaction successful'}
        else:
            return {'error': 'Not enough crypto in wallet'}

    @staticmethod
    def receive_crypto(user, symbol, quantity):
        """
        Receive crypto from another user
        """
        # get the user wallet for the crypto and update the wallet
        user_wallet = CryptoWallet.query.filter_by(user_id=user.id, symbol=symbol).first()
        user_wallet.quantity += quantity
        db.session.commit()

        # Update wallet evolution
        w_manager = wallet_manager()
        w_manager.update_crypto_wallet_evolution(user)

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
        transaction = CryptoTransactionHistory()
        transaction.wallet_id = wallet.id
        transaction.transaction_type = transaction_type
        transaction.quantity = quantity
        transaction.symbol = wallet.symbol
        transaction.date = datetime.utcnow()
        db.session.add(transaction)
        db.session.commit()
