from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import AddStructure, StructureList, Results, reservation, ReservationsList, \
    DeleteRestaurant, add_review, WatchReviews, delete_reservation

app_name = 'book'

urlpatterns = [
    path('add_structure', AddStructure.as_view(), name='add_structure'),
    path('structure_list', StructureList.as_view(), name='structure_list'),
    path('structure_list/<int:pk>', DeleteRestaurant.as_view(), name='delete_restaurant'),
    path('results/<str:destination>/', Results.as_view(), name='results'),
    path('results/<int:restaurant>/review', add_review, name='review'),
    path('reservations', ReservationsList.as_view(), name='watch_reservations'),
    path('reservations/<int:pk>', delete_reservation, name='delete_reservation'),
    path('results/<int:oid>', reservation, name='reservation'),
    path('reviews/<str:restaurant>', WatchReviews.as_view(), name='watch_reviews'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
