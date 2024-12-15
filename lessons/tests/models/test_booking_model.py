from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import User, Request, Child, Booking
from datetime import date, time, timedelta
from decimal import Decimal

class BookingModelTestCase(TestCase):
    """Unit tests for the Booking model."""

    fixtures = [
        'lessons/tests/fixtures/test_data.json'
    ]
    def setUp(self):
        self.client = User.objects.get(email="john.doe@example.org")
        self.teacher = User.objects.get(email="jane.doe@example.org")
        self.child = Child.objects.get(first_name="Alice",last_name="Doe")
        self.request = Request.objects.create(
            client=self.client,
            availability="Any time",
            lessons="1",
            days_between_lessons="7",
            duration="60",
            info="Piano",
            child=self.child
        )
        self.booking = Booking.objects.create(
            client=self.client,
            lessons=2,
            days_between_lessons=7,
            duration=60,
            teacher=self.teacher,
            date=date(2022,1,1),
            time=time(16),
            child=self.child
        )

    def test_valid_booking(self):
        self._assert_booking_is_valid()

    def test_lessons_must_not_be_blank(self):
        self.booking.lessons = None
        self._assert_booking_is_invalid()

    def test_lessons_cannot_be_negative(self):
        self.booking.lessons = -1
        self._assert_booking_is_invalid()

    def test_lessons_cannot_be_zero(self):
        self.booking.lessons = 0
        self._assert_booking_is_invalid()

    def test_lessons_cannot_be_none(self):
        self.booking.lessons = None
        self._assert_booking_is_invalid()

    def test_days_between_lessons_must_not_be_blank(self):
        self.booking.days_between_lessons = None
        self._assert_booking_is_invalid()

    def test_duration_must_not_be_blank(self):
        self.booking.duration = None
        self._assert_booking_is_invalid()

    def test_date_must_not_be_blank(self):
        self.booking.date = None
        self._assert_booking_is_invalid()
        
    def test_time_must_not_be_blank(self):
        self.booking.time = None
        self._assert_booking_is_invalid()

    def test_teacher_must_not_be_blank(self):
        self.booking.teacher = None
        self._assert_booking_is_invalid()

    def test_duration_cannot_be_negative(self):
        self.booking.duration = -1
        self._assert_booking_is_invalid()

    def test_duration_cannot_be_zero(self):
        self.booking.duration = 0
        self._assert_booking_is_invalid()

    def test_child_can_be_blank(self):
        self.booking.child = None
        self._assert_booking_is_valid()

    def test_child_must_belong_to_client(self):
        self.child.parent = User.objects.get(email="ryan.fuller@example.org")
        self.child.save()
        self._assert_booking_is_invalid()

    def test_invoice_referance_id(self):
        self.assertEqual(self.booking.invoice_reference(),f"{self.client.id}-{self.booking.id}")

    def test_price(self):
        self.assertEqual(self.booking.calculate_price(),Decimal(30 * (Decimal(self.booking.lessons) * (Decimal(self.booking.duration)/Decimal(60)))))

    def test_invoice_referance_id(self):
        self.assertEqual(self.booking.invoice_reference(),f"{self.client.id}-{self.booking.id}")

    def test_lesson_dates(self):
        self.assertEqual(self.booking.dates(),[date(2022, 1, 1),date(2022, 1, 8)])

    def test_properties(self):
        self.assertEqual(self.booking.between_name,self.booking.get_days_between_lessons_display())
        self.assertEqual(self.booking.duration_name,self.booking.get_duration_display())

    def test_booking_date(self):
        self.assertEqual(self.booking.day(),self.booking.date.weekday())

    def _assert_booking_is_valid(self):
        try:
            self.booking.full_clean()
        except (ValidationError):
            self.fail('Test booking should be valid')

    def _assert_booking_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.booking.full_clean()
