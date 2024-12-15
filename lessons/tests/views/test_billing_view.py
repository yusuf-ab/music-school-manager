from django.test import TestCase
from django.urls import reverse
from lessons.models import User, Child, Request, Booking, Transfer, Invoice
from datetime import date, time, timedelta

class BillingViewTestCase(TestCase):
    """Tests of the billing view."""

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

        self.invoice = Invoice.objects.create(
            booking=self.booking,
            invoice_ref=self.booking.invoice_reference(),
            date="2022-11-21",
            due_by_date=self.booking.date,
            amount=self.booking.calculate_price(),
            refund=False
        )

        Transfer.objects.create(
            invoice=self.invoice,
            date="2022-11-21",
            amount=self.booking.calculate_price(),
            refund=False
         )

        Transfer.objects.create(
            invoice=self.invoice,
            date="2022-11-21",
            amount=self.booking.calculate_price(),
            refund=False
         )

        Transfer.objects.create(
            invoice=self.invoice,
            date="2022-11-21",
            amount=self.booking.calculate_price(),
            refund=False
         )


        self.url = reverse('billing', kwargs={})
        self.client.login(username='marty.major@example.org', password='Password123')

    def test_billing_url(self):
        self.assertEqual(self.url,'/billing/')
    
    def test_get_billing(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'billing.html')

    def test_view_shows_all_students_balances(self):
        response = self.client.get(self.url)
        for student in User.objects.filter(role=User.STUDENT):
            self.assertContains(response,f'{student.id}')
            self.assertContains(response,f'{student.total_invoice_amount():.2f}')
            self.assertContains(response,f'{student.total_paid_net():.2f}')
            self.assertContains(response,f'{student.total_owed():.2f}')

    def test_view_shows_all_invoices_info(self):
        response = self.client.get(self.url)
        for invoice in Invoice.objects.all():
            self.assertContains(response,f'{invoice.invoice_ref}')
            self.assertContains(response,f'{invoice.amount:.2f}')
            self.assertContains(response,f'{invoice.net_paid():.2f}')

    def test_view_shows_all_trasfer_info(self):
        response = self.client.get(self.url)
        for transfer in Transfer.objects.all():
            self.assertContains(response,f'{transfer.id}')
            self.assertContains(response,f'{transfer.amount:.2f}')