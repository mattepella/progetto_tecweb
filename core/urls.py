from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

from book import views
from book.forms import LoginForm
from .views import home_page, mark_notification_as_read, delete_account
from core.views import RegisterCustomer, RegisterOwner

app_name = 'core'

urlpatterns = [
    path('', home_page, name='homepage'),
    path('notifications/<int:notification_id>/read/', mark_notification_as_read, name='mark_notification_as_read'),
    path('admin/', admin.site.urls),
    path('delete_account', delete_account, name='delete_account'),
    path('register/customer', RegisterCustomer.as_view(), name='customer-registration'),
    path('register/owner', RegisterOwner.as_view(), name='owner-registration'),
    path('login/', auth_views.LoginView.as_view(authentication_form=LoginForm), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('book/', include('book.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
