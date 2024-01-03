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


# Table pour enregistrer les cryptomonnaies détenues par les utilisateurs
class Wallet(db.Model):
    """
    Table to record the cryptocurrencies owned by users
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)  # Symbole de la cryptomonnaie, ex. BTC-USD
    quantity = db.Column(db.Float, nullable=False)     # Quantité détenue


class WalletHistory(db.Model):
    """
    Table to record the history of transactions in the wallets
    """
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # 'buy' ou 'sell'
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)


class WalletDailySnapshot(db.Model):
    """
    Table to record the daily snapshots of the wallets
    """
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)  # La date de l'instantané
    quantity = db.Column(db.Float, nullable=False)  # Quantité de la cryptomonnaie ce jour-là

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
