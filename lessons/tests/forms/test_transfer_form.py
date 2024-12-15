from django import forms
from django.test import TestCase
from lessons.forms import TransferForm
from lessons.models import User, Invoice, Booking
from datetime import datetime, timedelta

class TransferFormTestCase(TestCase):
    """Unit tests of the TransferForm"""
    fixtures = [
        'lessons/tests/fixtures/test_data.json'
    ]
    def setUp(self):
        self.client = User.objects.get(email="john.doe@example.org")
        self.booking = Booking(
            id=10000,
            client=self.client,
            lessons=3,
            days_between_lessons=7,
            duration=60,
            teacher=User.objects.get(email="jane.doe@example.org"),
            date=datetime.today()+timedelta(days=1),
            time=datetime.now().time())

        self.booking.save()
        self.invoice = Invoice(
            id=10000,
            booking=self.booking,
            invoice_ref=self.booking.invoice_reference(),
            date=datetime.today(),
            due_by_date=self.booking.date,
            amount=self.booking.calculate_price(),
            refund=False
        )
        self.invoice.save()

        self.form_input = {
            "invoice":"10000",
            "amount":"0.03",
            "date":"2022-12-01"

        }

    def test_form_has_necessary_fields(self):
        form = TransferForm(user=self.client)
        self.assertIn('invoice', form.fields)
        self.assertTrue(isinstance(form.fields['invoice'], forms.ModelChoiceField))
        self.assertIn('amount', form.fields)
        self.assertTrue(isinstance(form.fields['amount'], forms.DecimalField))
        self.assertIn('date', form.fields)
        self.assertTrue(isinstance(form.fields['date'], forms.DateField))

    def test_form_accepts_valid_input(self):
        form = TransferForm(user=self.client,data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_invalid_invoice(self):
        self.form_input['invoice'] = '100'
        form = TransferForm(user=self.client,data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_no_invoice_selected(self):
        self.form_input['invoice'] = ''
        form = TransferForm(user=self.client,data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_no_amount(self):
        self.form_input['amount'] = ''
        form = TransferForm(user=self.client,data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_negative_amount(self):
        self.form_input['amount'] = '-100'
        form = TransferForm(user=self.client,data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_zero_amount(self):
        self.form_input['amount'] = '0'
        form = TransferForm(user=self.client,data=self.form_input)
        self.assertFalse(form.is_valid())
    
    def test_form_accepts_small_amount(self):
        self.form_input['amount'] = '0.02'
        form = TransferForm(user=self.client,data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_amount_smaller_than_a_penny(self):
        self.form_input['amount'] = '0.001'
        form = TransferForm(user=self.client,data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_accepts_large_amount(self):
            self.form_input['amount'] = '100000'
            form = TransferForm(user=self.client,data=self.form_input)
            self.assertTrue(form.is_valid())

    def test_form_rejects_no_date(self):
            self.form_input['date'] = '2020-2022-2022'
            form = TransferForm(user=self.client,data=self.form_input)
            self.assertFalse(form.is_valid())

    def test_form_rejects_invalid_date(self):
            self.form_input['date'] = '2020-2022-2022'
            form = TransferForm(user=self.client,data=self.form_input)
            self.assertFalse(form.is_valid())

    def test_form_invoice_field_has_correct_amount_of_choices(self):
        form = TransferForm(user=self.client,data=self.form_input)
        self.assertEqual(len(form.fields['invoice'].queryset),len(Invoice.objects.filter(booking__client=self.client)))