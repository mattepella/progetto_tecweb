# Generated by Django 5.1.3 on 2024-12-03 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0004_tag_restaurant_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurant',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='restaurants', to='book.tag'),
        ),
    ]
