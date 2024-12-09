from book.models import Notification


def create_notification(customuser, restaurant, message):
    Notification.objects.create(CustomUser=customuser, restaurant=restaurant, message=message)
