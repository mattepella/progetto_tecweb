from django.contrib import admin
from book.models import CustomUser, Tag, Restaurant

# Registrazione del modello CustomUser
admin.site.register(CustomUser)

# Registrazione del modello Tag
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

# Registrazione del modello Restaurant
@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('restaurant_name', 'city', 'owner')
    search_fields = ('restaurant_name', 'city')
    filter_horizontal = ('tags',)  # Questo permette di selezionare i tag in modo più comodo
