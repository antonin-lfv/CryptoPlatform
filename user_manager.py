from models import User
from app import db


class UserManager:
    def __init__(self):
        ...

    @staticmethod
    def change_username(user_id, new_username):
        try:
            user = User.query.filter_by(id=user_id).first()
            user.username = new_username
            db.session.commit()
            return {'message': 'Username changed successfully'}
        except Exception as e:
            return {'message': str(e)}

    @staticmethod
    def switch_notifications_active(user_id):
        try:
            user = User.query.filter_by(id=user_id).first()
            user.notifications_active = not user.notifications_active
            db.session.commit()
            return {'message': 'Notifications turned off successfully', 'active': user.notifications_active}
        except Exception as e:
            return {'message': str(e), 'active': False}

    @staticmethod
    def is_user_notification_active(user_id):
        user = User.query.filter_by(id=user_id).first()
        return {'active': user.notifications_active}
