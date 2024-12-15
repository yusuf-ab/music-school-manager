from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import User, Booking, Invoice, Transfer

class TransferModelTestCase(TestCase):
    """Unit tests for the Transfer model."""

    fixtures = [
        'lessons/tests/fixtures/test_data.json'
    ]
    def setUp(self):
        self.client = User.objects.get(email="john.doe@example.org")
        self.booking = Booking.objects.create(
            client=self.client,
            lessons=3,
            days_between_lessons=7,
            duration=60,
            teacher=User.objects.get(email="jane.doe@example.org"),
            date="2022-11-28",
            time="19:36:59.149"
        )

        self.booking.save()
        self.invoice = Invoice.objects.create(
            booking=self.booking,
            invoice_ref=self.booking.invoice_reference(),
            date="2022-11-21",
            due_by_date=self.booking.date,
            amount=self.booking.calculate_price(),
            refund=False
        )
        # User pays £20
        self.transfer= Transfer.objects.create(
            invoice=self.invoice,
            date="2022-11-21",
            amount=20,
            refund=False)
        
    def test_amount_cannot_be_negative(self):
        self.transfer.amount = -1
        self._assert_transfer_is_invalid()

    def test_amount_cannot_be_zero(self):
        self.transfer.amount = 0
        self._assert_transfer_is_invalid()

    def test_amount_cannot_be_none(self):
        self.transfer.amount = None
        self._assert_transfer_is_invalid()

    def test_date_cannot_be_none(self):
        self.transfer.date = None
        self._assert_transfer_is_invalid()
    
    def test_invoice_cannot_be_none(self):
        self.transfer.invoice = None
        self._assert_transfer_is_invalid()

    def test_valid_transfer(self):
        self._assert_transfer_is_valid()

    def test_booking_invoice_transfers_are_linked_to_user(self):
        self.assertIn(self.booking,self.client.bookings())
        self.assertIn(self.invoice,self.client.invoices())
        self.assertIn(self.transfer,self.client.transfers())

    def test_invoice_payments(self):
        # User pays another £30
        Transfer.objects.create(
            invoice=self.invoice,
            date="2022-11-21",
            amount=30,
            refund=False)

        self.assertEqual(self.booking.get_invoice,self.invoice)
        self.assertEqual(self.client.total_invoice_amount(), self.booking.calculate_price())
        self.assertEqual(self.client.total_paid(), 50) #20+30

        # User is refunded £10
        Transfer.objects.create(
            invoice=self.invoice,
            date="2022-11-21",
            amount=10,
            refund=True
         )

        # 10 pounds refunded
        self.assertEqual(self.client.total_refunded(), 10)
        self.assertEqual(self.client.total_paid_net(), 40 ) # 50 - 10 = 40
        self.assertEqual(self.invoice.net_paid(), 40)
        # How much is left to pay
        self.assertEqual(self.client.total_owed(), self.booking.calculate_price()-40) 

        self.assertFalse(self.invoice.paid())
        
        # Pay full amount
        Transfer.objects.create(
            invoice=self.invoice,
            date="2022-11-21",
            amount=self.booking.calculate_price(),
            refund=False
         )
        self.assertTrue(self.invoice.paid())



    def _assert_transfer_is_valid(self):
        try:
            self.transfer.full_clean()
        except (ValidationError):
            self.fail('Test transfer should be valid')

    def _assert_transfer_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.transfer.full_clean()
