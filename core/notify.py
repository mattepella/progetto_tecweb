from book.models import Notification


def create_notification(customer, message):
    Notification.objects.create(customer=customer, message=message)
