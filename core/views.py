from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from book.forms import CustomerRegister, OwnerRegister, HomeForm
from book.models import CustomUser


class RegisterCustomer(CreateView):
    model = CustomUser
    form_class = CustomerRegister
    template_name = 'registration/registration.html'
    success_url = reverse_lazy('homepage')


def home_page(response):
    if response.method == "POST":
        form = HomeForm(response.POST)
        if form.is_valid():
            destination = form.cleaned_data['destinazione'].lower()
            return redirect('book:results', destination)
    else:
        form = HomeForm()
        return render(response, "home.html", {'form': form})


class RegisterOwner(CreateView):
    model = CustomUser
    form_class = OwnerRegister
    template_name = 'registration/registration.html'
    success_url = reverse_lazy('homepage')
