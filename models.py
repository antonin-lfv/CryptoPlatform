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
    username = db.Column(db.String(25))
    role = db.Column(db.String(100), default='USER')
    profile_img_path = db.Column(db.String(1000), default="images/avatar/avatar-1.png")
    notifications_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, default=None)
    wallets = db.relationship('CryptoWallet', backref='user', lazy=True)
    game_wallet = db.relationship('GameWallet', backref='user', lazy=True)


# Table pour enregistrer les cryptomonnaies détenues par les utilisateurs
class CryptoWallet(db.Model):
    """
    Table to record the cryptocurrencies owned by users
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)  # Symbole de la cryptomonnaie, ex. BTC-USD
    quantity = db.Column(db.Float, nullable=False)  # Quantité détenue


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


class CryptoTransactionHistory(db.Model):
    """
    Table to record the history of transactions in the wallets
    """
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('crypto_wallet.id'), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # 'buy' ou 'sell'
    quantity = db.Column(db.Float, nullable=False)  # Quantity of crypto bought/sold
    symbol = db.Column(db.String(10), nullable=False)  # Symbole de la cryptomonnaie, ex. BTC
    date = db.Column(db.DateTime, default=datetime.utcnow)


class CryptoWalletDailySnapshot(db.Model):
    """
    Table to record the daily snapshots of the wallets (USD spent per day)
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User id
    date = db.Column(db.Date, default=date.today)  # Date of the snapshot
    quantity = db.Column(db.Float, nullable=False)  # USD value of the wallet at this date

    def __repr__(self):
        return f'<WalletDailySnapshot {self.wallet_id} {self.date} {self.quantity}>'


class CryptoPrice(db.Model):
    """
    Table to record the prices of cryptocurrencies
    """
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)  # Symbole de la cryptomonnaie, par ex. BTC
    date = db.Column(db.Date, default=datetime.utcnow)  # Date de la valeur du prix
    price = db.Column(db.Float)  # Prix d'ouverture
    volume = db.Column(db.Integer)  # Volume de transactions

    def __repr__(self):
        return f'<CryptoPrice {self.symbol} {self.date}>'


class CryptoWalletEvolution(db.Model):
    """
    Table to record the evolution of the wallet (in USD) per day
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User id
    date = db.Column(db.Date, default=date.today)  # Date of the snapshot
    quantity = db.Column(db.Float, nullable=False)  # USD value of the wallet at this date

    def __repr__(self):
        return f'<WalletEvolution {self.wallet_id} {self.date} {self.quantity}>'


class Notification(db.Model):
    """
    Table to record the notifications of the users

    Icon can be:
    - users
    - user
    - warning
    - shopping-cart

    Example:
        <li>
            <a href="#">
                <i class="fa fa-users text-info"></i> Some notification text
            </a>
        </li>
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User id
    date = db.Column(db.DateTime, default=datetime.utcnow)  # Date of the notification
    message = db.Column(db.String(1000), nullable=False)  # Message of the notification
    icon = db.Column(db.String(1000), nullable=False)  # Icon of the notification


class MiningServer(db.Model):
    """
    Table to record the mining servers available in the game and their characteristics
    This table is used to display the servers in the shop and to allow users to buy or rent them
    It's a static table, just to store the characteristics of the servers
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    rent_amount_per_day = db.Column(db.Float, nullable=False)
    buy_amount = db.Column(db.Float, nullable=False)
    power = db.Column(db.Float, nullable=False)
    maintenance_cost_per_day = db.Column(db.Float, nullable=False)
    logo_path = db.Column(db.String(1000), nullable=False)
    category = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Server {self.name}>'


class UserServer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    server_id = db.Column(db.Integer, db.ForeignKey('mining_server.id'), nullable=False)
    # Last earning date (None if no earning yet)
    next_earning_date = db.Column(db.Date, nullable=True)
    # Number of instances of the server
    instances_number = db.Column(db.Integer, nullable=False, default=0)

    user = db.relationship('User', backref=db.backref('user_servers', lazy=True))
    server = db.relationship('MiningServer', backref=db.backref('server_users', lazy=True))

    def __repr__(self):
        return f'<UserServer {self.user_id} owns/rents {self.server_id}>'


class ServerInvoices(db.Model):
    """
    Class to generate invoices for the servers

    Attributes
    - Period: Month and year of the invoice
    - Issuer: Name of the issuer of the invoice (username)
    - Due date: Date of payment of the invoice
    - Amount: Amount to pay
    - type_payment: 'rent' or 'buy'
    - server_id: id of the server type in MiningServer
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    period = db.Column(db.String(10), nullable=False)
    issuer = db.Column(db.String(100), nullable=False)
    purchase_date = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type_payment = db.Column(db.String(10), nullable=False)
    server_id = db.Column(db.Integer, nullable=True)
    instances_number = db.Column(db.Integer, nullable=True)


class NFT(db.Model):
    """
    Table to record the NFTs available in the game
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Name of the NFT
    collection = db.Column(db.String(100), nullable=False)  # Collection of the NFT
    price = db.Column(db.Float, nullable=False)  # Price of the NFT at this moment in ETH
    image_path = db.Column(db.String(1000), nullable=False)  # Path to the image of the NFT
    is_for_sale = db.Column(db.Boolean, default=True)  # Is the NFT for sale?
    views_number = db.Column(db.Integer, default=0)  # Number of views of the NFT
    price_change_24h = db.Column(db.Float, default=0)  # Pourcentage change of the price in the last 24h in USD
    # owner id is optional because the NFT can be for sale without having an owner
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Owner of the NFT

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'collection': self.collection,
            'price': self.price,
            'image_path': self.image_path,
            'is_for_sale': self.is_for_sale,
            'views_number': self.views_number,
            'price_change_24h': self.price_change_24h,
            'owner_id': self.owner_id
        }


class UserLikedNFT(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User id
    nft_id = db.Column(db.Integer, db.ForeignKey('nft.id'), nullable=False)  # NFT id

    user = db.relationship('User', backref=db.backref('user_liked_nfts', lazy=True))
    nft = db.relationship('NFT', backref=db.backref('nft_likers', lazy=True))

    def __repr__(self):
        return f'<UserLikedNFT {self.user_id} likes {self.nft_id}>'


class UserNFT(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    nft_id = db.Column(db.Integer, db.ForeignKey('nft.id'), nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    purchase_price_usd = db.Column(db.Float, nullable=False)
    purchase_price_crypto = db.Column(db.Float, nullable=False)
    purchase_crypto_symbol = db.Column(db.String(10), nullable=False)

    user = db.relationship('User', backref=db.backref('user_nfts', lazy=True))
    nft = db.relationship('NFT', backref=db.backref('nft_owners', lazy=True))

    def __repr__(self):
        return f'<UserNFT {self.user_id} owns {self.nft_id}>'


class NFTBid(db.Model):
    """
    Table to record the bids on NFTs
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    nft_id = db.Column(db.Integer, db.ForeignKey('nft.id'), nullable=False)
    bid_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    bid_price_crypto = db.Column(db.Float, nullable=False)
    bid_crypto_symbol = db.Column(db.String(10), nullable=False)

    user = db.relationship('User', backref=db.backref('user_bids', lazy=True))
    nft = db.relationship('NFT', backref=db.backref('nft_bids', lazy=True))

    def __repr__(self):
        return f'<UserBid {self.user_id} bids {self.nft_id}>'
