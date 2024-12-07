from crispy_forms.bootstrap import InlineCheckboxes
from crispy_forms.layout import Submit, Layout, Field, Div
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from crispy_forms.helper import FormHelper

from book.models import CustomUser, Customer, Restaurant, Review, Tag


class AddStructureForm(forms.ModelForm):

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='seleziona i tag:'
    )

    restaurant_name = forms.CharField(
        max_length=255,
        label="Nome ristorante:"
    )
    city = forms.CharField(
        label="Luogo",
        max_length=255
    )
    start_lunch = forms.TimeField(
        label="inizio pranzo:",
        widget=forms.TimeInput(attrs={'type': 'time'}, format='%H:%M')
    )
    end_lunch = forms.TimeField(
        label="fine pranzo",
        widget=forms.TimeInput(attrs={'type': 'time'}, format='%H:%M')
    )

    start_dinner = forms.TimeField(
        label="inizio cena",
        widget=forms.TimeInput(attrs={'type': 'time'}, format='%H:%M')
    )

    end_dinner = forms.TimeField(
        label="fine cena",
        widget=forms.TimeInput(attrs={'type': 'time'}, format='%H:%M')
    )

    total_seats = forms.IntegerField(
        label="capienza massima:"
    )

    price = forms.IntegerField(
        label="costo del coperto:"
    )

    image = forms.ImageField(
        label="Immagine:",
        widget=forms.FileInput(attrs={'class': 'image-upload'})
    )

    address = forms.CharField(
        label='indirizzo:'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-exampleForm'
        self.helper.form_class = 'try'
        self.helper.form_method = 'post'
        self.helper.form_action = 'homepage'
        self.helper.add_input(Submit('submit', 'Aggiungi'))
        self.helper.layout = Layout(
            Field('restaurant_name', style='max-width: 400px'),
            Field('address', style='max-width: 400px'),
            Field('total_seats', style='max-width: 70px'),
            Field('price', style='max-width: 70px'),
            Field('city', style='max-width: 300px'),
            Div(
                Field('start_lunch', style='max-width: 80px'),
                Field('end_lunch', style='max-width: 80px'),
                css_class='form-row'
            ),
            Div(
                Field('start_dinner', style='max-width: 80px'),
                Field('end_dinner', style='max-width: 80px'),
                css_class='form-row'
            ),
            Div(
                Field('image'),
                css_class='image-upload'
            ),


            InlineCheckboxes('tags'),
        )

    class Meta:
        model = Restaurant
        fields = ['restaurant_name', 'address', 'city', 'start_lunch', 'total_seats', 'start_dinner',
                  'end_lunch', 'end_dinner', 'price', 'image', 'tags']


class ReviewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('review_text', style='max-width: 400px'),
            Field('review_value', style='max-width: 100px'),
            Submit('submit', 'INSERISCI')
        )

    review_text = forms.CharField(
        label='Inserisci recensione:',
        widget=forms.Textarea()
    )
    review_value = forms.IntegerField(
        label="Inserisci valutazione",
        widget=forms.NumberInput(attrs={'min': 1, 'max': 5})
    )

    class Meta:
        fields = ['review_text', 'review_value']
        model = Review


class HomeForm(forms.Form):
    destinazione = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': "form-control"}))


class ReservationForm(forms.Form):

    add_to_waiting_list = forms.BooleanField(required=False, label='Vuoi metterti in lista di attesa?', widget=forms.HiddenInput())

    seats = forms.IntegerField(
        label='seleziona numero di persone: '
    )
    res_date = forms.DateField(
        label='seleziona una data per la prenotazione:',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    res_time = forms.TimeField(
        label="seleziona l'orario di prenotazione",
        widget=forms.TimeInput(attrs={'type': 'time'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('seats', style='max-width: 300px'),
            Field('res_date', style='max-width: 300px'),
            Field('res_time', style='max-width: 300px'),
            Field('add_to_waiting_list', style='margin-top: 5px;'),
            Submit('submit', 'Prenota')
        )


class CustomerRegister(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username', style='max-width: 400px'),
            Field('password1', style='max-width: 400px'),
            Field('password2', style='max-width: 400px'),
            Field('short_bio', style='max-width: 700px'),
            Submit('submit', 'REGISTRATI')
        )

    password2 = forms.CharField(
        label='Conferma password:',
        strip=False,
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html(),
    )

    short_bio = forms.CharField(
        max_length=255,
        label='inserisci una bio'
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_customer = True
        user.save()
        customer = Customer.objects.create(user=user)
        customer.short_bio = self.cleaned_data.get("short_bio")
        customer.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username', style='max-width: 400px'),
            Field('password', style='max-width: 400px'),
            Submit('submit', 'LOGIN')
        )


class OwnerRegister(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username', style='max-width: 400px'),
            Field('password1', style='max-width: 400px'),
            Field('password2', style='max-width: 400px'),
            Submit('submit', 'REGISTRATI')
        )

    password2 = forms.CharField(
        label='Conferma password:',
        strip=False,
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html(),

    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_owner = True
        user.save()
        return user
