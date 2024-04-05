from models import User, UserQuestsStats
from app import db


class Quests_manager:

    @staticmethod
    def check_and_reward(user_id):
        """
        Check if the user has completed a quest and reward him
        """
        # get the current step of all quests
        user_step_quest = UserQuestsStats.query.filter_by(user_id=user_id).first()
        if user_step_quest is None:
            user_step_quest = UserQuestsStats(user_id=user_id)
            db.session.add(user_step_quest)
            db.session.commit()
            nft_bougth, nft_sold, nft_bid, servers_bought = 0, 0, 0, 0

        # TODO
