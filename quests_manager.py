from models import User, UserQuestRewards, UserQuestsStats
from app import db
from wallet_manager import wallet_manager
from utils import reward_factor
from mining_server_manager import Mining_server_manager


class Quests_manager:

    @staticmethod
    def recover_quest(user_id, step, quest_type):
        user = User.query.get(user_id)
        # Get the reward for the quest
        user_rewards = UserQuestRewards.query.filter_by(user_id=user_id, step=step, quest_type=quest_type).first()
        # If None, create with reward_claimed field as True
        if user_rewards is None:
            user_rewards = UserQuestRewards(user_id=user_id, step=step, quest_type=quest_type, reward_claimed=True)
            db.session.add(user_rewards)
        # If not None, set reward_claimed as True if it is False else return an error
        else:
            if user_rewards.reward_claimed:
                return {"status": "error", "message": f"User {user_id} has already claimed the reward for "
                                                      f"quest {quest_type} step {step}"}
            user_rewards.reward_claimed = True

        db.session.commit()

        # Reward the user
        reward_BTC = reward_factor*step
        wallet_manager().receive_crypto(user, 'BTC-USD', reward_BTC)

        return {"status": "success", "message": f"User {user_id} has claimed "
                                                f"the reward for quest {quest_type} step {step}"}
