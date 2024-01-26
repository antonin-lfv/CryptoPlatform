from models import MiningServer, UserServer, User, ServerInvoices
from wallet_manager import wallet_manager
from crypto_manager import CryptoDataManager
from notification_manager import Notification_manager
from datetime import datetime, timedelta
from app import db


class Mining_server_manager:

    def __init__(self):
        ...

    def check_for_server_payment(self, user_id):
        """
        Iterate through all day, one by one, from the last payment date to today (the oldest of all servers).
        For each day, check if the user has servers that need to be paid.
        If yes, pay them.
        Also, earn crypto from mining.
        If not enough crypto, delete the server instance (so only for rent).
        """
        # Get the user
        user = User.query.filter_by(id=user_id).first()
        # Get the oldest server earning date
        oldest_earning_date_instance = (UserServer.query.filter_by(user_id=user_id)
                                        .order_by(UserServer.last_earning_date).first())
        # Number of servers deleted because not enough crypto
        number_of_servers_deleted = 0
        # Amount of USD earned
        USD_amount_earned = 0
        # Get the current date
        today_date = datetime.date(datetime.now())

        # If there is no server instance, return
        if oldest_earning_date_instance is None:
            print("[INFO]: No server instance")
            return

        # If oldest_earning_date is today, return
        if oldest_earning_date_instance.last_earning_date == today_date:
            print("[INFO]: Already paid today")
            return

        oldest_earning_date = oldest_earning_date_instance.last_earning_date

        # Iterate through all day, one by one, from the last payment date to today
        while oldest_earning_date <= today_date:
            print(f"[INFO]: oldest_earning_date: {oldest_earning_date}, today_date: {today_date}")
            # We start by earning crypto from mining then we pay the servers

            # == Bought servers earning ==
            bought_user_server_instances = UserServer.query.filter_by(user_id=user_id,
                                                                      last_earning_date=oldest_earning_date -
                                                                                        timedelta(days=1),
                                                                      rent_start_date=None
                                                                      ).all()
            print(f"[INFO]: number of bought_user_server_instances: {len(bought_user_server_instances)}")

            # Receive crypto from mining
            for server_instance in bought_user_server_instances:
                # Get the server details
                server_details = MiningServer.query.filter_by(id=server_instance.server_id).first()
                # Update the last earning date
                server_instance.last_earning_date = oldest_earning_date
                db.session.commit()
                # Update the user's wallet
                wallet_manager().receive_crypto(user, server_details.symbol + '-USD',
                                                server_details.power)
                USD_amount_earned += CryptoDataManager().get_USD_from_crypto(server_details.symbol + '-USD',
                                                                             server_details.power)
                print(
                    f"[INFO]: User {user_id} earned {server_details.power} {server_details.symbol} on {oldest_earning_date}")

            # == Rented servers earning ==
            rented_user_server_instances = UserServer.query.filter_by(user_id=user_id,
                                                                      last_earning_date=oldest_earning_date -
                                                                                        timedelta(days=1),
                                                                      purchase_date=None
                                                                      ).all()
            print(f"[INFO]: number of rented_user_server_instances: {len(rented_user_server_instances)}")

            # Receive crypto from mining
            for server_instance in rented_user_server_instances:
                # Get the server details
                server_details = MiningServer.query.filter_by(id=server_instance.server_id).first()
                # Update the last earning date
                server_instance.last_earning_date = oldest_earning_date
                db.session.commit()
                # Update the user's wallet
                wallet_manager().receive_crypto(user, server_details.symbol + '-USD',
                                                server_details.power)
                USD_amount_earned += CryptoDataManager().get_USD_from_crypto(server_details.symbol + '-USD',
                                                                             server_details.power)
                print(
                    f"[INFO]: User {user_id} earned {server_details.power} {server_details.symbol} on {oldest_earning_date}")

            # == Rented servers payment ==
            # Get the user's server instances that need to be paid
            rented_user_server_instances = UserServer.query.filter_by(user_id=user_id,
                                                                      last_payment_date=oldest_earning_date -
                                                                                        timedelta(days=7),
                                                                      purchase_date=None
                                                                      ).all()

            print(f"[INFO]: number of rented_user_server_instances: {len(rented_user_server_instances)}")

            # Iterate through all server instances
            for server_instance in rented_user_server_instances:
                # Get the server details
                server_details = MiningServer.query.filter_by(id=server_instance.server_id).first()
                # Get the user's wallet for the crypto symbol
                user_wallet = wallet_manager().get_user_specific_balance(user, server_details.symbol + '-USD')
                # Test if the user has enough crypto to pay the server
                if (user_wallet['tokens'] >= server_details.rent_amount_per_week +
                        server_details.maintenance_cost_per_week):
                    to_pay = server_details.rent_amount_per_week + server_details.maintenance_cost_per_week
                    # If yes, update the user's wallet
                    wallet_manager().buy_with_crypto(user, server_details.symbol + '-USD', to_pay)
                    # Update the last payment date
                    server_instance.last_payment_date = oldest_earning_date
                    db.session.commit()
                    print(
                        f"[INFO]: User {user_id} paid {server_details.rent_amount_per_week} {server_details.symbol} on "
                        f"{oldest_earning_date}")
                    # Add an invoice
                    # Period is Month + Year
                    print(f"[INFO]: Adding invoice for user_server_id {server_instance.id}")
                    period = oldest_earning_date.strftime("%B %Y")
                    issuer = user.username
                    due_date = oldest_earning_date + timedelta(days=7)
                    amount = to_pay
                    self.add_invoice(user_id, period, issuer, due_date, amount, server_instance.id, 'rent')
                    # Update USD_amount_earned
                    USD_amount_earned -= CryptoDataManager().get_USD_from_crypto(server_details.symbol + '-USD', to_pay)

                else:
                    # If not enough crypto, delete the server instance (so only for rent)
                    self.stop_renting_specific_server_instance(server_instance.id, user_id)
                    number_of_servers_deleted += 1
                    print(
                        f"[INFO]: User {user_id} didn't have enough crypto to pay {server_details.rent_amount_per_week} "
                        f"{server_details.symbol} on {oldest_earning_date}")

            # Update the last payment date
            oldest_earning_date += timedelta(days=1)

        if number_of_servers_deleted > 0:
            Notification_manager.add_notification(user_id,
                                                  f"{number_of_servers_deleted} server(s) deleted due to not "
                                                  f"enough crypto to afford rent",
                                                  f"warning")

        # Create notification for the amount earned
        if USD_amount_earned > 0:
            Notification_manager.add_notification(user_id,
                                                  f"You earned {round(USD_amount_earned, 2)} USD from mining",
                                                  f"shopping-cart")

    @staticmethod
    def get_user_mining_servers_invoices(user, server_name):
        """
        Get the invoices for a user
        """
        # Get the server type id
        server_type_id = MiningServer.query.filter_by(name=server_name).first().id
        # Get the invoices for this server type
        user_server_type_invoices = ServerInvoices.query.filter_by(server_id=server_type_id, user_id=user.id).all()
        invoices_list = []
        for invoice in user_server_type_invoices:
            elem = {
                'period': invoice.period,
                'issuer': invoice.issuer,
                'due_date': invoice.due_date,
                'amount': invoice.amount,
                'type_payment': invoice.type_payment,
                'server_name': server_name,
                'number_of_instances': 1,
            }

            existing_invoice = find_invoice(invoices_list, elem)
            if existing_invoice:
                existing_invoice['amount'] += elem['amount']
                existing_invoice['number_of_instances'] += 1
            else:
                invoices_list.append(elem)

        return invoices_list

    @staticmethod
    def add_invoice(user_id, period, issuer, due_date, amount, server_id, type_payment):
        """
        Add an invoice to the database
        """
        print(f"[INFO]: Adding invoice for server_id {server_id}")
        invoice = ServerInvoices(period=period, issuer=issuer, due_date=due_date, amount=amount,
                                 server_id=server_id, type_payment=type_payment, user_id=user_id)
        db.session.add(invoice)
        db.session.commit()

    @staticmethod
    def get_all_servers():
        """
        Get all mining servers from the database

        Return:
            dict
        """
        servers = MiningServer.query.all()
        # Create a dict with all NFTs
        servers_list = []
        for server_item in servers:
            servers_list.append({
                'name': server_item.name,
                'symbol': server_item.symbol,
                'rent_amount_per_week': server_item.rent_amount_per_week,
                'buy_amount': server_item.buy_amount,
                'power': server_item.power,
                'maintenance_cost_per_week': server_item.maintenance_cost_per_week,
                'logo_path': server_item.logo_path,
                'category': server_item.category
            })

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
        # - Number of servers bought
        # - Number of servers rented
        # - Compute the total buy amount
        # - Compute the total rent amount per week
        # - Compute the total maintenance cost per week (bought servers only)
        # - Power
        # - Symbol
        output = {'number_of_servers_bought': 0, 'number_of_servers_rented': 0, 'total_buy_amount': 0,
                  'total_rent_amount_per_week': 0, 'total_maintenance_cost_per_week': 0,
                  'power': server_details.power, 'symbol': server_details.symbol}

        for server in user_server_details:
            if server.rent_start_date:
                output['number_of_servers_rented'] += 1
                output['total_rent_amount_per_week'] += server.server.rent_amount_per_week
                output['total_maintenance_cost_per_week'] += server.server.maintenance_cost_per_week
            elif server.purchase_date:
                output['number_of_servers_bought'] += 1
                output['total_buy_amount'] += server.server.buy_amount
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
        # Get the server details
        server_details = MiningServer.query.filter_by(id=server_id).first()
        # Get the user
        user = User.query.filter_by(id=user_id).first()
        # Get the user's wallet for the crypto symbol
        user_wallet = wallet_manager().get_user_specific_balance(user, server_details.symbol + '-USD')
        # Test if the user has enough crypto to buy the server with the quantity he wants
        if user_wallet['tokens'] >= server_details.buy_amount * number_of_servers_to_buy:
            # If yes, update the user's wallet
            wallet_manager().buy_with_crypto(user, server_details.symbol + '-USD', server_details.buy_amount)
            # Create entry for each server bought
            period = datetime.now().strftime("%B %Y")
            issuer = user.username
            due_date = datetime.now().strftime("%Y-%m-%d")
            # We set last_earning_date to yesterday so the user will earn crypto the day when he buys the server
            for i in range(number_of_servers_to_buy):
                user_server_details = UserServer(user_id=user_id, server_id=server_id,
                                                 purchase_date=datetime.date(datetime.now()),
                                                 last_earning_date=datetime.date(datetime.now()) - timedelta(days=1))
                db.session.add(user_server_details)
                # Add an invoice for this first payment
                amount = server_details.buy_amount
                self.add_invoice(user_id, period, issuer, due_date, amount, server_id, 'buy')

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
        user_server_details = UserServer.query.filter_by(user_id=user_id,
                                                         server_id=server_id).all()
        # Filter the list to get only the servers that are currently bought
        user_server_details = [server for server in user_server_details if server.purchase_date is not None]
        # Sort the list by purchase_date to get the oldest first
        user_server_details.sort(key=lambda x: x.purchase_date)
        # Get the user
        user = User.query.filter_by(id=user_id).first()
        # Test if the user has enough servers to sell
        if len(user_server_details) >= number_of_servers_to_sell:
            # If yes, update the user's wallet
            wallet_manager().receive_crypto(user, server_details.symbol + '-USD', server_details.buy_amount)
            # Delete entry for each server sold
            for i in range(number_of_servers_to_sell):
                db.session.delete(user_server_details[i])
            db.session.commit()

            return {'success': True, 'message': 'Server sold successfully'}
        else:
            return {'success': False, 'message': 'You do not have enough servers to sell'}

    def rent_server(self, server_id, user_id, number_of_servers_to_rent):
        """
        Rent a server type
        """
        # Cast the number of servers to rent to int
        number_of_servers_to_rent = int(number_of_servers_to_rent)
        # Get the server details
        server_details = MiningServer.query.filter_by(id=server_id).first()
        # Get the user
        user = User.query.filter_by(id=user_id).first()
        # Get the user's wallet for the crypto symbol
        user_wallet = wallet_manager().get_user_specific_balance(user, server_details.symbol + '-USD')
        # Test if the user has enough crypto to rent the server with the quantity he wants
        if (user_wallet['tokens'] >= (server_details.rent_amount_per_week + server_details.maintenance_cost_per_week) *
                number_of_servers_to_rent):
            # If yes, update the user's wallet
            # The user pay immediately for the servers for the next week (add maintenance cost)
            wallet_manager().buy_with_crypto(user, server_details.symbol + '-USD',
                                             (server_details.rent_amount_per_week +
                                              server_details.maintenance_cost_per_week) * number_of_servers_to_rent)
            # Create entry for each server rented
            for i in range(number_of_servers_to_rent):
                # We set last_earning_date to yesterday so the user will earn crypto the day when he rents the server
                user_server_details = UserServer(user_id=user_id, server_id=server_id,
                                                 rent_start_date=datetime.date(datetime.now()),
                                                 last_payment_date=datetime.date(datetime.now()),
                                                 last_earning_date=datetime.date(datetime.now()) - timedelta(days=1))
                db.session.add(user_server_details)
                # Add an invoice for this first payment
                period = datetime.now().strftime("%B %Y")
                issuer = user.username
                due_date = datetime.now().strftime("%Y-%m-%d")
                amount = server_details.rent_amount_per_week + server_details.maintenance_cost_per_week
                self.add_invoice(user_id, period, issuer, due_date, amount, server_id, 'rent')

            db.session.commit()

            return {'success': True, 'message': 'Server rented successfully'}
        else:
            return {'success': False, 'message': 'You do not have enough crypto to rent this server'}

    @staticmethod
    def stop_renting_server(server_id, user_id, number_of_servers_to_stop_renting):
        """
        Stop renting a server type
        """
        # Cast the number of servers to stop renting to int
        number_of_servers_to_stop_renting = int(number_of_servers_to_stop_renting)
        # Get the server details
        server_details = MiningServer.query.filter_by(id=server_id).first()
        # Get the user
        user = User.query.filter_by(id=user_id).first()
        # Get the user's server details (sort them buy last_payment_date to get the oldest first)
        user_server_details = UserServer.query.filter_by(user_id=user_id,
                                                         server_id=server_id).all()
        # Filter the list to get only the servers that are currently rented
        user_server_details = [server for server in user_server_details if server.rent_start_date is not None]
        # get user server details that did not earn anything
        user_server_details_no_earning = [server for server in user_server_details if
                                          server.last_earning_date is None]
        # Sort the list by last_payment_date to get the oldest first (except if last_earning_date is None)
        user_server_details_sort_by_last_payment = [serv_details for serv_details in user_server_details if
                                                    serv_details.last_earning_date is not None]
        user_server_details_sort_by_last_payment.sort(key=lambda x: x.last_payment_date)
        # Concat, so we will delete the oldest first
        user_server_details = user_server_details_sort_by_last_payment + user_server_details_no_earning

        # Test if the user has enough servers to stop renting
        if len(user_server_details) >= number_of_servers_to_stop_renting:
            # Delete entry for each server stopped renting
            for i in range(number_of_servers_to_stop_renting):
                # If the user didn't earn anything, we refund the full amount
                if user_server_details[i].last_earning_date is None:
                    amount_to_refund = server_details.rent_amount_per_week + server_details.maintenance_cost_per_week
                    # Update the user's wallet
                    wallet_manager().receive_crypto(user, server_details.symbol + '-USD', amount_to_refund)
                db.session.delete(user_server_details[i])
            db.session.commit()

            return {'success': True, 'message': 'Server stopped renting successfully'}
        else:
            return {'success': False, 'message': 'You do not have enough servers to stop renting'}

    @staticmethod
    def stop_renting_specific_server_instance(server_instance_id, user_id):
        """
        Stop renting a specific instance of a server type.
        Refund the user if he didn't earn anything. Else, he will not be refunded.
        """
        # Get the server instance details
        server_instance_details = UserServer.query.filter_by(id=server_instance_id).first()
        # Get the server details
        server_details = MiningServer.query.filter_by(id=server_instance_details.server_id).first()
        # Get the user
        user = User.query.filter_by(id=user_id).first()
        # If the user didn't earn anything, we refund the full amount
        if server_instance_details.last_earning_date is None:
            print("User didn't earn anything")
            amount_to_refund = server_details.rent_amount_per_week + server_details.maintenance_cost_per_week
            # Update the user's wallet
            print(f"Amount to refund: {amount_to_refund}")
            wallet_manager().receive_crypto(user, server_details.symbol + '-USD', amount_to_refund)
        db.session.delete(server_instance_details)
        db.session.commit()

        return {'success': True, 'message': 'Server stopped renting successfully'}


def find_invoice(invoices_list, elem):
    for invoice in invoices_list:
        if all(invoice[key] == elem[key] for key in elem if key not in ['number_of_instances', 'amount']):
            return invoice
    return None
