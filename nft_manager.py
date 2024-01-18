from models import NFT


class NFT_manager:
    def __init__(self):
        ...

    def get_NFTs(self, collection=None):
        """
        Get all NFTs from the marketplace

        Return:
            dict
        """
        if collection is None:
            return self.get_all_NFT()
        else:
            return self.get_collection_NFT(collection)

    @staticmethod
    def get_all_NFT():
        """
        Get all NFTs from the marketplace

        Return:
            dict
        """
        NFTs = NFT.query.all()
        # Create a dict with all NFTs
        NFTs_list = []
        for nft_item in NFTs:
            NFTs_list.append({
                'name': nft_item.name,
                'collection': nft_item.collection,
                'price': nft_item.price,
                'image_path': nft_item.image_path,
                'is_for_sale': nft_item.is_for_sale,
                'is_for_sale_since': nft_item.is_for_sale_since,
                'is_for_sale_until': nft_item.is_for_sale_until,
                'owner_id': nft_item.owner_id,
            })

        print(f"Length of NFTs_list: {len(NFTs_list)}")

        return NFTs_list

    @staticmethod
    def get_collection_NFT(collection):
        """
        Get all NFTs from the marketplace

        Return:
            dict
        """
        NFTs = NFT.query.filter_by(collection=collection).all()
        # Create a dict with all NFTs
        NFTs_list = []
        for nft_item in NFTs:
            NFTs_list.append({
                'name': nft_item.name,
                'collection': nft_item.collection,
                'price': nft_item.price,
                'image_path': nft_item.image_path,
                'is_for_sale': nft_item.is_for_sale,
                'is_for_sale_since': nft_item.is_for_sale_since,
                'is_for_sale_until': nft_item.is_for_sale_until,
                'owner_id': nft_item.owner_id,
            })

        print(f"Length of NFTs_list: {len(NFTs_list)}")

        return NFTs_list
