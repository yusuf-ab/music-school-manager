from django import forms
from django.test import TestCase
from lessons.forms import BookingForm
from lessons.models import User, Term
from datetime import date

class BookingFormTestCase(TestCase):
    """Unit tests of the BookingForm"""
    fixtures = [
        'lessons/tests/fixtures/test_data.json'
    ]
    def setUp(self):
        self.client = User.objects.get(email="john.doe@example.org")
        self.form_input = {
            "teacher": User.objects.get(email="jane.doe@example.org"),
            "child":"1",
            "day_of_week":"0", # Monday
            "time":"16:00",
            "duration":"60",
            "days_between_lessons":"7",
            "term":"1", # Sept. 1, 2022 - Oct. 21, 2022
            "start_date":"2022-9-05", # Monday
            "end_date":"2022-9-19" # 3 weeks of lessons
        }

    def test_form_has_necessary_fields(self):
        form = BookingForm(user=self.client)
        self.assertIn('teacher', form.fields)
        self.assertTrue(isinstance(form.fields['teacher'], forms.ModelChoiceField))
        self.assertIn('child', form.fields)
        self.assertTrue(isinstance(form.fields['child'], forms.ModelChoiceField))
        self.assertIn('day_of_week', form.fields)
        self.assertTrue(isinstance(form.fields['day_of_week'], forms.ChoiceField))
        self.assertIn('time', form.fields)
        self.assertTrue(isinstance(form.fields['time'], forms.TimeField))
        self.assertIn('duration', form.fields)
        self.assertTrue(isinstance(form.fields['duration'], forms.TypedChoiceField))
        self.assertIn('days_between_lessons', form.fields)
        self.assertTrue(isinstance(form.fields['days_between_lessons'], forms.TypedChoiceField))
        self.assertIn('term', form.fields)
        self.assertTrue(isinstance(form.fields['term'], forms.ModelChoiceField))
        self.assertIn('start_date', form.fields)
        self.assertTrue(isinstance(form.fields['start_date'], forms.DateField))
        self.assertIn('end_date', form.fields)
        self.assertTrue(isinstance(form.fields['end_date'], forms.DateField))

    def test_form_accepts_valid_input(self):
        form = BookingForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertTrue(form.is_valid())
        # Test form books right amount of lessons
        self.assertEqual(form.instance.lessons,3)

    def test_form_books_correct_number_of_lessons_when_its_every_two_weeks(self):
        self.form_input["days_between_lessons"] = "14"
        form = BookingForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertTrue(form.is_valid())
        self.assertEqual(form.instance.lessons,2)

    def test_form_books_corrent_amount_of_lessons_without_start_and_end_dates(self):
        self.form_input.pop('start_date')
        self.form_input.pop('end_date')
        form = BookingForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertTrue(form.is_valid())
        # Test form books right amount of lessons
        self.assertEqual(form.instance.lessons,7)

    def test_form_books_less_lessons_when_start_date_skips_first_week_of_term(self):
        self.form_input["start_date"] = "2022-9-12"
        self.form_input.pop('end_date')
        form = BookingForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertTrue(form.is_valid())
        # Test form books right amount of lessons
        self.assertEqual(form.instance.lessons,6)

    def test_form_books_less_lessons_when_end_date_skips_last_week_of_term(self):
        self.form_input["end_date"] = "2022-10-10"
        self.form_input.pop('start_date')
        form = BookingForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertTrue(form.is_valid())
        # Test form books right amount of lessons
        self.assertEqual(form.instance.lessons,6)

    def test_form_checks_start_date_is_correct_weekday(self):
        self.form_input["start_date"] = "2022-9-13"
        form = BookingForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertFalse(form.is_valid())
        self.assertTrue('Date does not match selected day of the week' in str(form.errors['start_date']))

    def test_form_checks_end_date_is_correct_weekday(self):
        self.form_input["end_date"] = "2022-9-11"
        form = BookingForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertFalse(form.is_valid())
        self.assertTrue('Date does not match selected day of the week' in str(form.errors['end_date']))

    def test_form_checks_start_date_in_selected_term(self):
        self.form_input["start_date"] = "2022-1-1"
        form = BookingForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertFalse(form.is_valid())
        self.assertTrue('Date is not within selected term' in str(form.errors['start_date']))

    def test_form_checks_end_date_in_selected_term(self):
        self.form_input["end_date"] = "2022-1-1"
        form = BookingForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertFalse(form.is_valid())
        self.assertTrue('Date is not within selected term' in str(form.errors['end_date']))

    def test_form_rejects_end_date_after_start_date(self):
        # switch dates
        self.form_input["end_date"],self.form_input["start_date"] = self.form_input["start_date"],self.form_input["end_date"]
        form = BookingForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertFalse(form.is_valid())
        self.assertTrue('End date needs to be after start date' in str(form.errors['end_date']))

    def test_form_fails_to_book_lesson_when_no_lessons_are_possible(self):
        term = Term.objects.get(name="Term one")
        term.end_date = date(2022,9,2)# Make term 1 day long
        term.save()
        self.form_input.pop('start_date')
        self.form_input.pop('end_date')
        form = BookingForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertFalse(form.is_valid())
        self.assertTrue('No lessons were able to be booked within these constraints' in str(form.errors['end_date']))

    def test_form_sets_initial_day_of_week_and_time_when_booking_is_being_edited(self):
        form = BookingForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertTrue(form.is_valid())
        booking = form.save()

        form = BookingForm(user=self.client, data=self.form_input, instance=booking)
        form.instance.client = self.client
        self.assertEqual(form.initial['day_of_week'],0)
        self.assertEqual(form.initial['start_date'],date(2022, 9, 5))
        self.assertTrue(form.is_valid())