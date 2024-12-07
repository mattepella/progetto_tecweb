# Generated by Django 5.1.3 on 2024-12-07 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0005_alter_restaurant_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='waiting_list',
            field=models.ManyToManyField(blank=True, related_name='waiting_restaurants', to='book.customer'),
        ),
    ]
