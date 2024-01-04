from flask_login import UserMixin
from datetime import datetime, date
from app import db


class User(UserMixin, db.Model):
    """
    Table to record users
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    username = db.Column(db.String(1000))
    wallets = db.relationship('Wallet', backref='user', lazy=True)
    game_wallet = db.relationship('GameWallet', backref='user', lazy=True)


# Table pour enregistrer les cryptomonnaies détenues par les utilisateurs
class Wallet(db.Model):
    """
    Table to record the cryptocurrencies owned by users
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)  # Symbole de la cryptomonnaie, ex. BTC-USD
    quantity = db.Column(db.Float, nullable=False)     # Quantité détenue


class GameWallet(db.Model):
    """
    Table to record the USD available in the game. This is the initial amount of money that the user has when he starts
    and when he earns exp this amount increases.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User id
    mini_wallet = db.Column(db.Float(200), nullable=False)  # Amount of money available in the game (refill every day)
    bank_wallet = db.Column(db.Float(10000), nullable=False)  # Amount of money available in the bank (refill every
    # week)
    mini_wallet_last_update = db.Column(db.DateTime, default=datetime.utcnow)  # Last update of the mini wallet
    bank_wallet_last_update = db.Column(db.DateTime, default=datetime.utcnow)  # Last update of the bank wallet


class WalletHistory(db.Model):
    """
    Table to record the history of transactions in the wallets
    """
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # 'buy' ou 'sell'
    quantity = db.Column(db.Float, nullable=False)   # Quantity of crypto bought/sold
    date = db.Column(db.DateTime, default=datetime.utcnow)


class WalletDailySnapshot(db.Model):
    """
    Table to record the daily snapshots of the wallets
    """
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)  # Date of the snapshot
    quantity = db.Column(db.Float, nullable=False)  # USD value of the wallet at this date

    def __repr__(self):
        return f'<WalletDailySnapshot {self.wallet_id} {self.date} {self.quantity}>'


class CryptoPrice(db.Model):
    """
    Table to record the prices of cryptocurrencies
    """
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)   # Symbole de la cryptomonnaie, par ex. BTC
    date = db.Column(db.Date, default=datetime.utcnow)  # Date de la valeur du prix
    price = db.Column(db.Float)                          # Prix d'ouverture
    volume = db.Column(db.Integer)                      # Volume de transactions

    def __repr__(self):
        return f'<CryptoPrice {self.symbol} {self.date}>'
