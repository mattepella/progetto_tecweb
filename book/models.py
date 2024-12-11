from django.contrib.auth.models import AbstractUser, User
from django.core.exceptions import ValidationError
from django.db import models


class CustomUser(AbstractUser):
    is_customer = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)


class Customer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    short_bio = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Notification(models.Model):
    CustomUser = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name="notifications", null=True)
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, related_name="notifications", null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.CustomUser.username} - {self.message}"


class Restaurant(models.Model):
    total_seats = models.IntegerField(default=10)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    city = models.CharField(max_length=255)
    restaurant_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='owners_photos')
    start_lunch = models.TimeField()
    address = models.CharField(max_length=255, null=True)
    waiting_list = models.ManyToManyField(CustomUser, related_name="waiting_restaurants", blank=True)
    end_lunch = models.TimeField()
    start_dinner = models.TimeField(null=True)
    end_dinner = models.TimeField(null=True)
    tags = models.ManyToManyField(Tag, related_name='restaurants', blank=True)

    def save(self, *args, **kwargs):
        self.city = self.city.lower()
        return super(Restaurant, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete(save=False)
            super().delete(*args, **kwargs)

    def __str__(self):
        return self.restaurant_name


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

    def clean(self):
        if self.seats > self.restaurant.total_seats:
            raise ValidationError(f"Il numero massimo di posti per questo ristorante è: {self.restaurant.total_seats}")
