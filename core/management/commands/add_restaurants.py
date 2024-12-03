import csv
import os

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from book.models import CustomUser, Customer, Restaurant


class Command(BaseCommand):
    help = 'importazione ristoranti da csv a database'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(os.path.dirname(__file__), 'restaurants.csv')
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Creazione del Ristorante
                if not Restaurant.objects.filter(restaurant_name=row['restaurant_name']):
                    Restaurant.objects.create(
                        owner_id=row['owner_id'],
                        restaurant_name=row['restaurant_name'],
                        total_seats=row['total_seats'],
                        city=row['city'],
                        start_lunch=row['start_lunch'],
                        end_lunch=row['end_lunch'],
                        start_dinner=row['start_dinner'],
                        end_dinner=row['end_dinner'],
                        price=row['price'],
                        address=row['address'],
                        image=row['image']
                    )

            self.stdout.write("Utenti e clienti importati con successo!")
