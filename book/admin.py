from django.contrib import admin
from book.models import CustomUser, Tag, Restaurant

admin.site.register(CustomUser)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('restaurant_name', 'city', 'owner')
    search_fields = ('restaurant_name', 'city')
