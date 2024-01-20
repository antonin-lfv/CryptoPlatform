from models import MiningServer

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
