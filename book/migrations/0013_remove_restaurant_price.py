# Generated by Django 5.1.3 on 2024-12-11 08:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0012_restaurant_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='restaurant',
            name='price',
        ),
    ]
