from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import Invoice, Booking, User

class InvoiceModelTestCase(TestCase):
    """Unit tests for the Invoice model."""
    fixtures = [
        'lessons/tests/fixtures/test_data.json'
    ]
    def setUp(self):
        self.booking = Booking(
            client=User.objects.get(email="john.doe@example.org"),
            lessons=3,
            days_between_lessons=7,
            duration=60,
            teacher=User.objects.get(email="jane.doe@example.org"),
            date="2022-11-28",
            time="19:36:59.149"
        )

        self.booking.save()
        self.invoice = Invoice(
            booking=self.booking,
            invoice_ref=self.booking.invoice_reference(),
            date="2022-11-21",
            due_by_date=self.booking.date,
            amount=self.booking.calculate_price(),
            refund=False
        )

    def test_booking_must_not_be_blank(self):
        self.invoice.booking = None
        self._assert_invoice_is_invalid()


    def test_invoice_ref_must_not_be_blank(self):
        self.invoice.invoice_ref = ''
        self._assert_invoice_is_invalid()

    def test_invoice_ref_may_contain_20_characters(self):
        self.invoice.invoice_ref = 'x' * 20
        self._assert_invoice_is_valid()

    def test_invoice_ref_must_not_contain_more_than_20_characters(self):
        self.invoice.invoice_ref = 'x' * 21
        self._assert_invoice_is_invalid()

    def test_date_must_not_be_blank(self):
        self.invoice.date = ''
        self._assert_invoice_is_invalid()


    def test_due_by_date_must_not_be_blank(self):
        self.invoice.due_by_date = ''
        self._assert_invoice_is_invalid()


    def test_amount_must_not_be_blank(self):
        self.invoice.amount = ''
        self._assert_invoice_is_invalid()


    def test_amount_may_be_19_digits(self):
        self.invoice.amount = 12345678901234567.89
        self._assert_invoice_is_valid()

    def test_amount_must_not_be_more_than_19_digits(self):
        self.invoice.amount = 123456789012345678.90
        self._assert_invoice_is_invalid()

    def test_amount_cannot_have_less_than_2_decimal_places(self):
        self.invoice.amount = 5.1
        self._assert_invoice_is_invalid()

    def test_amount_may_not_be_less_than_1(self):
        self.invoice.amount = 0.99
        self._assert_invoice_is_invalid()


    def test_refund_must_not_be_blank(self):
        self.invoice.refund = None
        self._assert_invoice_is_invalid()

    def test_string_format(self):
        self.assertEqual(str(self.invoice),str(self.invoice.invoice_ref) )

    def _assert_invoice_is_valid(self):
        try:
            self.invoice.full_clean()
        except (ValidationError):
            self.fail('Test invoice should be valid')

    def _assert_invoice_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.invoice.full_clean()
