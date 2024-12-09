from django.contrib import admin
from book.models import CustomUser, Tag, Restaurant, Review

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


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('rev_customer', 'review_value', 'review_text', 'review_res')
    list_filter = ('review_res',)
    search_fields = ('review_text',)
