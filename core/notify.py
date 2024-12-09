from book.models import Notification


def create_notification(customer, restaurant, message):
    Notification.objects.create(customer=customer, restaurant=restaurant, message=message)
