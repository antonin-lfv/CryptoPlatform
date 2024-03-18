from models import NFT, UserLikedNFT
from app import db


class NFT_manager:
    def __init__(self):
        ...

    def get_NFTs(self, user_id, collection=None):
        """
        Get all NFTs from the marketplace

        Return:
            dict
        """
        if collection is None:
            return self.get_all_NFT(user_id)
        else:
            return self.get_collection_NFT(user_id, collection=collection)

    @staticmethod
    def get_NFT(nft_id, user_id):
        """
        Get a NFT from the marketplace

        Return:
            dict of the NFT
        """
        # Get the NFT
        NFTs = NFT.query.filter_by(id=nft_id).first()
        # get the liked status of the NFT
        liked = UserLikedNFT.query.filter_by(nft_id=nft_id).all()
        is_user_liked = user_id in [l.user_id for l in liked]
        if NFTs:
            # Create a dict with all NFTs
            nft_data = {
                'id': NFTs.id,
                'name': NFTs.name,
                'collection': NFTs.collection,
                'price': NFTs.price,
                'image_path': NFTs.image_path,
                'is_for_sale': NFTs.is_for_sale,
                'is_for_sale_since': NFTs.is_for_sale_since,
                'is_for_sale_until': NFTs.is_for_sale_until,
                'owner_id': NFTs.owner_id,
                'liked': '' if is_user_liked else '-o',
                'number_of_likes': len(liked) if liked else 0
            }

            return nft_data
        else:
            return []

    @staticmethod
    def get_all_NFT(user_id):
        """
        Get all NFTs from the marketplace

        Return:
            dict
        """
        # Get all NFTs
        NFTs = NFT.query.all()
        # Get all the NFTs liked by the user
        nft_ids = UserLikedNFT.query.filter_by(user_id=user_id).all()
        # Create a dict with all NFTs
        NFTs_list = []
        for nft_item in NFTs:
            NFTs_list.append({
                'id': nft_item.id,
                'name': nft_item.name,
                'collection': nft_item.collection,
                'price': nft_item.price,
                'image_path': nft_item.image_path,
                'is_for_sale': nft_item.is_for_sale,
                'is_for_sale_since': nft_item.is_for_sale_since,
                'is_for_sale_until': nft_item.is_for_sale_until,
                'owner_id': nft_item.owner_id,
                'liked': '' if nft_item.id in [n.nft_id for n in nft_ids] else '-o'
            })

        return NFTs_list

    @staticmethod
    def get_collection_NFT(user_id, collection):
        """
        Get all NFTs from the marketplace

        Return:
            dict
        """
        # Get all NFTs of the collection
        NFTs = NFT.query.filter_by(collection=collection).all()
        # Get all the NFTs liked by the user
        nft_ids = UserLikedNFT.query.filter_by(user_id=user_id).all()
        # Create a dict with all NFTs
        NFTs_list = []
        for nft_item in NFTs:
            NFTs_list.append({
                'id': nft_item.id,
                'name': nft_item.name,
                'collection': nft_item.collection,
                'price': nft_item.price,
                'image_path': nft_item.image_path,
                'is_for_sale': nft_item.is_for_sale,
                'is_for_sale_since': nft_item.is_for_sale_since,
                'is_for_sale_until': nft_item.is_for_sale_until,
                'owner_id': nft_item.owner_id,
                'liked': '' if nft_item.id in [n.nft_id for n in nft_ids] else '-o'
            })

        return NFTs_list

    def get_liked_NFTs(self, user_id):
        """
        Get all NFTs liked by the user

        Return:
            dict
        """
        # There is a table user_liked_nft with user_id and nft_id fields
        # Get all the nft_id liked by the user
        nft_ids = UserLikedNFT.query.filter_by(user_id=user_id).all()
        # Create a list with all the nft_id liked by the user
        nft_ids_list = [nft_id.nft_id for nft_id in nft_ids]
        # Get all the NFTs liked by the user
        nft_liked_list = []
        for nft_id in nft_ids_list:
            nft_liked_list.append(self.get_NFT(nft_id, user_id))

        return nft_liked_list

    @staticmethod
    def like_NFT(user_id, nft_id):
        """
        Like a NFT (or unlike if already liked)

        Return:
            json
        """
        # Check if the user already liked the NFT
        if UserLikedNFT.query.filter_by(user_id=user_id, nft_id=nft_id).first() is not None:
            # The user already liked the NFT, so we delete the like
            UserLikedNFT.query.filter_by(user_id=user_id, nft_id=nft_id).delete()
        else:
            # Add the like to the database
            user_liked_nft = UserLikedNFT(user_id=user_id, nft_id=nft_id)
            db.session.add(user_liked_nft)

        db.session.commit()

        return {"status": "success"}
