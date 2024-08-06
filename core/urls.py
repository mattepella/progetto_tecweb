from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

from book.forms import LoginForm
from .views import home_page
from core.views import RegisterCustomer, RegisterOwner


urlpatterns = [
    path('', home_page, name='homepage'),
    path('admin/', admin.site.urls),
    path('register/customer', RegisterCustomer.as_view(), name='customer-registration'),
    path('register/owner', RegisterOwner.as_view(), name='owner-registration'),
    path('login/', auth_views.LoginView.as_view(authentication_form=LoginForm), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('book/', include('book.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
