from models import NFT, UserLikedNFT, User, UserNFT, NFTBid, CryptoPrice, NFTPriceOwnerHistory
from flask import url_for
from app import db
from wallet_manager import wallet_manager
from crypto_manager import CryptoDataManager
from notification_manager import Notification_manager
from datetime import datetime
from utils import user_profile_default_image_path
import os
from utils import NFT_collections, core_url_NFT, collection_to_min_max_price
import random
import math


class NFT_manager:
    def __init__(self):
        """
        All NFT are in ETH
        """
        ...

    @staticmethod
    def update_NFT_price():
        print("[INFO] Updating NFT prices")
        last_days = CryptoPrice.query.filter_by(symbol='ETH-USD').order_by(
            CryptoPrice.id.desc()).limit(2).all()
        if len(last_days) < 2:
            print("[ERROR] Insufficient data to update NFT prices")
            return

        # Compute the percentage change of the ETH price
        eth_price_old = last_days[-1].price
        eth_price_new = last_days[0].price
        if eth_price_old == 0:
            print("[ERROR] Previous ETH price is zero, cannot calculate percentage change")
            return

        # difference between the two days for the NFT
        eth_price_change_usd = eth_price_new - eth_price_old

        nfts = NFT.query.all()
        for nft in nfts:
            # Update the price_change_24h of the NFT
            nft.price_change_24h = round(eth_price_change_usd * nft.price, 3)

        db.session.commit()

    @staticmethod
    def refresh_NFT_base(user_id):
        """
        ADMIN FUNCTION
        Refresh the NFT base of the app
        :param user_id: to verify if the user is an admin
        """
        # Vérification de l'utilisateur admin
        user = User.query.filter_by(id=user_id).first()
        if user is None or user.role != 'ADMIN':
            return {"status": "error", "message": "You are not an admin"}

        # Configuration initiale
        existing_nfts = {nft.image_path: nft for nft in NFT.query.all()}  # Un dictionnaire pour une recherche rapide

        # Parcourir chaque collection
        n_NFT_refreshed = 0
        for collection in NFT_collections:
            collection_path = core_url_NFT + collection.lower() + '/'
            abs_path = os.path.join('assets', collection_path.strip('/'))  # Assurez-vous que le chemin est correct
            if not os.path.exists(abs_path):
                continue  # Si le chemin n'existe pas, passer à la collection suivante
            # Parcourir les fichiers dans le dossier de la collection
            for filename in os.listdir(abs_path):
                if not filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.jpeg'):
                    continue
                file_path = os.path.join(collection_path, filename)
                if file_path not in existing_nfts.keys():
                    # Si l'image n'est pas déjà dans la base, l'ajouter
                    name = f"{collection} #{filename.split('_')[-1].split('.')[0]}"
                    price = round(collection_to_min_max_price[collection][0] +
                                  (collection_to_min_max_price[collection][1] -
                                   collection_to_min_max_price[collection][0]) * (1 - math.exp(-5 * random.random())),
                                  3)
                    nft = NFT(name=name, collection=collection, image_path=file_path, price=price, owner_id=None,
                              price_change_24h=0)
                    db.session.add(nft)

                    n_NFT_refreshed += 1

        db.session.commit()
        return {"status": "success", "message": f"NFT base refreshed successfully - {n_NFT_refreshed} NFTs added"}

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
    def get_number_of_NFTs_user(user_id):
        """
        Get the number of NFTs owned by a user

        Return:
            int
        """
        return len(UserNFT.query.filter_by(user_id=user_id).all())

    @staticmethod
    def get_number_of_bids_user(user_id):
        """
        Get the number of bids placed by a user

        Return:
            int
        """
        return len(NFTBid.query.filter_by(user_id=user_id).all())

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
            price_usd = round(CryptoDataManager().get_USD_from_crypto('ETH-USD', NFTs.price), 2)
            nft_data = {
                'id': NFTs.id,
                'name': NFTs.name,
                'collection': NFTs.collection,
                'price': NFTs.price,
                'price_usd': price_usd,
                'price_usd_format': "{:,}".format(price_usd),
                'image_path': NFTs.image_path,
                'is_for_sale': NFTs.is_for_sale,
                'owner_id': NFTs.owner_id,
                'owned': NFTs.owner_id == user_id,
                'liked': '' if is_user_liked else '-o',
                'number_of_likes': len(liked) if liked else 0,
                'views_number': NFTs.views_number,
                'price_change_24h': round(NFTs.price_change_24h, 2)
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
        # Sort by collection in the same order as the NFT_collections list
        NFTs = sorted(NFTs, key=lambda x: NFT_collections.index(x.collection))
        # Get all the NFTs liked by the user
        nft_ids = UserLikedNFT.query.filter_by(user_id=user_id).all()
        # Get the number of likes for each NFT
        nft_likes = UserLikedNFT.query.all()
        number_of_likes = {}
        for nft_id in nft_likes:
            if nft_id.nft_id in number_of_likes:
                number_of_likes[nft_id.nft_id] += 1
            else:
                number_of_likes[nft_id.nft_id] = 1
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
                'owner_id': nft_item.owner_id,
                'owned': nft_item.owner_id == user_id,
                'liked': '' if nft_item.id in [n.nft_id for n in nft_ids] else '-o',
                'number_of_likes': number_of_likes[nft_item.id] if nft_item.id in number_of_likes else 0,
                'views_number': nft_item.views_number,
                'price_change_24h': round(nft_item.price_change_24h, 2)
            })

        return NFTs_list

    def get_user_NFTs(self, user_id, current_user_id):
        """
        Get all NFTs from the user

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
            nft_owned_list.append(self.get_NFT(nft_id, current_user_id))

        # Sort by collection
        nft_owned_list = sorted(nft_owned_list, key=lambda x: x['collection'])

        return nft_owned_list

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
        # Get the number of likes for each NFT
        nft_likes = UserLikedNFT.query.all()
        number_of_likes = {}
        for nft_id in nft_likes:
            if nft_id.nft_id in number_of_likes:
                number_of_likes[nft_id.nft_id] += 1
            else:
                number_of_likes[nft_id.nft_id] = 1
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
                'owner_id': nft_item.owner_id,
                'owned': nft_item.owner_id == user_id,
                'liked': '' if nft_item.id in [n.nft_id for n in nft_ids] else '-o',
                'number_of_likes': number_of_likes[nft_item.id] if nft_item.id in number_of_likes else 0,
                'views_number': nft_item.views_number,
                'price_change_24h': round(nft_item.price_change_24h, 2)
            })

        # Sort by price
        NFTs_list = sorted(NFTs_list, key=lambda x: x['price'])

        return NFTs_list

    @staticmethod
    def get_collection_details(collection):
        # Get details of a collection
        # - Name
        # - Number of NFTs
        # - Floor price
        # - Ceiling price
        # - Average price
        # - Total volume
        # - Number of owners (unique)
        collection_details = {
            'name': collection,
        }
        # Get all NFTs of the collection
        NFTs = NFT.query.filter_by(collection=collection).all()
        # Get the number of NFTs
        collection_details['number_of_NFTs'] = len(NFTs)
        # Get the floor price
        floor_price = min([nft.price for nft in NFTs])
        collection_details['floor_price'] = round(floor_price, 2)
        # Get the average price
        average_price = sum([nft.price for nft in NFTs]) / len(NFTs)
        collection_details['average_price'] = round(average_price, 2)
        # Get the total volume
        total_volume = sum([nft.price for nft in NFTs])
        collection_details['total_volume'] = round(total_volume, 2)
        # Get the number of owners
        owners = list(set([nft.owner_id for nft in NFTs if nft.owner_id is not None]))
        collection_details['number_of_owners'] = len(owners)

        return collection_details

    @staticmethod
    def get_NFTS_preview(collection, nft_id):
        """
        Get all NFTs from the marketplace

        Return:
            dict
        """
        # Get all NFTs of the collection
        NFTs = NFT.query.filter_by(collection=collection).all()
        # Get all the NFTs liked by the user
        nft_ids = UserLikedNFT.query.filter_by(nft_id=nft_id).all()
        # Get the number of likes for each NFT
        nft_likes = UserLikedNFT.query.all()
        number_of_likes = {}
        for nft_id_ in nft_likes:
            if nft_id_.nft_id in number_of_likes:
                number_of_likes[nft_id_.nft_id] += 1
            else:
                number_of_likes[nft_id_.nft_id] = 1
        # Create a dict with all NFTs
        NFTs_list = []
        for nft_item in NFTs:
            if nft_item.id != int(nft_id):
                NFTs_list.append({
                    'id': nft_item.id,
                    'name': nft_item.name,
                    'collection': nft_item.collection,
                    'price': nft_item.price,
                    'image_path': nft_item.image_path,
                    'is_for_sale': nft_item.is_for_sale,
                    'owner_id': nft_item.owner_id,
                    'liked': '' if nft_item.id in [n.nft_id for n in nft_ids] else '-o',
                    'number_of_likes': number_of_likes[nft_item.id] if nft_item.id in number_of_likes else 0,
                    'views_number': nft_item.views_number
                })

        # Pick 4 random NFTs
        random.shuffle(NFTs_list)
        NFTs_list = NFTs_list[:4]

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
        nft_liked_list = [self.get_NFT(nft_id, user_id) for nft_id in nft_ids_list]

        return nft_liked_list

    def get_bids_NFTs(self, user_id):
        """
        Get all NFTs where the user placed a bid

        Return:
            dict
        """
        # Get all the bids of the user
        nft_bids = NFTBid.query.filter_by(user_id=user_id).all()
        # Create a list with all the nft_id where the user placed a bid
        nft_ids_list = [nft_bid.nft_id for nft_bid in nft_bids]
        # Only keep the unique nft_id
        nft_ids_list = list(set(nft_ids_list))
        # Get all the NFTs where the user placed a bid
        nft_bids_list = [self.get_NFT(nft_id, user_id) for nft_id in nft_ids_list]

        return nft_bids_list

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
                # Update the NFT history
                history_nft = NFTPriceOwnerHistory(nft_id=nft_id, price=nft_price,
                                                   owner_id=user_id,
                                                   date=datetime.now())
                db.session.add(history_nft)
                # Commit the changes
                db.session.commit()
                # Buy the NFT with ETH
                wallet.buy_with_crypto(user, 'ETH-USD', nft_price)
                # Update crypto history
                wallet.update_crypto_wallet_evolution(user)
                return {"status": "success", "message": "You bought the NFT successfully"}
        else:
            return {"status": "error", "message": "The NFT is not for sale", "refresh": True}

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
            url = url_for('BLP_general.public_profile', user_id=str(owner.id))
            return {"message": f"Owned by <a href='{url}'>@{owner.username}</a>",
                    "owned": False,
                    "set_profile_text": None}

    @staticmethod
    def increment_views(nft_id):
        """
        Increment the number of views of a NFT
        """
        # Get the NFT
        nft = NFT.query.filter_by(id=nft_id).first()
        # Increment the number of views
        nft.views_number += 1
        db.session.commit()
        return {"status": "success", "number_of_views": nft.views_number}

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

    def place_bid(self, user_id, nft_id, amount):
        """
        Place a bid on a NFT owned by another user
        """
        amount = round(amount, 3)
        # Get the NFT
        nft = NFT.query.filter_by(id=nft_id).first()
        # Get the user
        user = User.query.filter_by(id=user_id).first()
        # Get all the bids on the NFT
        nft_bids = self.get_bids(nft_id)
        # Get the minimum bid
        bids = [bid['bid_price_crypto'] for bid in nft_bids]
        if bids:
            min_bid = min(bids)
        else:
            min_bid = nft.price
        # Check if the NFT is owned by another user
        if nft.owner_id is None:
            return {"status": "error", "message": "The NFT is not for sale, just buy it"}
        # Check if the user is not the owner of the NFT
        if nft.owner_id == user_id:
            return {"status": "error", "message": "You can't bid on your own NFT"}
        # Check if the user already placed a bid with a higher amount or same amount
        for bid in nft_bids:
            if bid['user_id'] == user_id and bid['bid_price_crypto'] >= amount:
                return {"status": "error", "message": "You already placed a bid with a higher amount or same amount"}

        # Check if the user has enough ETH to place the bid
        wallet = wallet_manager()
        eth_amount = wallet.get_user_specific_balance(user, 'ETH-USD')
        if eth_amount['tokens'] < amount:
            return {"status": "error", "message": "Not enough ETH in the wallet"}

        # Check if the bid is higher than the minimum bid
        if nft_bids:
            if amount <= min_bid:
                return {"status": "error", "message": "The bid is too low"}

        # Take the amount of the bid from the user
        wallet.buy_with_crypto(user, 'ETH-USD', amount)
        # Add the bid to the database and delete the previous minimum bids to only keep 5 bids
        new_bid = NFTBid(user_id=user_id, nft_id=nft_id, bid_date=datetime.utcnow(),
                         bid_price_crypto=amount, bid_crypto_symbol='ETH')
        db.session.add(new_bid)

        # Delete the previous minimum bids if there are more than 5 bids
        if len(nft_bids) > 4:
            for bid in nft_bids:
                if bid['bid_price_crypto'] == min_bid:
                    bid_to_delete = NFTBid.query.filter_by(id=bid['id']).first()
                    db.session.delete(bid_to_delete)
                    # Give back the amount of the bid to the user
                    wallet.receive_crypto(user, 'ETH-USD', min_bid)
                    break

        # send a notification to the owner of the NFT
        url = url_for('BLP_general.nft_details', nft_id=nft_id)
        Notification_manager().add_notification(nft.owner_id,
                                                f"New bid on your NFT <a href='{url}'><b>{nft.name}</b></a>",
                                                "shopping-cart")

        db.session.commit()

        # Update crypto history
        wallet_manager().update_crypto_wallet_evolution(user)

        return {"status": "success", "message": "Bid placed successfully"}

    @staticmethod
    def get_bids(nft_id):
        """
        Get all the bids on a NFT
        """
        # Get all the bids on the NFT
        nft_bids = NFTBid.query.filter_by(nft_id=nft_id).all()
        # Create a list with all the bids
        bids_list = []
        for bid in nft_bids[::-1]:
            user = User.query.filter_by(id=bid.user_id).first()
            bids_list.append({
                'id': bid.id,
                'user_id': user.id,
                'username': user.username,
                'bid_price_crypto': bid.bid_price_crypto,
                'bid_date': bid.bid_date,
                'bid_crypto_symbol': 'ETH'
            })

        return bids_list

    @staticmethod
    def delete_bid(bid_id, current_user_id):
        """
        Delete a bid on a NFT of a user
        """
        # Get the Bid
        bid = NFTBid.query.filter_by(id=bid_id).first()
        if not bid:
            return {"status": "error", "message": "The bid doesn't exist"}
        # Get the NFT
        nft = NFT.query.filter_by(id=bid.nft_id).first()
        # If the user is not the owner of the bid or the owner of the NFT, return an error
        if bid.user_id != current_user_id and nft.owner_id != current_user_id:
            return {"status": "error", "message": "You are not the owner of the bid or the NFT"}
        # Return the amount of the bid to the user
        wallet = wallet_manager()
        wallet.receive_crypto(User.query.filter_by(id=bid.user_id).first(), 'ETH-USD', bid.bid_price_crypto)
        # Delete the bid from the database
        db.session.delete(bid)
        db.session.commit()

        # Update crypto history
        user = User.query.filter_by(id=current_user_id).first()
        wallet_manager().update_crypto_wallet_evolution(user)

        return {"status": "success", "message": "Bid deleted successfully"}

    @staticmethod
    def accept_bid(bid_id, current_user_id):
        """
        Accept a bid on a NFT for the user
        """
        # Get the bid
        bid = NFTBid.query.filter_by(id=bid_id).first()
        # Get the NFT
        nft = NFT.query.filter_by(id=bid.nft_id).first()
        # Get the user who will sell the NFT
        seller = User.query.filter_by(id=nft.owner_id).first()

        # Check if the user is the owner of the NFT
        if nft.owner_id != current_user_id:
            return {"status": "error", "message": "You are not the owner of the NFT"}
        # Check if the bid is still valid
        if nft.owner_id is None:
            return {"status": "error", "message": "The NFT is not for sale"}

        # Transfer the NFT to the user
        user_nft = UserNFT(user_id=bid.user_id, nft_id=bid.nft_id,
                           purchase_price_usd=CryptoDataManager().get_USD_from_crypto('ETH-USD', bid.bid_price_crypto),
                           purchase_price_crypto=bid.bid_price_crypto, purchase_crypto_symbol='ETH')
        db.session.add(user_nft)

        # Delete the NFT from the seller
        UserNFT.query.filter_by(user_id=nft.owner_id, nft_id=bid.nft_id).delete()

        # Update the NFT object
        nft.is_for_sale = False
        nft.owner_id = bid.user_id
        nft.price = bid.bid_price_crypto
        db.session.commit()

        # Update the NFT history
        history_nft = NFTPriceOwnerHistory(nft_id=nft.id, price=bid.bid_price_crypto,
                                           owner_id=bid.user_id,
                                           date=datetime.now())
        db.session.add(history_nft)

        # Transfer the amount of the bid to the seller
        wallet = wallet_manager()
        wallet.receive_crypto(seller, 'ETH-USD', bid.bid_price_crypto)

        # Delete all the bids on the NFT
        NFTBid.query.filter_by(nft_id=bid.nft_id).delete()
        db.session.commit()

        # send a notification to the buyer
        url = url_for('BLP_general.nft_details', nft_id=nft.id)
        Notification_manager().add_notification(bid.user_id,
                                                f"Your bid on the NFT <a href='{url}'><b>{nft.name}</b></a> has been accepted",
                                                "shopping-cart")

        wallet_manager().update_crypto_wallet_evolution(seller)

        return {"status": "success", "message": "Bid accepted successfully"}

    @staticmethod
    def get_NFT_history(nft_id):
        """
        Get the history of a NFT
        """
        # Get the history of the NFT
        nft_history = NFTPriceOwnerHistory.query.filter_by(nft_id=nft_id).all()
        # Create a list with all the history
        history_list = []
        for history in nft_history:
            user = User.query.filter_by(id=history.owner_id).first()
            # For the date, only keep year, month, day, hour and minute
            history_list.append({
                'owner_id': history.owner_id,
                'owner_username': user.username,
                'price': history.price,
                'date': history.date.strftime("%Y-%m-%d %H:%M")
            })

        return history_list
