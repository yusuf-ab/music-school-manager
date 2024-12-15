from django.test import TestCase
from django.urls import reverse
from lessons.models import User, Child, Request, Booking
from datetime import date, time, timedelta

class ScheduleViewTestCase(TestCase):
    """Tests of the schedule view."""

    fixtures = [
        'lessons/tests/fixtures/test_data.json',
    ]

    def setUp(self):
        self.user = User.objects.get(email="john.doe@example.org")
        self.user2 = User.objects.get(email="ryan.fuller@example.org")
        self.teacher = User.objects.get(email="jane.doe@example.org")
        self.child = Child.objects.get(first_name="Alice",last_name="Doe")

        self.url = reverse('schedule', kwargs={})
        self.client.login(username=self.teacher.email, password='Password123')

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

        self.booking3 = Booking.objects.create(
            client=self.user2,
            lessons=2,
            days_between_lessons=7,
            duration=60,
            teacher=self.teacher,
            date=date(2022,1,1),
            time=time(16),
        )

    def test_schedule_url(self):
        self.assertEqual(self.url,'/schedule/')
    
    def test_get_schedule(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schedule.html')

    def test_get_schedule(self):
        self.url = reverse('schedule', kwargs={})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schedule.html')

    # Check schedule with different months

    def test_schedule_view_with_valid_month(self):
        year = 2022
        month = 12
        url = reverse('schedule_custom', kwargs={'year': year, 'month': month})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_schedule_view_with_invalid_month(self):
        # Set up the test data
        year = 2022
        month = 13
        url = reverse('schedule_custom', kwargs={'year': year, 'month': month})
        response = self.client.get(url)
        self.assertContains(response,"Invalid Date")

    def test_previous_month_with_non_january(self):
        year = 2022
        month = 5
        url = reverse('schedule_custom', kwargs={'year': year, 'month': month})
        response = self.client.get(url)
        self.assertEqual(response.context['previous_month'], reverse('schedule_custom', args=[2022, 4]))

    def test_next_month_with_december(self):
        year = 2022
        month = 12
        url = reverse('schedule_custom', kwargs={'year': year, 'month': month})
        response = self.client.get(url)
        self.assertEqual(response.context['next_month'], reverse('schedule_custom', args=[2023, 1]))

    def test_previous_month_with_january(self):
        year = 2022
        month = 1
        url = reverse('schedule_custom', kwargs={'year': year, 'month': month})
        response = self.client.get(url)
        self.assertEqual(response.context['previous_month'], reverse('schedule_custom', args=[2021, 12]))

    def test_next_month_with_non_december(self):
        year = 2022
        month = 5
        url = reverse('schedule_custom', kwargs={'year': year, 'month': month})
        response = self.client.get(url)
        self.assertEqual(response.context['next_month'], reverse('schedule_custom', args=[2022, 6]))

    # Check schedule has all bookings for a teacher
    def test_get_schedule_has_all_teachers_bookings(self):
        self.client.login(username=self.teacher.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schedule.html')

    def test_get_schedule_has_all_students_bookings(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schedule.html')