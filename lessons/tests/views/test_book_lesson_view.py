"""Tests of the book lesson view."""
from django.test import TestCase
from django.urls import reverse
from lessons.forms import BookingForm, UserSelectForm
from lessons.models import User, Booking, Child, Request, Invoice, Transfer
from lessons.tests.helpers import LogInTester
from datetime import date, datetime, time


class BookLessonTestCase(TestCase,LogInTester):
    """Tests of the booking view."""

    fixtures = [
        'lessons/tests/fixtures/test_data.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email="john.doe@example.org")
        self.user2 = User.objects.get(email="ryan.fuller@example.org")
        self.teacher = User.objects.get(email="jane.doe@example.org")
        self.child = Child.objects.get(first_name="Alice",last_name="Doe")

        self.request1 = Request.objects.create(
            client=self.user,
            availability="Any time",
            lessons="3",
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
            info="Piano",
            fulfilled=False
        )

        self.booking = Booking.objects.create(
            client=self.user,
            lessons=3,
            days_between_lessons=7,
            duration=60,
            teacher=self.teacher,
            date=date(2022,1,1),
            time=time(16),
            child=self.child
        )
        self.invoice = Invoice(
            booking=self.booking,
            invoice_ref=self.booking.invoice_reference(),
            date="2022-11-21",
            due_by_date=self.booking.date,
            amount=self.booking.calculate_price(),
            refund=False
        )
        self.invoice.save()

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

        self.admin = User.objects.get(email="marty.major@example.org")
        self.form_input = {
            "name":"Term 1",
            "start_date":"2022-09-01",
            "end_date":"2022-10-22"
        }
        self.client.login(email=self.admin.email, password='Password123')
        self.before_count = Booking.objects.count()

    def test_booking_view_urls(self):
        # Test the book_lesson view with the 'req' type
        url = reverse('book_lesson', kwargs={'id': 1, 'type': 'req'})
        self.assertEqual(url,'/book_lesson/1/')

        # Test the book_lesson view with the 'new' type
        url = reverse('book_lesson_new', kwargs={'id': 'new', 'type': 'new'})
        self.assertEqual(url,'/book_lesson/new/')

        # Test the book_lesson view with the 'user' type
        url = reverse('book_lesson_user', kwargs={'id': 1, 'type': 'user'})
        self.assertEqual(url,'/book_lesson/user/1/')

        # Test the book_lesson view with the 'edit' type
        url = reverse('book_lesson_edit', kwargs={'id': 1, 'type': 'edit'})
        self.assertEqual(url,'/book_lesson/edit/1/')

    def test_get_booking_view(self):
        # Test the book_lesson view with the 'req' type
        url = reverse('book_lesson', kwargs={'id': 1, 'type': 'req'})
        self.assertEqual(url,'/book_lesson/1/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_lesson.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, BookingForm))
        self.assertFalse(form.is_bound)

        # Test the book_lesson view with the 'new' type
        url = reverse('book_lesson_new', kwargs={'id': 'new', 'type': 'new'})
        self.assertEqual(url,'/book_lesson/new/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_lesson.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserSelectForm))
        self.assertFalse(form.is_bound)
        
        # Test the book_lesson view with the 'user' type
        url = reverse('book_lesson_user', kwargs={'id': 1, 'type': 'user'})
        self.assertEqual(url,'/book_lesson/user/1/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_lesson.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, BookingForm))
        self.assertFalse(form.is_bound)

        # Test the book_lesson view with the 'edit' type
        url = reverse('book_lesson_edit', kwargs={'id': 1, 'type': 'edit'})
        self.assertEqual(url,'/book_lesson/edit/1/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_lesson.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, BookingForm))
        self.assertFalse(form.is_bound)
        self.assertEqual(Booking.objects.count(), self.before_count)
    
    def test_successful_new_booking_form(self):
        self.url = reverse('book_lesson_new', kwargs={'id': 'new', 'type': 'new'})
        self.form_input = {'client' : self.user.id}
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('book_lesson_user', kwargs={'id': self.user.id, 'type': 'user'})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'book_lesson.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, BookingForm))
        self.assertFalse(form.is_bound)
        self.assertEqual(Booking.objects.count(), self.before_count)

    def test_insuccessful_new_booking_form(self):
        self.url = reverse('book_lesson_new', kwargs={'id': 'new', 'type': 'new'})
        self.form_input = {'client' : 'cat'}
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertTemplateUsed(response, 'book_lesson.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserSelectForm))
        self.assertEqual(Booking.objects.count(), self.before_count)

    def test_successful_edit_booking_form(self):
        self.url = reverse('book_lesson_edit', kwargs={'id': self.booking.id, 'type': 'edit'})
        self.form_input = {
            "teacher":self.teacher.id,
            "child":"1",
            "day_of_week":"3",
            "time":"13:46",
            "duration":"60",
            "days_between_lessons":"7",
            "term":"1",
            "start_date":"2022-09-01",
            "end_date":"2022-09-15"
        }
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertContains(response,'Booking updated successfully')
        self.assertTemplateUsed(response, 'book_lesson.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, BookingForm))
        self.assertTrue(form.is_bound)
        self.assertEqual(Booking.objects.count(), self.before_count)

    def test_unsuccessful_edit_booking_form(self):
        self.url = reverse('book_lesson_edit', kwargs={'id': self.booking.id, 'type': 'edit'})
        self.form_input = {
            "teacher":self.teacher.id,
            "child":"1",
            "day_of_week":"5", # wrong day of week
            "time":"13:46",
            "duration":"60",
            "days_between_lessons":"7",
            "term":"1",
            "start_date":"2022-09-01",
            "end_date":"2022-09-15"
        }
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertNotContains(response,'Booking updated successfully')
        self.assertTemplateUsed(response, 'book_lesson.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, BookingForm))
        self.assertEqual(Booking.objects.count(), self.before_count)

    def test_unsuccessful_edit_with_invalid_booking_id(self):
        self.url = reverse('book_lesson_edit', kwargs={'id': 10000, 'type': 'edit'})
        self.form_input = {
            "teacher":self.teacher.id,
            "child":"1",
            "day_of_week":"4",
            "time":"13:46",
            "duration":"60",
            "days_between_lessons":"7",
            "term":"1",
            "start_date":"2022-09-01",
            "end_date":"2022-09-15"
        }
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertContains(response,'Booking not found')
        self.assertEqual(Booking.objects.count(), self.before_count)

    def test_successful_edit_booking_form2(self):
        self.url = reverse('book_lesson_edit', kwargs={'id': self.booking2.id, 'type': 'edit'})
        self.form_input = {
            "teacher":self.teacher.id,
            "child":"1",
            "day_of_week":"3",
            "time":"13:46",
            "duration":"60",
            "days_between_lessons":"7",
            "term":"1",
            "start_date ":"2022-09-01",
            "end_date":"2022-09-15"
        }
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertContains(response,'Booking updated successfully')
        self.assertTemplateUsed(response, 'book_lesson.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, BookingForm))
        self.assertTrue(form.is_bound)
        self.assertEqual(Booking.objects.count(), self.before_count)

    def test_invoice_price_is_the_same(self):
        self.url = reverse('book_lesson_edit', kwargs={'id': self.booking.id, 'type': 'edit'})
        self.form_input = {
            "teacher":self.teacher.id,
            "child":"1",
            "day_of_week":"3",
            "time":"13:46",
            "duration":"60",
            "days_between_lessons":"7", 
            "term":"1",
            "start_date ":"2022-09-01",
            "end_date":"2022-09-15"
        }
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertContains(response,'Booking updated successfully')
        self.assertContains(response,'Invoice price is the same')
        self.assertTemplateUsed(response, 'book_lesson.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, BookingForm))
        self.assertTrue(form.is_bound)
        self.assertEqual(Booking.objects.count(), self.before_count)

    def test_invoice_price_increased_after_edit(self):
        self.url = reverse('book_lesson_edit', kwargs={'id': self.booking.id, 'type': 'edit'})
        self.form_input = {
            "teacher":self.teacher.id,
            "child":"1",
            "day_of_week":"3",
            "time":"13:46",
            "duration":"60",
            "days_between_lessons":"7",
            "term":"1",
            "start_date ":"2022-09-01",
            "end_date":"2022-09-22" # more lessons
        }
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertContains(response,'Booking updated successfully')
        self.assertContains(response,'Pricing for booking has increased')
        self.assertTemplateUsed(response, 'book_lesson.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, BookingForm))
        self.assertTrue(form.is_bound)
        self.assertEqual(Booking.objects.count(), self.before_count)


    def test_invoice_price_decreased_after_edit(self):
        self.url = reverse('book_lesson_edit', kwargs={'id': self.booking.id, 'type': 'edit'})
        self.form_input = {
            "teacher":self.teacher.id,
            "child":"1",
            "day_of_week":"3",
            "time":"13:46",
            "duration":"60",
            "days_between_lessons":"7",
            "term":"1",
            "start_date ":"2022-09-01",
            "end_date":"2022-09-8" # less lessons
        }
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertContains(response,'Booking updated successfully')
        self.assertContains(response,'Pricing for booking has decreased')
        self.assertTemplateUsed(response, 'book_lesson.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, BookingForm))
        self.assertTrue(form.is_bound)
        self.assertEqual(Booking.objects.count(), self.before_count)

    def test_invoice_price_decreased_and_needs_refund_after_edit(self):
        self.url = reverse('book_lesson_edit', kwargs={'id': self.booking.id, 'type': 'edit'})
        self.form_input = {
            "teacher":self.teacher.id,
            "child":"1",
            "day_of_week":"3",
            "time":"13:46",
            "duration":"60",
            "days_between_lessons":"7",
            "term":"1",
            "start_date ":"2022-09-01",
            "end_date":"2022-09-8" # less lessons
        }
        Transfer.objects.create(
            invoice=self.invoice,
            amount=1000,
            refund=False,
            date=datetime.today()
        )
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertContains(response,'Booking updated successfully')
        self.assertContains(response,'Pricing for booking has decreased')
        self.assertContains(response,'Client has been given a refund')
        self.assertTemplateUsed(response, 'book_lesson.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, BookingForm))
        self.assertTrue(form.is_bound)
        self.assertEqual(Booking.objects.count(), self.before_count)

    def test_successful_create_booking_from_request(self):
        self.url = reverse('book_lesson', kwargs={'id': self.request1.id, 'type': 'req'})
        self.form_input = {
            "teacher":self.teacher.id,
            "child":"1",
            "day_of_week":"3",
            "time":"13:46",
            "duration":"60",
            "days_between_lessons":"7",
            "term":"1",
            "start_date":"2022-09-01",
            "end_date":"2022-09-15"
        }
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('manage_lessons')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'manage_lessons.html')
        self.assertTrue(Request.objects.get(id=self.request1.id).fulfilled)
        self.assertEqual(Booking.objects.count(), self.before_count+1)

    def test_unsuccessful_create_booking_from_request(self):
        self.url = reverse('book_lesson', kwargs={'id': self.request1.id, 'type': 'req'})
        self.form_input = {
            "teacher":self.teacher.id,
            "child":"1",
            "day_of_week":"5", # wrong day of week
            "time":"13:46",
            "duration":"60",
            "days_between_lessons":"7",
            "term":"1",
            "start_date":"2022-09-01",
            "end_date":"2022-09-15"
        }
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertTemplateUsed(response, 'book_lesson.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, BookingForm))
        self.assertEqual(Booking.objects.count(), self.before_count)

    def test_unsuccessful_create_booking_from_request_with_invalid_id(self):
        self.url = reverse('book_lesson', kwargs={'id': 10000, 'type': 'req'})
        self.form_input = {
            "teacher":self.teacher.id,
            "child":"1",
            "day_of_week":"4",
            "time":"13:46",
            "duration":"60",
            "days_between_lessons":"7",
            "term":"1",
            "start_date":"2022-09-01",
            "end_date":"2022-09-15"
        }
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertContains(response,'Request not found')
        self.assertEqual(Booking.objects.count(), self.before_count)

    def test_create_booking_from_request_already_fulfilled_fails(self):
        self.request1.fulfilled = True
        self.request1.save()
        self.url = reverse('book_lesson', kwargs={'id':  self.request1.id, 'type': 'req'})
        self.form_input = {
            "teacher":self.teacher.id,
            "child":"1",
            "day_of_week":"4",
            "time":"13:46",
            "duration":"60",
            "days_between_lessons":"7",
            "term":"1",
            "start_date":"2022-09-01",
            "end_date":"2022-09-15"
        }
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertContains(response,'Request already fulfilled')
        self.assertEqual(Booking.objects.count(), self.before_count)

    def test_successful_create_booking_for_user(self):
        self.url = reverse('book_lesson_user', kwargs={'id': 1, 'type': 'user'})
        self.form_input = {
            "teacher":self.teacher.id,
            "child":"1",
            "day_of_week":"3",
            "time":"13:46",
            "duration":"60",
            "days_between_lessons":"7",
            "term":"1",
            "start_date":"2022-09-01",
            "end_date":"2022-09-15"
        }
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('manage_lessons')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'manage_lessons.html')
        self.assertEqual(Booking.objects.count(), self.before_count+1)

    def test_unsuccessful_create_for_user(self):
        self.url = reverse('book_lesson_user', kwargs={'id': 1, 'type': 'user'})
        self.form_input = {
            "teacher":self.teacher.id,
            "child":"1",
            "day_of_week":"5", # wrong day of week
            "time":"13:46",
            "duration":"60",
            "days_between_lessons":"7",
            "term":"1",
            "start_date":"2022-09-01",
            "end_date":"2022-09-15"
        }
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertTemplateUsed(response, 'book_lesson.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, BookingForm))

    def test_unsuccessful_create_booking_for_user_with_invalid_user_id(self):
        self.url = reverse('book_lesson_user', kwargs={'id': 100000, 'type': 'user'})
        self.form_input = {
            "teacher":self.teacher.id,
            "child":"1",
            "day_of_week":"4",
            "time":"13:46",
            "duration":"60",
            "days_between_lessons":"7",
            "term":"1",
            "start_date":"2022-09-01",
            "end_date":"2022-09-15"
        }
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertContains(response,'User not found')
        self.assertEqual(Booking.objects.count(), self.before_count)

    def test_create_booking_from_request_with_user_not_student(self):
        self.url = reverse('book_lesson_user', kwargs={'id': self.admin.id, 'type': 'user'})
        self.form_input = {
            "teacher":self.teacher.id,
            "child":"1",
            "day_of_week":"4",
            "time":"13:46",
            "duration":"60",
            "days_between_lessons":"7",
            "term":"1",
            "start_date":"2022-09-01",
            "end_date":"2022-09-15"
        }
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertContains(response,'This user is not a student')
        self.assertEqual(Booking.objects.count(), self.before_count)
    