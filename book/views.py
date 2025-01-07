from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count

from core.notify import create_notification
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, DeleteView
from .forms import AddStructureForm, ReservationForm, ReviewForm
from .models import Restaurant, Reservation, Review, Tag
from datetime import datetime
from django.contrib import messages
from django.forms.widgets import CheckboxInput


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


@login_required
def add_review(response, restaurant):
    form = ReviewForm()
    city = Restaurant.objects.get(id=restaurant).city
    if response.method == "POST":
        form = ReviewForm(response.POST)
        if form.is_valid():
            if Review.objects.filter(rev_customer_id=response.user.id, review_res=restaurant):
                messages.error(response, "hai gia una recensione per questo ristorante!")
                return redirect('homepage')
            value = form.cleaned_data['review_value']
            text = form.cleaned_data['review_text']
            res = Restaurant.objects.get(id=restaurant)
            Review.objects.create(review_res=res, rev_customer_id=response.user.id, review_value=value,
                                  review_text=text)
            messages.success(response, "Recensione aggiunta con successo!!")
            return redirect('homepage')
        else:
            return render(response, 'add_review.html', {'form': form, 'city': city})
    return render(response, 'add_review.html', {'form': form, 'city': city})


class DeleteRestaurant(LoginRequiredMixin, DeleteView):
    model = Restaurant
    template_name = 'structure_list.html'
    success_url = reverse_lazy('book:restaurant_list')

    def form_valid(self, form):
        data = super().form_valid(form)
        messages.success(self.request, 'Ristorante rimosso con successo!')
        return data


@login_required
def delete_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    waiting_list_customers = reservation.restaurant.waiting_list.all()

    for customer in waiting_list_customers:
        message = f'Si sono liberati dei posti al ristorante {reservation.restaurant.restaurant_name}'
        create_notification(customer, reservation.restaurant, message)

    reservation.delete()

    messages.success(request, 'Prenotazione cancellata con successo!')

    return redirect('book:watch_reservations')


class ReservationsList(LoginRequiredMixin, ListView):
    template_name = 'reservation_list.html'
    model = Reservation

    def get_queryset(self):
        return Reservation.objects.filter(customer_id=self.request.user.id)


def check_time(restaurant, res_time):
    if restaurant.start_lunch <= res_time <= restaurant.end_lunch:
        return 'lunch'

    elif restaurant.start_dinner <= res_time <= restaurant.end_dinner or \
            (res_time.strftime('%p') == 'PM' and restaurant.end_dinner.strftime('%p') == 'AM' and
             res_time.hour <= restaurant.end_dinner.hour + 24 and res_time >= restaurant.start_dinner) or \
            (res_time.strftime('%p') == 'AM' and restaurant.end_dinner.strftime('%p') == 'AM' and
             restaurant.end_dinner.hour + 24 >= res_time.hour + 24 >= restaurant.start_dinner.hour):
        return 'dinner'

    else:
        return None


def check_reservation(res_user, restaurant, res_seats, res_datetime):
    d = {}
    if res_seats <= 0:
        d['success'] = False
        d['message'] = 'numero di persone non valido'
        return d
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


