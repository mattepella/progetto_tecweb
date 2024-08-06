from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    is_customer = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)


class Customer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    short_bio = models.CharField(max_length=255)


class Restaurant(models.Model):
    total_seats = models.IntegerField(default=10)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    city = models.CharField(max_length=255)
    restaurant_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='owners_photos')
    start_lunch = models.TimeField()
    address = models.CharField(max_length=255, null=True)
    end_lunch = models.TimeField()
    start_dinner = models.TimeField(null=True)
    end_dinner = models.TimeField(null=True)
    price = models.IntegerField()

    def save(self, *args, **kwargs):
        self.city = self.city.lower()
        return super(Restaurant, self).save(*args, **kwargs)


class Review(models.Model):
    rev_customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    review_value = models.IntegerField()
    review_text = models.TextField()
    review_res = models.ForeignKey(Restaurant, on_delete=models.CASCADE)


class Reservation(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    seats = models.IntegerField()
    res_datetime = models.DateTimeField(default=None)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
