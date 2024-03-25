from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from configuration.config import Config as app_config
import os
from utils import NFT_collections, min_prix_NFT, max_prix_NFT, core_url_NFT
import random
import json
from utils import mini_wallet, bank_wallet
from werkzeug.security import generate_password_hash
from notification_manager import Notification_manager
from datetime import datetime

db = SQLAlchemy()


def create_app():
    # ===== Flask app
    app = Flask(__name__, template_folder='templates', static_folder='assets')
    app.config.from_object(app_config)
    # ===== Blueprint
    from auth.auth import BLP_auth
    from general.general import BLP_general
    from API.api import BLP_api
    app.register_blueprint(BLP_auth)
    app.register_blueprint(BLP_general)
    app.register_blueprint(BLP_api)
    # ===== Login manager
    login_manager = LoginManager()
    login_manager.login_view = 'BLP_auth.login'
    login_manager.init_app(app)

    with app.app_context():
        db.init_app(app)
        if not os.path.exists("instance/db.sqlite"):
            # ===== init SQLAlchemy
            db.create_all()

            # ===== Init NFT marketplace
            # Go trhough all NFTs and add them to the database
            # Add a random price between 0.1 and 100 in crypto among :
            # [Litecoin, Cardano, XRP, Dogecoin, Qtum, Basic Attention Token, NEO]
            # Lower price is more probable than higher price
            # Add a name that is the same as the collection and the index with #
            # add the collection name
            # add the image path
            from models import NFT
            print("Adding NFTs to the database")

            for collection in NFT_collections:
                collection_path = core_url_NFT + collection.lower() + '/'
                # Add as many NFTs as there is in the folder with the same name and _index (starting at 1)
                # get the number of file in collection_path
                nb_files = len(os.listdir('assets' + collection_path))
                for i in range(1, nb_files + 1):
                    name = f"{collection} #{i}"
                    path = f"{collection_path}{collection.lower()}_{i}.png"
                    price = random.uniform(min_prix_NFT, max_prix_NFT)
                    nft = NFT(name=name, collection=collection, image_path=path, price=price, owner_id=None)
                    db.session.add(nft)

                db.session.commit()

            # ===== Init Mining server
            from models import MiningServer

            path_to_mining_server_config = 'configuration/mining_servers.json'
            # Iterate over all the json in the document, and add the mining server to the database
            with open(path_to_mining_server_config) as json_file:
                data = json.load(json_file)
                for mining_server in data:
                    mining_server = MiningServer(
                        name=mining_server['Name'],
                        symbol=mining_server['Symbol'],
                        rent_amount_per_week=mining_server['RentAmountPerWeek'],
                        buy_amount=mining_server['BuyAmount'],
                        power=mining_server['Power'],
                        maintenance_cost_per_week=mining_server['MaintenanceCostPerWeek'],
                        logo_path=mining_server['Logo'],
                        category=mining_server['Category']
                    )
                    db.session.add(mining_server)
                db.session.commit()

            # Init the first user (admin)
            from models import User, GameWallet, CryptoWalletDailySnapshot
            email = os.getenv('ADMIN_EMAIL')
            username = os.getenv('ADMIN_USERNAME')
            password = os.getenv('ADMIN_PASSWORD')
            assert email is not None, "ADMIN_EMAIL is not set"
            assert username is not None, "ADMIN_USERNAME is not set"
            assert password is not None, "ADMIN_PASSWORD is not set"
            new_user = User()
            new_user.email = email
            new_user.username = username
            new_user.password = generate_password_hash(password, method='scrypt')
            db.session.add(new_user)
            # init game wallet
            game_wallet = GameWallet()
            game_wallet.user_id = User.query.filter_by(email=email).first().id
            game_wallet.mini_wallet = mini_wallet
            game_wallet.bank_wallet = bank_wallet
            db.session.add(game_wallet)
            # Create the first wallet daily snapshot
            wallet_daily_snapshot = CryptoWalletDailySnapshot()
            wallet_daily_snapshot.user_id = User.query.filter_by(email=email).first().id
            wallet_daily_snapshot.date = datetime.utcnow()
            wallet_daily_snapshot.quantity = 0
            db.session.add(wallet_daily_snapshot)
            # Add a notification to welcome the user
            Notification_manager().add_notification(user_id=User.query.filter_by(email=email).first().id,
                                                    message=f"Welcome to CryptoSim {username}!",
                                                    icon="user")
            db.session.commit()

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # ===== error page
    @app.errorhandler(404)
    def forbidden(error):
        return render_template('errors/error_404.html')

    @app.errorhandler(500)
    def forbidden(error):
        return render_template('errors/error_500.html')

    return app


app = create_app()

migrate = Migrate(app, db)