@login_required
def reservation(response, oid):
    if response.method == 'POST':
        restaurant = Restaurant.objects.get(id=oid)
        form = ReservationForm(response.POST)
        if form.is_valid():
            city = restaurant.city
            date = form.cleaned_data['res_date']
            time = form.cleaned_data['res_time']
            res_datetime = datetime.combine(date, time)
            seats = form.cleaned_data['seats']
            d = check_reservation(response.user, restaurant, seats, res_datetime)
            if d['success']:
                Reservation.objects.create(customer=response.user.customer, restaurant=restaurant, seats=seats,
                                           res_datetime=res_datetime)
                message = (
                    f'{restaurant.restaurant_name} prenotazione effettuata da {response.user.username} per il giorno: '
                    f'{res_datetime}')
                create_notification(restaurant.owner, restaurant=restaurant, message=message)
                messages.success(response, d['message'])
            else:
                messages.error(response, d['message'])
                if "Non ci sono più posti disponibili" in d['message']:
                    form.fields['add_to_waiting_list'].widget = CheckboxInput()
                    add_to_waiting_list = form.cleaned_data.get("add_to_waiting_list")
                    if add_to_waiting_list:
                        if response.user.customer not in restaurant.waiting_list.all():
                            restaurant.waiting_list.add(response.user)
                            messages.success(response, "Sei stato aggiunto alla lista di attesa!")
                            return redirect('homepage')
                        else:
                            messages.error(response, "Sei già in lista di attesa per questo ristorante!")
                return render(response, 'reservation.html',
                              {'form': form, 'success': False, 'city': city, 'message': d['message'],
                               'restaurant': restaurant})
            return redirect('homepage')
        else:
            form = ReservationForm()
            return render(response, 'reservation.html', {
                'form': form, 'restaurant': restaurant, 'image': restaurant.image,
                'res_name': restaurant.restaurant_name, 'city': restaurant.city
            })
    else:
        form = ReservationForm()
        restaurant = Restaurant.objects.get(id=oid)
        return render(response, 'reservation.html', {
            'form': form, 'restaurant': restaurant, 'image': restaurant.image,
            'res_name': restaurant.restaurant_name, 'city': restaurant.city
        })


class Results(ListView):
    template_name = 'results.html'
    model = Restaurant

    def get_queryset(self):
        destination = self.kwargs['destination']
        selected_tags = self.request.GET.getlist('tags')

        queryset = Restaurant.objects.filter(city=destination)

        if selected_tags:
            for tag_id in selected_tags:
                queryset = queryset.filter(tags__id__in=tag_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
        context['selected_tags'] = self.request.GET.getlist('tags')
        return context


class WatchReviews(ListView):
    model = Review
    template_name = 'watch_reviews.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.restaurant_city = ''

    def get_queryset(self, **kwargs):
        self.restaurant_city = Restaurant.objects.get(restaurant_name=self.kwargs['restaurant']).city
        return Review.objects.filter(review_res=Restaurant.objects.get(restaurant_name=self.kwargs['restaurant']))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['city'] = self.restaurant_city
        return context


@method_decorator(decorators, name='dispatch')
class StructureList(LoginRequiredMixin, ListView):
    model = Restaurant
    template_name = 'structure_list.html'

    def get_queryset(self):
        user = self.request.user
        return Restaurant.objects.filter(owner=user)


@login_required
def watchinfos(request, restaurant):
    res = get_object_or_404(Restaurant, id=restaurant)
    reservations = Reservation.objects.filter(restaurant=res)
    days_of_week = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
    reservation_count = {day: 0 for day in days_of_week}
    for reservation in reservations:
        day_of_week = reservation.res_datetime.weekday()  # Restituisce un numero tra 0 (Lunedì) e 6 (Domenica)
        reservation_count[days_of_week[day_of_week]] += 1

    reviews = Review.objects.filter(review_res=res)
    avg_rating = reviews.aggregate(Avg('review_value'))['review_value__avg']
    ratings_distribution = reviews.values('review_value').annotate(count=Count('review_value')).order_by('review_value')

    chart_data_reviews = {
        'labels': [str(item['review_value']) for item in ratings_distribution],
        'data': [item['count'] for item in ratings_distribution],
    }

    chart_data_reservations = {
        'labels': days_of_week,
        'data': [reservation_count[day] for day in days_of_week],
    }

    context = {
        'restaurant': res,
        'average_rating': avg_rating,
        'chart_data_reviews': chart_data_reviews,
        'chart_data_reservations': chart_data_reservations,
    }
    return render(request, 'watch_infos.html', context)


@method_decorator(decorators, name='dispatch')
class AddStructure(LoginRequiredMixin, CreateView):
    model = Restaurant
    form_class = AddStructureForm
    template_name = 'add_structure.html'
    success_url = reverse_lazy('homepage')

    def form_valid(self, form):
        messages.success(self.request, 'Ristorante aggiunto con successo!')
        form.instance.owner = self.request.user
        return super().form_valid(form)
