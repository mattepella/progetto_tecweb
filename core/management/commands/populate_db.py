import csv
import os

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from book.models import CustomUser, Customer


class Command(BaseCommand):
    help = 'importazione utenti da csv a databse'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(os.path.dirname(__file__), 'users_populate.csv')
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Creazione del CustomUser
                if not CustomUser.objects.filter(username=row['username']).exists():
                    user = CustomUser.objects.create(
                        username=row['username'],
                        is_customer=row['is_customer'].lower() == 'true',
                        is_owner=row['is_owner'].lower() == 'true',
                        password=make_password(row['password'])  # Hash password
                    )

                    # Creazione del Customer se `is_customer` è True
                    if user.is_customer:
                        Customer.objects.create(
                            user=user,
                            short_bio=row['short_bio']
                        )

            self.stdout.write("Utenti e clienti importati con successo!")
