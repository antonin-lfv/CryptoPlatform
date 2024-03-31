from datetime import timedelta
import yfinance as yf
from utils import top_cryptos_symbols, top_cryptos_names
from configuration.config import Config
from models import CryptoPrice
from app import db


class CryptoDataManager:
    def __init__(self):
        self.top_cryptos = top_cryptos_symbols
        self.top_cryptos_names = top_cryptos_names

    def update_crypto_data(self, symbol=None):
        """
        Update crypto data in database.
        Only if OFFLINE is False in config.py

        Parameters:
            symbol: symbol of the crypto to update (ex. BTC-USD) if None update all cryptos
        """
        print(f"[INFO] Updating crypto data")

        if Config.OFFLINE:
            print("You are in offline mode. No data will be updated.")
            return
        else:
            if not symbol:
                for symbol in self.top_cryptos:
                    latest_data = CryptoPrice.query.filter_by(symbol=symbol).order_by(CryptoPrice.date.desc()).first()

                    try:
                        # Télécharge les données depuis Yahoo Finance
                        start_date = (latest_data.date - timedelta(days=1)).isoformat() if latest_data else '2000-01-01'
                        data = yf.download(symbol, start=start_date)

                        # Ajoute ou remplace les données dans la base de données
                        for index, row in data.iterrows():
                            index_date = index.date()

                            # Vérifie si la date existe déjà dans la base de données
                            existing_data = CryptoPrice.query.filter_by(symbol=symbol, date=index_date).first()

                            if existing_data:
                                # Si la date existe déjà, on met à jour le prix et le volume
                                existing_data.price = row['Close']
                                existing_data.volume = row['Volume']
                            else:
                                # Sinon on ajoute une nouvelle entrée
                                new_data = CryptoPrice(
                                    symbol=symbol,
                                    date=index_date,
                                    price=row['Close'],
                                    volume=row['Volume']
                                )
                                db.session.add(new_data)

                        db.session.commit()

                    except KeyError as e:
                        print(f"Erreur lors de la mise à jour des données pour {symbol}: {e}. Tentative de relance.")
                        self.update_crypto_data(symbol)

                    except Exception as e:
                        print(f"Une erreur inattendue est survenue: {e}.")

            else:
                latest_data = CryptoPrice.query.filter_by(symbol=symbol).order_by(CryptoPrice.date.desc()).first()

                try:
                    # Télécharge les données depuis Yahoo Finance
                    start_date = latest_data.date.strftime('%Y-%m-%d') if latest_data else '2000-01-01'
                    data = yf.download(symbol, start=start_date)

                    # Ajoute ou remplace les données dans la base de données
                    for index, row in data.iterrows():
                        index_date = index.date()

                        if latest_data and index_date == latest_data.date:
                            latest_data.price = row['Close']
                            latest_data.volume = row['Volume']
                        else:
                            new_data = CryptoPrice(
                                symbol=symbol,
                                date=index_date,
                                price=row['Close'],
                                volume=row['Volume']
                            )
                            db.session.add(new_data)

                    db.session.commit()

                except KeyError as e:
                    print(f"Erreur lors de la mise à jour des données pour {symbol}: {e}.")

                except Exception as e:
                    print(f"Une erreur inattendue est survenue: {e}.")

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
        assert symbol in self.top_cryptos, f"Symbol {symbol} is not in top cryptos."
        return data['price'][-1] * float(quantity)

    def get_crypto_from_USD(self, symbol, USD):
        """
        Get the quantity of a specific crypto from a USD amount.

        Return:
            float
        """
        data = self.get_specific_crypto_data(symbol)
        return float(USD) / data['price'][-1]

    def get_crypto_from_crypto(self, symbol_from, symbol_to, quantity):
        """
        Get the quantity of a specific crypto from a USD amount.

        Return:
            float
        """
        data_from = self.get_specific_crypto_data(symbol_from)
        data_to = self.get_specific_crypto_data(symbol_to)
        return float(quantity) * data_from['price'][-1] / data_to['price'][-1]

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
                CryptoPrice.date >= latest_data.date - timedelta(days=30)).all())
            market_data[symbol]['chart_30d'] = ','.join([str(round(d.price, 2)) for d in data])

        # Order by price
        market_data = {k: v for k, v in sorted(market_data.items(),
                                               key=lambda item: float(item[1]['price'].replace(',', '')),
                                               reverse=True)}

        return market_data

    @staticmethod
    def get_crypto_change(symbol, days):
        """
        Get the change % for a specific symbol and number of days.

        Return:
            float
        """
        last_days = CryptoPrice.query.filter_by(symbol=symbol).order_by(CryptoPrice.id.desc()).limit(days+1).all()
        # pourcentage change from last_days[-1].date to last_days[0].date
        print(last_days[0].date, last_days[-1].date)
        coeff = last_days[0].price / last_days[-1].price
        pourcentage_change = (coeff - 1) * 100
        return round(pourcentage_change, 2)
