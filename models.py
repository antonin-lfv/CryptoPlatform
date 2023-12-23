from flask_login import UserMixin
from datetime import datetime
from app import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    username = db.Column(db.String(1000))


class CryptoPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)   # Symbole de la cryptomonnaie, par ex. BTC
    date = db.Column(db.Date, default=datetime.utcnow)  # Date de la valeur du prix
    price = db.Column(db.Float)                          # Prix d'ouverture
    volume = db.Column(db.Integer)                      # Volume de transactions

    def __repr__(self):
        return f'<CryptoPrice {self.symbol} {self.date}>'
