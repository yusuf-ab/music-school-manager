from django import forms
from django.test import TestCase
from lessons.forms import InvoiceForm
from lessons.models import Booking, User

class InvoiceFormTestCase(TestCase):
    """Unit tests of the InvoiceForm"""
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
        self.form_input = {
            'booking':self.booking,
            'invoice_ref':self.booking.invoice_reference(),
            'date':"2022-11-21",
            'due_by_date':self.booking.date,
            'amount':self.booking.calculate_price(),
            'refund':False
        }


    def test_form_has_necessary_fields(self):
        form = InvoiceForm()
        self.assertIn('invoice_ref', form.fields)
        self.assertTrue(isinstance(form.fields['invoice_ref'], forms.CharField))
        self.assertIn('date', form.fields)
        self.assertTrue(isinstance(form.fields['date'], forms.DateField))
        self.assertIn('due_by_date', form.fields)
        self.assertTrue(isinstance(form.fields['due_by_date'], forms.DateField))
        self.assertIn('amount', form.fields)
        self.assertTrue(isinstance(form.fields['amount'], forms.DecimalField))
        self.assertIn('refund', form.fields)
        self.assertTrue(isinstance(form.fields['refund'], forms.BooleanField))

    def test_form_accepts_valid_input(self):
        form = InvoiceForm(data=self.form_input)
        self.assertTrue(form.is_valid())


    def test_form_rejects_no_booking(self):
        self.form_input['booking'] = None
        form = InvoiceForm(data=self.form_input)
        self.assertFalse(form.is_valid())


    def test_form_rejects_no_invoice_ref(self):
        self.form_input['invoice_ref'] = ''
        form = InvoiceForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_invoice_ref_more_than_20_chars(self):
        self.form_input['invoice_ref'] = 'x'*21
        form = InvoiceForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_accepts_invoice_ref_has_20_chars(self):
        self.form_input['invoice_ref'] = 'x'*20
        form = InvoiceForm(data=self.form_input)
        self.assertTrue(form.is_valid())


    def test_form_rejects_no_date(self):
        self.form_input['date'] = ''
        form = InvoiceForm(data=self.form_input)
        self.assertFalse(form.is_valid())


    def test_form_rejects_no_due_by_date(self):
        self.form_input['due_by_date'] = ''
        form = InvoiceForm(data=self.form_input)
        self.assertFalse(form.is_valid())


    def test_form_rejects_no_amount(self):
        self.form_input['amount'] = ''
        form = InvoiceForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_amount_with_more_than_19_digits(self):
        self.form_input['amount'] = 123456789012345678.90
        form = InvoiceForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_accepts_amount_with_19_digits(self):
        self.form_input['amount'] = 12345678901234567.89
        form = InvoiceForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_amount_less_than_1(self):
        self.form_input['amount'] = 0.99
        form = InvoiceForm(data=self.form_input)
        self.assertFalse(form.is_valid())


    def test_form_accepts_no_refund(self):
        self.form_input['refund'] = ''
        form = InvoiceForm(data=self.form_input)
        self.assertTrue(form.is_valid())
