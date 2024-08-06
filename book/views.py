from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, DeleteView
from .forms import AddStructureForm, ReservationForm, ReviewForm
from .models import Restaurant, Reservation, Review
from datetime import datetime
from django.contrib import messages


def owner_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_owner,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


decorators = [login_required, owner_required()]


def add_review(response, restaurant):
    if response.method == "POST":
        form = ReviewForm(response.POST)
        if form.is_valid():
            value = form.cleaned_data['review_value']
            text = form.cleaned_data['review_text']
            res = Restaurant.objects.get(id=restaurant)
            Review.objects.create(review_res=res, rev_customer_id=response.user.id, review_value=value,
                                  review_text=text)
            return render(response, 'home.html')
        else:
            return render(response, 'add_review.html', {'form': form})
    form = ReviewForm()
    return render(response, 'add_review.html', {'form': form})


class DeleteRestaurant(DeleteView):
    template_name = 'structure_list.html'
    model = Restaurant
    success_message = 'Ristorante cancellato con successo!'
    success_url = reverse_lazy('book:structure_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteRestaurant, self).delete(request, *args, **kwargs)


class DeleteReservation(DeleteView):
    template_name = 'reservation_list.html'
    model = Reservation
    success_message = 'Prenotazione cancellata con successo!'
    success_url = reverse_lazy('book:watch_reservations')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteReservation, self).delete(request, *args, **kwargs)


class ReservationsList(ListView):
    template_name = 'reservation_list.html'
    model = Reservation

    def get_queryset(self):
        return Reservation.objects.filter(customer_id=self.request.user.id)


def check_time(restaurant, res_time):
    if restaurant.start_lunch <= res_time <= restaurant.end_lunch:
        return 'lunch'

    elif restaurant.start_dinner <= res_time <= restaurant.end_dinner or \
            (res_time.strftime('%p') == 'PM' and restaurant.end_dinner.strftime('%p') == 'AM' and
             res_time.hour <= restaurant.end_dinner.hour+24 and res_time >= restaurant.start_dinner) or \
            (res_time.strftime('%p') == 'AM' and restaurant.end_dinner.strftime('%p') == 'AM' and
             restaurant.end_dinner.hour + 24 >= res_time.hour + 24 >= restaurant.start_dinner.hour):
        return 'dinner'

    else:
        return None


def check_reservation(res_user, restaurant, res_seats, res_datetime):
    d = {}
    if res_datetime < datetime.now():
        d['success'] = False
        d['message'] = 'Non puoi effettuare una prenotazione nel passato'
        return d
    avaiable_seats = restaurant.total_seats
    res_time = check_time(restaurant, res_datetime.time())
    if res_time is None:
        d['success'] = False
        d['message'] = 'Non puoi prenotare in questo periodo di tempo'
        return d
    res = Reservation.objects.filter(restaurant_id=restaurant.id)
    for el in res:
        el.res_datetime = el.res_datetime.replace(tzinfo=None)
        if el.customer_id == res_user.id and el.res_datetime.date() == res_datetime.date():
            d['success'] = False
            d['message'] = 'Hai già una prenotazione per questo ristorante nello stesso giorno!'
            return d

        if el.res_datetime.date() == res_datetime.date() and \
                (check_time(restaurant, el.res_datetime.time()) == res_time):
            avaiable_seats -= el.seats
    if avaiable_seats - res_seats < 0:
        d['success'] = False
        d['message'] = 'Non ci sono più posti disponibili! Puoi metterti in lista di attesa'
        return d
    else:
        d['success'] = True
        d['message'] = 'Prenotazione effettuata con successo!'
        return d


def reservation(response, oid):
    if response.method == 'POST':
        restaurant = Restaurant.objects.get(id=oid)
        form = ReservationForm(response.POST)
        if form.is_valid():
            date = form.cleaned_data['res_date']
            time = form.cleaned_data['res_time']
            res_datetime = datetime.combine(date, time)
            seats = form.cleaned_data['seats']
            d = check_reservation(response.user, restaurant, seats, res_datetime)
            if d['success']:
                Reservation.objects.create(customer_id=response.user.id, restaurant=restaurant, seats=seats,
                                           res_datetime=res_datetime)
                messages.success(response, d['message'])
            else:
                messages.error(response, d['message'])
                return render(response, 'reservation.html', {'form': form})
            return redirect('homepage')
        else:
            form = ReservationForm()
            return render(response, 'reservation.html', {'form': form})
    else:
        form = ReservationForm()
        return render(response, 'reservation.html', {'form': form})


class Results(ListView):
    template_name = 'results.html'
    model = Restaurant

    def get_queryset(self, **kwargs):
        return Restaurant.objects.filter(city=self.kwargs['destination'])


class WatchReviews(ListView):
    model = Review
    template_name = 'watch_reviews.html'

    def get_queryset(self, **kwargs):
        return Review.objects.filter(review_res=Restaurant.objects.get(restaurant_name=self.kwargs['restaurant']))


@method_decorator(decorators, name='dispatch')
class StructureList(LoginRequiredMixin, ListView):
    model = Restaurant
    template_name = 'structure_list.html'

    def get_queryset(self):
        user = self.request.user
        return Restaurant.objects.filter(owner=user)


@method_decorator(decorators, name='dispatch')
class AddStructure(LoginRequiredMixin, CreateView):
    model = Restaurant
    form_class = AddStructureForm
    template_name = 'add_structure.html'
    success_url = reverse_lazy('homepage')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
