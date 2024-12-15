from django.test import TestCase
from django.urls import reverse
from lessons.models import User, Child, Request, Booking, Transfer, Invoice
from datetime import date, time, timedelta
from lessons.forms import TransferForm

class PaymentsViewTestCase(TestCase):
    """Tests of the payments view."""

    fixtures = [
        'lessons/tests/fixtures/test_data.json',
    ]

    def setUp(self):
        self.user = User.objects.get(email="john.doe@example.org")
        self.user2 = User.objects.get(email="ryan.fuller@example.org")
        self.teacher = User.objects.get(email="jane.doe@example.org")
        self.child = Child.objects.get(first_name="Alice",last_name="Doe")

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

        self.invoice = Invoice.objects.create(
            booking=self.booking,
            invoice_ref=self.booking.invoice_reference(),
            date="2022-11-21",
            due_by_date=self.booking.date,
            amount=100,
            refund=False
        )

        Transfer.objects.create(
            invoice=self.invoice,
            date="2022-11-21",
            amount=1,
            refund=False
         )

        Transfer.objects.create(
            invoice=self.invoice,
            date="2022-11-21",
            amount=1,
            refund=False
         )

        Transfer.objects.create(
            invoice=self.invoice,
            date="2022-11-21",
            amount=1,
            refund=False
         )


        self.url = reverse('payments', kwargs={})
        self.client.login(username=self.user.email, password='Password123')

    def test_billing_url(self):
        self.assertEqual(self.url,'/payments/')
    
    def test_get_billing(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TransferForm))
        self.assertFalse(form.is_bound)

    def test_successful_payment_form(self):
        self.form_input = {
            "invoice":"1",
            "amount":"1",
            "date":"2022-12-01"
        }
        before_count = Transfer.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Transfer.objects.count()
        self.assertEqual(after_count, before_count+1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TransferForm))
        self.assertContains(response,"left to pay on this invoice")
        self.assertTrue(form.is_valid())

    def test_unsuccessful_payment_form(self):
        self.form_input = {
            "invoice":"10000",
            "amount":"-1",#invalid amount
            "date":"2022-12-01"
        }
        before_count = Transfer.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Transfer.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TransferForm))
        self.assertFalse(form.is_valid())

    def test_pay_exact_amount(self):
        self.form_input = {
            "invoice":"1",
            "amount":"97",
            "date":"2022-12-01"
        }
        before_count = Transfer.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Transfer.objects.count()
        self.assertEqual(after_count, before_count+1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TransferForm))
        self.assertContains(response,"This invoice has now been fully paid")
        self.assertTrue(form.is_valid())

    def test_overpaid(self):
        self.form_input = {
            "invoice":"1",
            "amount":"1000",
            "date":"2022-12-01"
        }
        before_count = Transfer.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Transfer.objects.count()
        self.assertEqual(after_count, before_count+2)# 1 payment, 1 refund transfer
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TransferForm))
        self.assertContains(response,"You have overpaid")
        self.assertTrue(form.is_valid())

    def test_view_shows_all_students_balance_info(self):
        response = self.client.get(self.url)
        self.assertContains(response,f'{self.user.total_invoice_amount():.2f}')
        self.assertContains(response,f'{self.user.total_owed():.2f}')
        self.assertContains(response,f'{self.user.total_paid_net():.2f}')

    def test_view_shows_all_invoices(self):
        response = self.client.get(self.url)
        for invoice in Invoice.objects.all():
            self.assertContains(response,f'{invoice.amount:.2f}')
            self.assertContains(response,f'{invoice.net_paid():.2f}')

    def test_view_shows_all_transfers(self):
        response = self.client.get(self.url)
        for transfer in self.user.transfers():
            self.assertContains(response,f'{transfer.amount:.2f}')