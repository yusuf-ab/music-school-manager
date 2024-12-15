from django.test import TestCase
from django.urls import reverse
from lessons.models import User, Booking
from datetime import date, datetime, time

class ViewBookingViewTestCase(TestCase):
    """Tests of the view booking view."""

    fixtures = [
        'lessons/tests/fixtures/test_data.json',
    ]

    def setUp(self):
        self.user = User.objects.get(email='john.doe@example.org')
        self.user2 = User.objects.get(email="ryan.fuller@example.org")
        self.teacher = User.objects.get(email="jane.doe@example.org")
        self.booking = Booking.objects.create(
            client=self.user,
            lessons=3,
            days_between_lessons=7,
            duration=60,
            teacher=self.teacher,
            date=date(2022,1,1),
            time=time(16)
        )
        self.url = reverse('view_booking', kwargs={'id':self.booking.id})
        self.client.login(email=self.user.email, password='Password123')

    def test_booking_url(self):
        self.assertEqual(self.url,f'/view_booking/{self.booking.id}/')
    
    def test_get_booking(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'view_booking.html')

    def test_invalid_booking_id(self):
        self.url = reverse('view_booking', kwargs={'id':100000})
        response = self.client.get(self.url)
        self.assertContains(response,'Booking does not exist or you don\'t have authorisation to view it')

    def test_other_users_cant_view_other_users_bookings(self):
        self.client.login(email=self.user2.email, password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response,'Booking does not exist or you don\'t have authorisation to view it')
