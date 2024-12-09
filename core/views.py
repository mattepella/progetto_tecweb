from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView

from book.forms import CustomerRegister, OwnerRegister, HomeForm
from book.models import CustomUser, Restaurant, Notification, Reservation


class RegisterCustomer(CreateView):
    model = CustomUser
    form_class = CustomerRegister
    template_name = 'registration/registration.html'
    success_url = reverse_lazy('homepage')


def mark_notification_as_read(request, notification_id):
    # Recupera la notifica specificata
    print("hai cliccato la notifica")
    notification = get_object_or_404(Notification, id=notification_id)
    # Segna la notifica come letta
    notification.is_read = True
    notification.save()

    # Se la notifica ha un ristorante associato
    if notification.restaurant:
        # Rimuovi l'utente dalla lista di attesa del ristorante
        restaurant = notification.restaurant
        if notification.CustomUser in restaurant.waiting_list.all():
            restaurant.waiting_list.remove(notification.CustomUser)
            messages.success(request, f"Sei stato rimosso dalla lista di attesa del ristorante {restaurant.restaurant_name}.")

    return redirect('homepage')


def home_page(response):
    # Controlla se l'utente è autenticato
    if response.user.is_authenticated:
        # Filtra le notifiche non lette per l'utente corrente
        unread_notifications = Notification.objects.filter(CustomUser=response.user, is_read=False)
        unread_count = unread_notifications.count()  # Conta le notifiche non lette
    else:
        unread_notifications = []
        unread_count = 0

    # Gestisci il POST per il form di ricerca della città
    if response.method == "POST":
        form = HomeForm(response.POST)
        if form.is_valid():
            destination = form.cleaned_data['destinazione'].lower()
            if not Restaurant.objects.filter(city=destination):
                messages.error(response, "Nessun ristorante disponibile per la località inserita")
                return render(response, "home.html", {'form': form, 'unread_notifications': unread_notifications,
                                                      'unread_count': unread_count})
            return redirect('book:results', destination)
        else:
            messages.error(response, "Inserire una città")
            return render(response, "home.html",
                          {'form': form, 'unread_notifications': unread_notifications, 'unread_count': unread_count})
    else:
        form = HomeForm()

    # Passa anche le notifiche al template
    return render(response, "home.html",
                  {'form': form, 'unread_notifications': unread_notifications, 'unread_count': unread_count})


class RegisterOwner(CreateView):
    model = CustomUser
    form_class = OwnerRegister
    template_name = 'registration/registration.html'
    success_url = reverse_lazy('homepage')
