from django.test import TestCase
from django.urls import reverse
from lessons.models import User, Child, Request, Booking
from datetime import date, time, timedelta

class ListLessonsViewTestCase(TestCase):
    """Tests of the list lessons view."""

    fixtures = [
        'lessons/tests/fixtures/test_data.json',
    ]

    def setUp(self):
        self.user = User.objects.get(email="john.doe@example.org")
        self.user2 = User.objects.get(email="ryan.fuller@example.org")
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

        self.url = reverse('list_lessons', kwargs={})
        self.client.login(username='john.doe@example.org', password='Password123')

    def test_list_lessons_url(self):
        self.assertEqual(self.url,'/list_lessons/')
    
    def test_get_list_lessons(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list_lessons.html')

    def test_student_can_see_all_their_requests(self):
        response = self.client.get(self.url)
        for request in Request.objects.filter(client=self.user):
            self.assertContains(response,f'request-{request.id}')

    def test_student_cannot_see_other_student_requests(self):
        response = self.client.get(self.url)
        for request in Request.objects.filter(client=self.user2):
            self.assertNotContains(response,f'request-{request.id}')

    def test_student_can_see_all_their_bookings(self):
        response = self.client.get(self.url)
        for booking in Request.objects.filter(client=self.user):
            self.assertContains(response,f'booking-{booking.id}')

    def test_student_cannot_see_other_student_bookings(self):
        response = self.client.get(self.url)
        for booking in Request.objects.filter(client=self.user2):
            self.assertNotContains(response,f'booking-{booking.id}')

    def test_student_can_delete_request(self):
        self.data={'id': f'{self.request1.id}', 'delete_request': 'Delete'}
        request_count_before = Request.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        request_count_after = Request.objects.count()
        self.assertEqual(request_count_before, request_count_after + 1)
        self.assertTemplateUsed(response, 'list_lessons.html')

    def test_student_deletes_request_with_invalid_id(self):
        self.data={'id': 10000, 'delete_request': 'Delete'}
        request_count_before = Request.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        request_count_after = Request.objects.count()
        self.assertEqual(request_count_before, request_count_after)
        self.assertTemplateUsed(response, 'list_lessons.html')

    def test_student_deletes_request_that_does_not_exist(self):
        self.data={'id': 'pizza', 'delete_request': 'Delete'}
        request_count_before = Request.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        request_count_after = Request.objects.count()
        self.assertEqual(request_count_before, request_count_after)
        self.assertTemplateUsed(response, 'list_lessons.html')

    def test_student_cannot_delete_other_students_request(self):
        self.data={'id': f'{self.request3.id}', 'delete_request': 'Delete'}
        request_count_before = Request.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        request_count_after = Request.objects.count()
        self.assertEqual(request_count_before, request_count_after)
        self.assertTemplateUsed(response, 'list_lessons.html')