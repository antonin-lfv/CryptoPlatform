from models import MiningServer, UserServer, User
from wallet_manager import wallet_manager
from datetime import datetime
from app import db


class Mining_server_manager:

    def __init__(self):
        ...

    @staticmethod
    def check_for_server_payment(user_id):
        """
        Check for all servers if :
        - the user has to pay for them (if last_payment_date is more than 7 days ago)
        - the user has enough crypto to pay for them (if yes, pay for them, else, sell them until he has enough crypto)
        - the user has to get paid for them (if last_earning_date is more than 1 day ago)

        Careful: this function can be call many weeks after the last time it was called, so we have to check for
        multiple weeks. If the user didn't pay for 2 weeks, we have to sell 2 weeks of servers. If he can just afford
        1 week, we have to sell 1 week of servers and stop renting the other week. But don't forget the earning part
        each day.
        """
        # TODO

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

        print(f"Length of servers_list: {len(servers_list)}")

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

    @staticmethod
    def buy_server(server_id, user_id, number_of_servers_to_buy):
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
        print(f"You want to buy {number_of_servers_to_buy} servers and you have {user_wallet['tokens']}")
        # Test if the user has enough crypto to buy the server with the quantity he wants
        if user_wallet['tokens'] >= server_details.buy_amount * number_of_servers_to_buy:
            # If yes, update the user's wallet
            wallet_manager().buy_with_crypto(user, server_details.symbol + '-USD', server_details.buy_amount)
            # Create entry for each server bought
            for i in range(number_of_servers_to_buy):
                user_server_details = UserServer(user_id=user_id, server_id=server_id, purchase_date=datetime.now())
                db.session.add(user_server_details)

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

    @staticmethod
    def rent_server(server_id, user_id, number_of_servers_to_rent):
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
            wallet_manager().buy_with_crypto(user, server_details.symbol + '-USD', (server_details.rent_amount_per_week +
                                             server_details.maintenance_cost_per_week)*number_of_servers_to_rent)
            # Create entry for each server rented
            for i in range(number_of_servers_to_rent):
                # We set last_earning_date to None because the user will earn the next day (Next the last_payment_date)
                user_server_details = UserServer(user_id=user_id, server_id=server_id, rent_start_date=datetime.now(),
                                                 last_payment_date=datetime.now())
                db.session.add(user_server_details)

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
        user_server_details.sort(key=lambda x: x.rent_start_date)
        # Test if the user has enough servers to stop renting
        if len(user_server_details) >= number_of_servers_to_stop_renting:
            # Delete entry for each server stopped renting
            for i in range(number_of_servers_to_stop_renting):
                # The user wallet is refunded depending on the last payment date
                # Get the number of days since the last payment
                number_of_days_since_last_payment = (datetime.now() - user_server_details[i].last_payment_date).days
                # Compute the amount to refund
                amount_to_refund = ((server_details.rent_amount_per_week + server_details.maintenance_cost_per_week) /
                                    7 * number_of_days_since_last_payment)
                # If the user didn't earn anything, we refund the full amount
                if user_server_details[i].last_earning_date is None:
                    print("User didn't earn anything")
                    amount_to_refund = server_details.rent_amount_per_week + server_details.maintenance_cost_per_week
                # Update the user's wallet
                print(f"Amount to refund: {amount_to_refund}")
                wallet_manager().receive_crypto(user, server_details.symbol + '-USD', amount_to_refund)
                db.session.delete(user_server_details[i])
            db.session.commit()

            return {'success': True, 'message': 'Server stopped renting successfully'}
        else:
            return {'success': False, 'message': 'You do not have enough servers to stop renting'}

    @staticmethod
    def stop_renting_specific_server_instance(server_instance_id, user_id):
        """
        Stop renting a specific instance of a server type
        """
        # Get the server instance details
        server_instance_details = UserServer.query.filter_by(id=server_instance_id).first()
        # Get the server details
        server_details = MiningServer.query.filter_by(id=server_instance_details.server_id).first()
        # Get the user
        user = User.query.filter_by(id=user_id).first()
        # Get the number of days since the last payment
        number_of_days_since_last_payment = (datetime.now() - server_instance_details.last_payment_date).days
        # Compute the amount to refund
        amount_to_refund = ((server_details.rent_amount_per_week + server_details.maintenance_cost_per_week) /
                            7 * number_of_days_since_last_payment)
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
