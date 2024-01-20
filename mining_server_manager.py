from models import MiningServer, UserServer


class Mining_server_manager:

    def __init__(self):
        ...

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
        Get the details of a specific mining server
        """
        # Get the user's server details
        user_server_details = UserServer.query.filter_by(user_id=user_id, server_id=server_id).all()
        # Get :
        # - Number of servers bought
        # - Number of servers rented
        # - Compute the total buy amount
        # - Compute the total rent amount per week
        # - Compute the total maintenance cost per week (bought servers only)
        output = {'number_of_servers_bought': 0, 'number_of_servers_rented': 0, 'total_buy_amount': 0,
                  'total_rent_amount_per_week': 0, 'total_maintenance_cost_per_week': 0}

        for server in user_server_details:
            if server.rent_start_date:
                output['number_of_servers_rented'] += 1
                output['total_rent_amount_per_week'] += server.server.rent_amount_per_week
            elif server.purchase_date:
                output['number_of_servers_bought'] += 1
                output['total_buy_amount'] += server.server.buy_amount
                output['total_maintenance_cost_per_week'] += server.server.maintenance_cost_per_week
        return output
