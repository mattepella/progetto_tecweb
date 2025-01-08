from django.contrib.auth import authenticate
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from book.models import CustomUser, Restaurant, Customer, Reservation, Review
from django.urls import reverse
from datetime import time, date, datetime


class TestReservationView(TestCase):

    def setUp(self):
        self.owner_test = CustomUser.objects.create_user(
            username='owner_test',
            password='test_password',
            is_owner=True,
            is_customer=False
        )

        self.test_user = CustomUser.objects.create_user(
            username='test_user',
            password='test_password',
            is_owner=False,
            is_customer=True
        )

        self.customer = Customer.objects.create(user=self.test_user)

        self.restaurant = Restaurant.objects.create(
            restaurant_name="Test Restaurant",
            owner=self.owner_test,
            city="Test City",
            total_seats=40,
            start_lunch=time(12, 0),
            end_lunch=time(14, 0),
            start_dinner=time(18, 0),
            end_dinner=time(22, 0),
            image=SimpleUploadedFile(
                name='test.jpg',
                content=b"test image content",
                content_type='image/jpeg'

            )
        )

        self.client.force_login(self.test_user)

    def test_reservation_get(self):
        response = self.client.get(reverse('book:reservation', args=[self.restaurant.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Restaurant')
        self.assertContains(response, 'res_date')
        self.assertContains(response, 'res_time')
        self.assertContains(response, 'city')

    def test_create_reservation(self):
        form_data = {
            'res_date': date(2025, 1, 18),
            'res_time': time(18, 0),
            'seats': 2,
        }

        response = self.client.post(reverse('book:reservation', args=[self.restaurant.id]), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Reservation.objects.filter(
            customer=self.customer,
            restaurant=self.restaurant,
            seats=2,
            res_datetime=datetime(2025, 1, 18, 18, 0)
        ).exists())

    def test_wrong_reservation_date(self):
        form_data = {
            'res_date': date(2025, 1, 6),  # Data nel passato
            'res_time': time(18, 0),
            'seats': 2,
        }

        response = self.client.post(reverse('book:reservation', args=[self.restaurant.id]), form_data)

        self.assertEqual(response.status_code, 200)

        self.assertFalse(Reservation.objects.filter(
            customer=self.customer,
            restaurant=self.restaurant,
            seats=2,
            res_datetime=datetime(2025, 1, 6, 18, 0)
        ).exists())

        self.assertIn('Non puoi effettuare una prenotazione nel passato', response.content.decode())

    def test_wrong_reservation_seats(self):
        form_data = {
            'res_date': date(2025, 1, 6),  # Data nel passato
            'res_time': time(18, 0),
            'seats': -2,
        }
        response = self.client.post(reverse('book:reservation', args=[self.restaurant.id]), form_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Reservation.objects.filter(
            customer=self.customer,
            restaurant=self.restaurant,
            seats=2,
            res_datetime=datetime(2025, 1, 6, 18, 0)
        ).exists())
        self.assertIn('numero di persone non valido', response.content.decode())

    def test_reservation_waiting_list(self):
        self.restaurant.total_seats = 40
        self.restaurant.save()

        for _ in range(20):
            Reservation.objects.create(
                customer=self.customer,
                restaurant=self.restaurant,
                seats=2,
                res_datetime=datetime(2025, 1, 18, 18, 0)
            )

        form_data = {
            'res_date': date(2025, 1, 18),
            'res_time': time(18, 0),
            'seats': 2,
        }
        response = self.client.post(reverse('book:reservation', args=[self.restaurant.id]), form_data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'add_to_waiting_list')

        form = response.context['form']
        self.assertTrue(form.is_valid())
        self.assertFalse(form.cleaned_data.get('add_to_waiting_list', False))

        form_data = {
            'res_date': date(2025, 1, 18),
            'res_time': time(18, 0),
            'seats': 2,
            'add_to_waiting_list': True
        }
        response = self.client.post(reverse('book:reservation', args=[self.restaurant.id]), form_data)
        #self.assertEqual(response.status_code, 302)


class TestReviews(TestCase):
    def setUp(self):
        self.owner_test = CustomUser.objects.create_user(
            username='owner_test',
            password='test_password',
            is_owner=True,
            is_customer=False
        )

        self.test_user = CustomUser.objects.create_user(
            username='test_user',
            password='test_password',
            is_owner=False,
            is_customer=True
        )

        self.customer = Customer.objects.create(user=self.test_user)

        self.restaurant = Restaurant.objects.create(
            restaurant_name="Test Restaurant",
            owner=self.owner_test,
            city="Test City",
            total_seats=40,
            start_lunch="12:00",
            end_lunch="14:00",
            start_dinner="18:00",
            end_dinner="22:00",
            image=SimpleUploadedFile(name='test.jpg', content=b"test image content", content_type='image/jpeg')
        )

    def test_create_review(self):
        review_data = {
            'review_value': 5,
            'review_text': 'ottimo cibo!!',
        }
        self.client.force_login(self.test_user)
        response = self.client.post(reverse('book:review', args=[self.restaurant.id]), review_data)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertIn("Recensione aggiunta con successo!!", response.content.decode())
        customer = Customer.objects.get(user=self.test_user)
        review = Review.objects.filter(
            rev_customer=customer,
            review_res=self.restaurant,
            review_value=5,
            review_text='ottimo cibo!!'
        )
        self.assertTrue(review.exists())

    def test_duplicate_review(self):
        review_data = {
            'review_value': 5,
            'review_text': 'ottimo cibo!!',
        }
        self.client.force_login(self.test_user)
        response = self.client.post(reverse('book:review', args=[self.restaurant.id]), review_data)
        self.assertEqual(response.status_code, 302)

        duplicate_review_data = {
            'review_value': 3,
            'review_text': 'ottimo cibo2!',
        }
        response = self.client.post(reverse('book:review', args=[self.restaurant.id]), duplicate_review_data)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertIn("hai gia una recensione per questo ristorante!", response.content.decode())
        customer = Customer.objects.get(user=self.test_user)
        reviews = Review.objects.filter(rev_customer=customer, review_res=self.restaurant)
        self.assertEqual(reviews.count(), 1)


class TestAccount(TestCase):

    def setUp(self):

        self.test_user = CustomUser.objects.create_user(
            username='test_user',
            password='test_password',
            is_owner=False,
            is_customer=True
        )

        self.test_owner = CustomUser.objects.create_user(
            username='owner_test',
            password='test_password',
            is_owner=True,
            is_customer=False
        )

        self.restaurant = Restaurant.objects.create(
            restaurant_name="Test Restaurant",
            owner=self.test_owner,
            city="Test City",
            total_seats=40,
            start_lunch="12:00",
            end_lunch="14:00",
            start_dinner="18:00",
            end_dinner="22:00",
            image=SimpleUploadedFile(name='test.jpg', content=b"test image content", content_type='image/jpeg')
        )

    def test_logged(self):
        user = authenticate(username='test_user', password='test_password')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'test_user')

    def test_wrong_credentials(self):
        user = authenticate(username='test_user', password='wrong')
        self.assertIsNone(user)

    def test_owner_access_infos(self):
        client = Client()
        client.login(username='owner_test', password='test_password')
        response = client.get(reverse('book:watch_infos', kwargs={'restaurant': self.restaurant.id}))
        self.assertEqual(response.status_code, 200)

    def test_owner_wrong_access_infos(self):
        client = Client()
        client.login(username='test_user', password='test_password')
        response = client.get(reverse('book:watch_infos', kwargs={'restaurant': self.restaurant.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/book/infos/1/infos')