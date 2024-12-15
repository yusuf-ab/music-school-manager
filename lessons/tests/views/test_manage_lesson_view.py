from django.test import TestCase
from django.urls import reverse
from lessons.models import User, Child, Request, Booking
from datetime import date, time, timedelta

class ManageLessonsViewTestCase(TestCase):
    """Tests of the manage lessons view."""

    fixtures = [
        'lessons/tests/fixtures/test_data.json',
    ]

    def setUp(self):
        self.user = User.objects.get(email="john.doe@example.org")
        self.user2 = User.objects.get(email="ryan.fuller@example.org")
        self.admin = User.objects.get(email="marty.major@example.org")
        self.teacher = User.objects.get(email="jane.doe@example.org")
        self.child = Child.objects.get(first_name="Alice",last_name="Doe")

        self.request1 = Request.objects.create(
            client=self.user,
            availability="Any time",
            lessons="1",
            days_between_lessons="7",
            duration="60",
            info="Piano",
            child=self.child
        )
        self.request2 = Request.objects.create(
            client=self.user,
            availability="Any time",
            lessons="1",
            days_between_lessons="7",
            duration="60",
            info="Piano"
        )

        self.booking = Booking.objects.create(
            client=self.user,
            lessons=2,
            days_between_lessons=7,
            duration=60,
            teacher=self.teacher,
            date=date(2022,1,1),
            time=time(16),
            child=self.child
        )

        self.booking2 = Booking.objects.create(
            client=self.user,
            lessons=2,
            days_between_lessons=7,
            duration=60,
            teacher=self.teacher,
            date=date(2022,1,1),
            time=time(16),
        )

        self.request3 = Request.objects.create(
            client=self.user2,
            availability="Any time",
            lessons="1",
            days_between_lessons="7",
            duration="60",
            info="Violin",
            fulfilled=True
        )

        self.booking3 = Booking.objects.create(
            client=self.user2,
            lessons=2,
            days_between_lessons=7,
            duration=60,
            teacher=self.teacher,
            date=date(2022,1,1),
            time=time(16),
        )

        self.url = reverse('manage_lessons', kwargs={})
        self.client.login(username=self.admin.email, password='Password123')

    def test_manage_lessons_url(self):
        self.assertEqual(self.url,'/manage_lessons/')
    
    def test_get_manage_lessons(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manage_lessons.html')

    def test_admin_can_see_all_requests(self):
        response = self.client.get(self.url)
        for request in Request.objects.all():
            self.assertContains(response,f'request-{request.id}')

    def test_admin_can_see_all_bookings(self):
        response = self.client.get(self.url)
        for booking in Request.objects.all():
            self.assertContains(response,f'booking-{booking.id}')