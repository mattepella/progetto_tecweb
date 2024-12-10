import csv
import os
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from book.models import CustomUser, Customer, Restaurant, Tag


class Command(BaseCommand):
    help = 'importazione ristoranti da csv a database'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(os.path.dirname(__file__), 'restaurants.csv')
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Creazione o recupero del ristorante
                restaurant, created = Restaurant.objects.get_or_create(
                    owner_id=row['owner_id'],
                    restaurant_name=row['restaurant_name'],
                    defaults={
                        'total_seats': row['total_seats'],
                        'city': row['city'],
                        'start_lunch': row['start_lunch'],
                        'end_lunch': row['end_lunch'],
                        'start_dinner': row['start_dinner'],
                        'end_dinner': row['end_dinner'],
                        'price': row['price'],
                        'address': row['address'],
                        'image': row['image']
                    }
                )

                # Gestione dei tag
                if 'tags' in row and row['tags']:
                    print(row['tags'])
                    tag_names = [tag.strip() for tag in row['tags'].split(' ')]
                    for tag_name in tag_names:
                        print(tag_name)
                        tag = Tag.objects.get(name=tag_name)
                        # Usa il metodo add per ciascun tag
                        restaurant.tags.add(tag)

                self.stdout.write("risoranti importati con successo")
