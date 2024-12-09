# Generated by Django 5.1.3 on 2024-12-09 15:25

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0009_remove_notification_customer_notification_customuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurant',
            name='waiting_list',
            field=models.ManyToManyField(blank=True, related_name='waiting_restaurants', to=settings.AUTH_USER_MODEL),
        ),
    ]
