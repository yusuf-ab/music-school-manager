from django.test import TestCase
from django.urls import reverse
from lessons.models import Invoice, Booking, User

class InvoiceViewTest(TestCase):

    fixtures = ['lessons/tests/fixtures/test_data.json']

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
        self.invoice.save()
        self.url = reverse('invoice', kwargs={'id': self.invoice.id})
        self.client.login(username='john.doe@example.org', password='Password123')

    def test_invoice_view_url(self):
        self.assertEqual(self.url,f'/invoice/{self.invoice.id}/')

    def test_get_invoice_view_with_valid_id(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoice.html')
        self.assertContains(response, self.invoice.invoice_ref)
        self.assertContains(response, self.invoice.amount)

    def test_get_invoice_view_with_invalid_id(self):
        url = reverse('invoice', kwargs={'id': self.invoice.id+1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, 'invoice.html')
        self.assertContains(response, 'Invoice not found')

    def test_student_cant_see_other_students_invoice(self):
        self.client.login(username='ryan.fuller@example.org', password='Password123')
        url = reverse('invoice', kwargs={'id': self.invoice.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, 'invoice.html')
        self.assertContains(response, 'You cannot view this invoice')
