# Generated by Django 5.1.3 on 2024-12-11 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0011_remove_restaurant_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='price',
            field=models.IntegerField(default=20),
            preserve_default=False,
        ),
    ]
