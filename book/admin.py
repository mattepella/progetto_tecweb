from django.contrib import admin, messages
from django.shortcuts import redirect

from book.models import CustomUser, Tag, Restaurant, Review, Reservation
from core.notify import create_notification

admin.site.register(CustomUser)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('restaurant_name', 'city', 'owner')
    search_fields = ('restaurant_name', 'city')
    filter_horizontal = ('tags',)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('customer', 'restaurant', 'seats', 'res_datetime')
    list_filter = ('restaurant', 'res_datetime')
    search_fields = ('customer__user__username', 'restaurant__restaurant_name')
    ordering = ('res_datetime',)

    def delete_model(self, request, obj):
        waiting_list_customers = obj.restaurant.waiting_list.all()
        for customer in waiting_list_customers:
            print('ci sono persone in attesa')
            message = f'Si sono liberati dei posti al ristorante {obj.restaurant.restaurant_name}'
            create_notification(customer, obj.restaurant, message)
        obj.delete()
        messages.success(request, 'Prenotazione cancellata con successo!')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        restaurant = obj.restaurant
        owner = obj.restaurant.owner
        message = (f'{restaurant.restaurant_name} prenotazione effettuata da {obj.customer.user.username} per il giorno: '
                   f'{obj.res_datetime}')
        create_notification(owner, obj.restaurant, message)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('rev_customer', 'review_value', 'review_text', 'review_res')
    list_filter = ('review_res',)
    search_fields = ('review_text',)
