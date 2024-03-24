from datetime import datetime, timedelta
from app import db
from models import Notification, User


class Notification_manager:
    def __init__(self):
        ...

    @staticmethod
    def get_notifications(current_user):
        """
        Get all notifications of the user
        """
        notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.date.desc()).all()
        # Create a dict object for each notification to be able to use it in the template
        notifications = [
            {
                'message': notification.message,
                'icon': notification.icon,
                'date': notification.date
            }
            for notification in notifications
        ]
        return notifications

    @staticmethod
    def add_notification(user_id, message, icon):
        """
        Add a notification to the database
        Icon options:
            - users
            - user
            - warning
            - shopping-cart
        """
        # Check if the user turn off the notifications
        user = User.query.filter_by(id=user_id).first()
        if user.notifications_active is False:
            return

        new_notification = Notification(
            user_id=user_id,
            message=message,
            icon=icon,
            date=datetime.utcnow()
        )
        db.session.add(new_notification)
        db.session.commit()

    @staticmethod
    def delete_all_notifications(current_user):
        """
        Delete all notifications from the database
        """
        notifications = Notification.query.filter_by(user_id=current_user.id).all()
        for notification in notifications:
            db.session.delete(notification)
        db.session.commit()

    @staticmethod
    def delete_old_notifications(current_user):
        """
        Delete notifications older than 1 week
        """
        notifications = Notification.query.filter_by(user_id=current_user.id).all()
        for notification in notifications:
            if notification.date < datetime.utcnow() - timedelta(days=7):
                db.session.delete(notification)
        db.session.commit()
