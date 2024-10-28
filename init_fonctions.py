import os
from datetime import datetime
from werkzeug.security import generate_password_hash
from models import User, GameWallet, CryptoWalletDailySnapshot
from notification_manager import Notification_manager
from wallet_manager import wallet_manager
from extensions import db
from utils import mini_wallet, bank_wallet


def init_admin():
    email = os.getenv("ADMIN_EMAIL")
    username = os.getenv("ADMIN_USERNAME")
    password = os.getenv("ADMIN_PASSWORD")
    assert email is not None, "ADMIN_EMAIL is not set"
    assert username is not None, "ADMIN_USERNAME is not set"
    assert password is not None, "ADMIN_PASSWORD is not set"
    new_user = User()
    new_user.email = email
    new_user.username = username
    new_user.password = generate_password_hash(password, method="scrypt")
    new_user.role = "ADMIN"
    print(f"[INFO] Creating admin user with email: {email} and username: {username}")
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
    Notification_manager().add_notification(
        user_id=User.query.filter_by(email=email).first().id,
        message=f"Welcome to CryptoSim Admin {username}!",
        icon="user",
    )

    db.session.commit()
