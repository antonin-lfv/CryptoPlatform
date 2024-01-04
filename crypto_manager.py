from datetime import datetime, timedelta
import yfinance as yf
from utils import top_cryptos_symbols, top_cryptos_names
from configuration.config import Config
from models import CryptoPrice, User, Wallet, WalletHistory, WalletDailySnapshot
from app import db


class CryptoDataManager:
    def __init__(self):
        self.top_cryptos = top_cryptos_symbols
        self.top_cryptos_names = top_cryptos_names

    def update_crypto_data(self):
        """
        Update crypto data in database.
        Only if OFFLINE is False in config.py
        """
        if Config.OFFLINE:
            print("You are in offline mode. No data will be updated.")
            return
        else:
            for symbol in self.top_cryptos:
                latest_data = CryptoPrice.query.filter_by(symbol=symbol).order_by(CryptoPrice.date.desc()).first()

                if latest_data and latest_data.date == datetime.utcnow().date():
                    print(f"Les données pour {symbol} sont déjà à jour.")
                    continue

                # Télécharge les données depuis Yahoo Finance
                start_date = latest_data.date if latest_data else '2000-01-01'
                data = yf.download(symbol, start=start_date)

                # Ajoute les nouvelles données dans la base de données
                for index, row in data.iterrows():
                    index_date = index.date()
                    if not latest_data or index_date > latest_data.date:
                        # Add new entry with : 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'
                        new_data = CryptoPrice(
                            symbol=symbol,
                            date=index_date,
                            price=row['Open'],
                            volume=row['Volume']
                        )
                        db.session.add(new_data)

                db.session.commit()
                print(f"Les données pour {symbol} ont été mises à jour.")

    @staticmethod
    def get_specific_crypto_data(symbol):
        """
        Get crypto data for a specific symbol

        Return:
            dict with keys date and price and list of floats as values
        """
        data = CryptoPrice.query.filter_by(symbol=symbol).all()
        return {
            'date': [d.date for d in data],
            'price': [d.price for d in data]
        }

    def get_USD_from_crypto(self, symbol, quantity):
        """
        Get the USD value of a quantity of a specific crypto.

        Return:
            float
        """
        data = self.get_specific_crypto_data(symbol)
        return data['price'][-1] * quantity

    def get_crypto_from_USD(self, symbol, USD):
        """
        Get the quantity of a specific crypto from a USD amount.

        Return:
            float
        """
        data = self.get_specific_crypto_data(symbol)
        return USD / data['price'][-1]

    def get_all_crypto_data(self):
        """
        Get crypto data for all symbols. Stored in dictionary with symbol as key.

        Return:
            dict of lists of CryptoPrice objects
        """
        data = {}
        for symbol in self.top_cryptos:
            data[symbol] = CryptoPrice.query.filter_by(symbol=symbol).all()
        return data

    def get_crypto_market_info(self):
        """
        Get crypto market info for all symbols. Stored in dictionary with symbol as key.
        Elements are:
            - symbol
            - name
            - price
            - volume
            - change % (24h)
            - change % (7d)
            - change % (30d)
            - chart data (7d)

        Return:
            dict of dicts with symbol as key
        """
        market_data = {}
        for symbol, name in zip(self.top_cryptos, self.top_cryptos_names):
            latest_data = CryptoPrice.query.filter_by(symbol=symbol).order_by(CryptoPrice.date.desc()).first()
            market_data[symbol] = {
                'symbol': symbol.split('-')[0],
                'API_symbol': symbol,
                'name': name,
                # use coma to separate thousands, and round to 3 decimals
                'price': '{:,}'.format(round(latest_data.price, 3)),
                # use coma to separate thousands
                'volume': '{:,}'.format(round(latest_data.volume, 0)),
                'change_24h': 0,
                'change_7d': 0,
                'change_30d': 0,
                'chart_24d': ''
            }
            # Get change % (24h)
            market_data[symbol]['change_24h'] = self.get_crypto_change(symbol, 1)
            # Get change % (7d)
            market_data[symbol]['change_7d'] = self.get_crypto_change(symbol, 7)
            # Get change % (30d)
            market_data[symbol]['change_30d'] = self.get_crypto_change(symbol, 30)
            # Get chart data (24d) in list of floats
            latest_data = CryptoPrice.query.filter_by(symbol=symbol).order_by(CryptoPrice.date.desc()).first()
            data = list(CryptoPrice.query.filter_by(symbol=symbol).filter(
                CryptoPrice.date >= latest_data.date - timedelta(days=24)).all())
            market_data[symbol]['chart_24d'] = ','.join([str(round(d.price, 2)) for d in data])

        return market_data

    @staticmethod
    def get_crypto_change(symbol, days):
        """
        Get the change % for a specific symbol and number of days.

        Return:
            float
        """
        latest_data = CryptoPrice.query.filter_by(symbol=symbol).order_by(CryptoPrice.date.desc()).first()
        data = CryptoPrice.query.filter_by(symbol=symbol).filter(
            CryptoPrice.date >= latest_data.date - timedelta(days=days)).all()
        return round((data[-1].price - data[0].price) / data[0].price * 100, 3)
