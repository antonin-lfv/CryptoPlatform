from models import NFT, UserLikedNFT, User, UserNFT
from app import db
from wallet_manager import wallet_manager
from crypto_manager import CryptoDataManager
from datetime import datetime
from utils import user_profile_default_image_path


class NFT_manager:
    def __init__(self):
        """
        All NFT are in ETH
        """
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
                'price_usd': round(CryptoDataManager().get_USD_from_crypto('ETH-USD', NFTs.price), 3),
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

    @staticmethod
    def get_owned_NFTs(user_id):
        """
        Get all NFTs owned by the user

        Return:
            dict
        """
        # Get all the NFTs owned by the user
        nft_ids = UserNFT.query.filter_by(user_id=user_id).all()
        # Create a list with all the nft_id owned by the user
        nft_ids_list = [nft_id.nft_id for nft_id in nft_ids]
        # Get all the NFTs owned by the user
        nft_owned_list = []
        for nft_id in nft_ids_list:
            nft_owned_list.append(NFT_manager().get_NFT(nft_id, user_id))

        return nft_owned_list

    @staticmethod
    def buy_NFT(user_id, nft_id):
        """
        Buy a NFT
        """
        # Get user wallet
        user = User.query.filter_by(id=user_id).first()
        wallet = wallet_manager()
        eth_amount = wallet.get_user_specific_balance(user, 'ETH-USD')
        # Get the NFT price
        nft = NFT.query.filter_by(id=nft_id).first()
        nft_price = nft.price
        # Check if the user has enough ETH to buy the NFT
        if nft.is_for_sale:
            if eth_amount['tokens'] < nft_price:
                return {"status": "error", "message": "Not enough ETH in the wallet"}
            else:
                # Transfer the NFT to the user
                user_nft = UserNFT(user_id=user_id, nft_id=nft_id,
                                   purchase_price_usd=CryptoDataManager().get_USD_from_crypto('ETH-USD', nft_price),
                                   purchase_price_crypto=nft_price, purchase_crypto_symbol='ETH')
                db.session.add(user_nft)
                # Update the NFT object
                nft.is_for_sale = False
                nft.owner_id = user_id
                nft.is_for_sale_since = None
                nft.is_for_sale_until = None
                db.session.commit()
                # Buy the NFT with ETH
                wallet.buy_with_crypto(user, 'ETH-USD', nft_price)
                return {"status": "success", "message": "You bought the NFT successfully"}
        else:
            return {"status": "error", "message": "The NFT is not for sale"}

    @staticmethod
    def sell_NFT(user_id, nft_id):
        """
        Sell a NFT
        """
        # Get the NFT
        nft = NFT.query.filter_by(id=nft_id).first()
        # Get the user
        user = User.query.filter_by(id=user_id).first()
        # Check if the NFT is owned by the user
        if nft.owner_id != user_id:
            return {"status": "error", "message": "You don't own this NFT",
                    "image_path": user_profile_default_image_path}
        else:
            # Update the NFT object
            nft.is_for_sale = True
            nft.is_for_sale_since = datetime.utcnow()
            nft.is_for_sale_until = None
            nft.owner_id = None
            # Delete the NFT from the user
            UserNFT.query.filter_by(user_id=user_id, nft_id=nft_id).delete()
            # Reset the profile picture if the NFT was the profile picture
            if user.profile_img_path == nft.image_path:
                user.profile_img_path = user_profile_default_image_path
            # Sell the NFT with ETH
            wallet_manager().receive_crypto(user, 'ETH-USD', nft.price)
            db.session.commit()
            return {"status": "success", "message": "The NFT is now for sale",
                    "image_path": user_profile_default_image_path}

    @staticmethod
    def owned_status(user_id, nft_id):
        """
        Check if the user owns the NFT
        """
        # Get the NFT
        nft = NFT.query.filter_by(id=nft_id).first()
        # Get the user
        user = User.query.filter_by(id=user_id).first()
        nft_used_for_profile_picture = user.profile_img_path == nft.image_path
        # Check if the NFT is owned by the user
        if nft.owner_id == user_id:
            return {"message": "You own this NFT", "owned": True,
                    "set_profile_text": "Reset profile picture" if nft_used_for_profile_picture
                    else "Set as profile picture"}
        if nft.owner_id is None:
            return {"message": "Not owned", "owned": False, "set_profile_text": None}
        else:
            # Get the name of the owner
            owner = User.query.filter_by(id=nft.owner_id).first()
            return {"message": f"NFT owned by {owner.username}", "owned": False, "set_profile_text": None}

    @staticmethod
    def set_as_profile_picture(user_id, nft_id):
        """
        Set a NFT as profile picture
        """
        # Get the NFT
        nft = NFT.query.filter_by(id=nft_id).first()
        # Get the user
        user = User.query.filter_by(id=user_id).first()
        # Check if the NFT is owned by the user
        if nft.owner_id != user_id:
            return {"status": "error", "message": "You don't own this NFT"}
        else:
            # if the NFT is the profile picture, reset the profile picture
            if user.profile_img_path == nft.image_path:
                user.profile_img_path = user_profile_default_image_path
                db.session.commit()
                return {"status": "success", "message": "The NFT is not your profile picture anymore",
                        "image_path": user_profile_default_image_path}
            else:
                # Set the NFT as profile picture
                user.profile_img_path = nft.image_path
                db.session.commit()
                return {"status": "success",
                        "message": "The NFT is now your profile picture", "image_path": nft.image_path}
