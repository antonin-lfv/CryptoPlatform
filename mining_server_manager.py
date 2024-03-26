from models import MiningServer, UserServer, User, ServerInvoices
from wallet_manager import wallet_manager
from crypto_manager import CryptoDataManager
from notification_manager import Notification_manager
from datetime import datetime, timedelta
from app import db
from functools import lru_cache
from collections import defaultdict
from utils import top_cryptos_symbols, max_servers
from tqdm import tqdm


class Mining_server_manager:

    def __init__(self):
        ...

    @staticmethod
    def check_for_server_payment(user_id):
        """
        Calculate and apply payment and earnings for all servers in one operation instead of daily iterations.
        """

        # Get the user
        user = User.query.filter_by(id=user_id).first()

        today_date = datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d").date()
        tomorrow_date = today_date + timedelta(days=1)

        # If the user has no servers, return
        if not UserServer.query.filter_by(user_id=user_id).first():
            return

        # Get the closest next_earning_date for the user
        closest_next_earning_date = UserServer.query.filter_by(user_id=user_id).order_by(
            UserServer.next_earning_date).first().next_earning_date

        # If the closest next_earning_date is in the future, return
        if closest_next_earning_date > today_date:
            return

        # Get all servers for the user
        user_server_instances = UserServer.query.filter_by(user_id=user_id).all()

        # Get all mining servers in dict with id as key
        mining_servers = {server.id: server for server in MiningServer.query.all()}

        # Get the user's wallet for all the crypto symbols
        user_wallet_dict = wallet_manager().get_user_balance(user)['crypto_balance_by_symbol']

        # Get the price for one unit of each crypto in USD to use for conversion
        @lru_cache(maxsize=None)
        def cached_convert_fct(currency_pair, amount):
            return round(CryptoDataManager().get_USD_from_crypto(currency_pair, amount), 1)

        number_of_servers_deleted = 0
        USD_amount_earned = 0

        print(f"[INFO]: Calculating payments and earnings for user {user_id} on {today_date.strftime('%Y-%m-%d')}")

        for server_instance in tqdm(user_server_instances):
            # === Calculate total earnings
            # Get the server details
            server_details = mining_servers[server_instance.server_id]
            # For each server instance, we compute the number of days since the last earning
            # Convert next_earning_date to datetime
            if server_instance.next_earning_date <= today_date:
                # Number of days since the last earning
                number_of_days_since_last_earning = (today_date - server_instance.next_earning_date).days
                # Compute the total earnings for the server instance
                total_earnings = server_details.power * server_instance.instances_number * number_of_days_since_last_earning
                # Convert the total earnings to USD
                total_earnings_USD = cached_convert_fct(server_details.symbol + '-USD', total_earnings)
                # Update the user's wallet
                wallet_manager().receive_crypto(user, server_details.symbol + '-USD', total_earnings)
                # Update the total USD amount earned
                USD_amount_earned += total_earnings_USD

                # Update the next earning date
                server_instance.next_earning_date = tomorrow_date

                # === Calculate total payments
            # For each server instance (rent only), we compute the number of days since the last payment
            if server_instance.next_payment_date and server_instance.next_payment_date <= today_date:
                # Number of days since the last payment
                number_of_days_since_last_payment = (today_date - server_instance.next_payment_date).days
                # Compute the total payment for the server instance
                total_payment = server_details.rent_amount_per_day * server_instance.instances_number * number_of_days_since_last_payment
                # Update the user's wallet
                wallet_manager().buy_with_crypto(user, server_details.symbol + '-USD', total_payment)

                # Update the next payment date
                server_instance.next_payment_date = tomorrow_date

        if number_of_servers_deleted > 0:
            Notification_manager.add_notification(user_id,
                                                  f"{number_of_servers_deleted} server(s) deleted due to not "
                                                  f"enough crypto to afford rent on {today_date.strftime('%Y-%m-%d')}",
                                                  "warning")

        if USD_amount_earned > 0:
            Notification_manager.add_notification(user_id,
                                                  f"You earned {round(USD_amount_earned, 2)} USD from mining "
                                                  f"on {today_date.strftime('%Y-%m-%d')}",
                                                  "shopping-cart")

    @staticmethod
    def get_user_mining_servers_invoices(user, server_name):
        """
        Get the invoices for a user
        """
        # Get the server type id
        server_type_id = MiningServer.query.filter_by(name=server_name).first().id
        # Get the invoices for this server type
        user_server_type_invoices = ServerInvoices.query.filter_by(server_id=server_type_id, user_id=user.id).all()
        # sort by period
        user_server_type_invoices = sorted(user_server_type_invoices, key=lambda x: x.period, reverse=True)
        invoices_list = []
        # Aggregate the invoices by period and sum the amount (field instances_number)
        for invoice in user_server_type_invoices:
            invoice_dict = {'period': invoice.period, 'issuer': invoice.issuer, 'purchase_date': invoice.purchase_date,
                            'amount': invoice.amount, 'type_payment': invoice.type_payment, 'server_name': server_name}
            elem = {'period': invoice.period, 'issuer': invoice.issuer, 'purchase_date': invoice.purchase_date,
                    'type_payment': invoice.type_payment}
            invoice_to_add = find_invoice(invoices_list, elem)
            if invoice_to_add is None:
                invoice_dict['number_of_instances'] = invoice.instances_number
                invoices_list.append(invoice_dict)
            else:
                invoice_to_add['amount'] += invoice.amount
                invoice_to_add['number_of_instances'] += invoice.instances_number

        return invoices_list

    @staticmethod
    def add_invoice(user_id, period, issuer, purchase_date, amount, server_id, type_payment, instances_number):
        """
        Add an invoice to the database
        """
        print(f"[INFO]: Adding invoice for server_id {server_id}")
        invoice = ServerInvoices(period=period, issuer=issuer, purchase_date=purchase_date, amount=amount,
                                 server_id=server_id, type_payment=type_payment, user_id=user_id,
                                 instances_number=instances_number)
        db.session.add(invoice)
        db.session.commit()

    @staticmethod
    def get_all_servers(user_id):
        """
        Get all mining servers of the user

        Return:
            dict
        """
        # Get the number of server instances for each server type of the user (bought and rented)
        # Get all user server instances with a single query
        user_server_instances = UserServer.query.filter_by(user_id=user_id).all()
        user_server_instances_dict = defaultdict(int)
        for server_instance in user_server_instances:
            key_suffix = 'buy'
            key = f"{server_instance.server_id}_{key_suffix}"
            user_server_instances_dict[key] += server_instance.instances_number

        # Get all mining servers with a single query
        servers = MiningServer.query.all()

        # Use caching for currency conversion
        @lru_cache(maxsize=None)
        def cached_convert_fct(currency_pair, amount):
            return round(CryptoDataManager().get_USD_from_crypto(currency_pair, amount), 1)

        # Création d'un dictionnaire pour stocker la conversion de 1 unité de chaque devise en USD
        conversion_rates = {}

        # Récupération des taux de conversion pour chaque devise unique
        unique_symbols = set(server.symbol for server in servers)
        for symbol in unique_symbols:
            usd_suffix = '-USD'
            # Stocker le taux de conversion pour 1 unité de la devise
            conversion_rates[symbol] = cached_convert_fct(symbol + usd_suffix, 1)

        servers_list = []
        for server_item in servers:
            symbol = server_item.symbol
            usd_rate = conversion_rates[symbol]
            dict_to_add = {
                'name': server_item.name,
                'symbol': symbol,
                'buy_amount': server_item.buy_amount,
                'buy_amount_USD': round(usd_rate * server_item.buy_amount, 1),
                'power': server_item.power,
                'power_USD': round(usd_rate * server_item.power, 1),
                'logo_path': server_item.logo_path,
                'category': server_item.category,
                'number_of_servers': user_server_instances_dict.get(f"{server_item.id}_buy", 0),
            }
            servers_list.append(dict_to_add)

        return servers_list

    @staticmethod
    def get_user_mining_server_details(server_id, user_id):
        """
        Get the details of a specific mining server type for a specific user
        """
        # Get the user's server details
        user_server_details = UserServer.query.filter_by(user_id=user_id, server_id=server_id).all()
        # Get the server details
        server_details = MiningServer.query.filter_by(id=server_id).first()
        # Get :
        # - Number of servers
        # - Compute the total buy amount
        # - Power
        # - Symbol

        output = {'number_of_servers': 0, 'total_buy_amount': 0,
                  'power': server_details.power, 'symbol': server_details.symbol,
                  'total_buy_amount_USD': 0, 'power_USD': 0}

        # Use caching for currency conversion
        @lru_cache(maxsize=None)
        def cached_convert_fct(currency_pair, amount):
            return round(CryptoDataManager().get_USD_from_crypto(currency_pair, amount), 1)

        output['power_USD'] = cached_convert_fct(server_details.symbol + '-USD', server_details.power)

        for server in user_server_details:
            output['number_of_servers'] += server.instances_number
            output['total_buy_amount'] += server.server.buy_amount * server.instances_number
            output['total_buy_amount_USD'] += cached_convert_fct(server.server.symbol + '-USD',
                                                                 server.server.buy_amount * server.instances_number)

        # round the values
        output['total_buy_amount'] = round(output['total_buy_amount'], 3)
        output['total_buy_amount_USD'] = round(output['total_buy_amount_USD'], 3)

        return output

    def buy_server(self, server_id, user_id, number_of_servers_to_buy):
        """
        Buy a server type:
        - Check if the user has enough crypto to buy the server
        - If yes, update the user's wallet
        - Create entry for each server bought
        """
        # Cast the number of servers to buy to int
        number_of_servers_to_buy = int(number_of_servers_to_buy)

        # Get the number of servers for this server type
        number_of_servers_bought = self.get_user_mining_server_details(server_id, user_id)['number_of_servers']
        # Test if the user has already bought the maximum number of servers for this server type
        if number_of_servers_bought + number_of_servers_to_buy > max_servers:
            return {'success': False, 'message': 'You will exceed the maximum number of bought servers for this '
                                                 'server type'}

        # Get the server details
        server_details = MiningServer.query.filter_by(id=server_id).first()
        # Get the user
        user = User.query.filter_by(id=user_id).first()
        # Get the user's wallet for the crypto symbol
        user_wallet = wallet_manager().get_user_specific_balance(user, server_details.symbol + '-USD')
        # Get the user's server details
        user_server_details = UserServer.query.filter_by(user_id=user_id, server_id=server_id).first()
        # Test if the user has enough crypto to buy the server with the quantity he wants
        if user_wallet['tokens'] >= server_details.buy_amount * number_of_servers_to_buy:
            # If yes, update the user's wallet
            wallet_manager().buy_with_crypto(user, server_details.symbol + '-USD',
                                             server_details.buy_amount * number_of_servers_to_buy)
            # Create entry or update the user's server details, then add an invoice (the user will instantly earn)
            period = datetime.now().strftime("%B %Y")
            issuer = user.username
            tomorrow = datetime.strptime((datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                                         "%Y-%m-%d").date()
            if user_server_details is None:
                new_server = UserServer(user_id=user_id, server_id=server_id,
                                        next_payment_date=None,
                                        next_earning_date=tomorrow,
                                        instances_number=number_of_servers_to_buy)
                db.session.add(new_server)
            else:
                user_server_details.instances_number += number_of_servers_to_buy

            today = datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d").date()

            self.add_invoice(user_id, period, issuer, today, server_details.buy_amount * number_of_servers_to_buy,
                             server_id, 'buy', number_of_servers_to_buy)

            # The user earns today
            wallet_manager().receive_crypto(user, server_details.symbol + '-USD',
                                            server_details.power * number_of_servers_to_buy)

            db.session.commit()

            return {'success': True, 'message': 'Server bought successfully'}
        else:
            return {'success': False, 'message': 'You do not have enough crypto to buy this server'}

    @staticmethod
    def sell_server(server_id, user_id, number_of_servers_to_sell):
        """
        Sell a server type
        """
        # Cast the number of servers to sell to int
        number_of_servers_to_sell = int(number_of_servers_to_sell)
        # Get the server details
        server_details = MiningServer.query.filter_by(id=server_id).first()
        # Get the user's server details (this is a list)
        user_server_details = UserServer.query.filter_by(user_id=user_id, server_id=server_id).all()
        # Filter the list to get only the servers that are currently bought
        user_server_details = [server for server in user_server_details]
        # Get the number of servers for this server type
        number_of_servers_bought = sum(server.instances_number for server in user_server_details)
        # Test if the user has enough servers to sell
        index_to_delete = 0
        if number_of_servers_bought < number_of_servers_to_sell:
            return {'success': False, 'message': 'You do not have enough servers to sell'}
        else:
            # While the number of servers to sell is not 0, continue to sell servers
            # for each server in user_server_details, we decrement the field instances_number by 1
            while number_of_servers_to_sell > 0:
                row = user_server_details[index_to_delete]
                # If the number of servers to sell is smaller than the field instances_number
                # we decrement the field instances_number by the number of servers to sell
                if row.instances_number > number_of_servers_to_sell:
                    row.instances_number -= number_of_servers_to_sell
                    number_of_servers_to_sell = 0
                # If the number of servers to sell is equal to the field instances_number
                # we delete the row
                elif row.instances_number == number_of_servers_to_sell:
                    number_of_servers_to_sell = 0
                    db.session.delete(row)
                # If the number of servers to sell is greater than the field instances_number
                # we delete the row and decrement the number of servers to sell by the field instances_number
                else:
                    number_of_servers_to_sell -= row.instances_number
                    db.session.delete(row)
                index_to_delete += 1

            # Refund the user
            wallet_manager().receive_crypto(User.query.filter_by(id=user_id).first(), server_details.symbol + '-USD',
                                            server_details.buy_amount * number_of_servers_to_sell)

            db.session.commit()

            return {'success': True, 'message': 'Server sold successfully'}

    @staticmethod
    def get_total_servers(user_id):
        """
        Get the total number of servers bought by a user
        """
        # Get the user's server details
        user_server_details = UserServer.query.filter_by(user_id=user_id).all()
        # The number of bought servers is the sum of the field instances_number for all servers
        n_number_of_servers_bought = sum(server.instances_number for server in user_server_details)
        return n_number_of_servers_bought

    @staticmethod
    def get_total_power(user_id):
        """
        Get the total power of the user's servers
        """
        # Get the user's server details
        user_server_details = UserServer.query.filter_by(user_id=user_id).all()

        # caching for currency conversion
        @lru_cache(maxsize=None)
        def cached_convert_fct(currency_pair, amount):
            return round(CryptoDataManager().get_USD_from_crypto(currency_pair, amount), 1)

        # Get conversion rate for all cryptos
        conversion_rates = {}
        for crypto in top_cryptos_symbols:
            conversion_rates[crypto] = cached_convert_fct(crypto, 1)

        # Get the total power
        total_power = 0
        for server in user_server_details:
            # convert power to USD
            power_in_usd = conversion_rates[server.server.symbol + '-USD'] * server.server.power
            total_power += power_in_usd * server.instances_number
        return total_power


def find_invoice(invoices_list, elem):
    for invoice in invoices_list:
        if all(invoice[key] == elem[key] for key in elem if key not in ['number_of_instances', 'amount']):
            return invoice
    return None
