"""Tests of the edit term view."""
from django.test import TestCase
from django.urls import reverse
from lessons.forms import TermForm
from lessons.models import User, Term
from lessons.tests.helpers import LogInTester


class EditRequestTestCase(TestCase,LogInTester):
    """Tests of the edit term view."""

    fixtures = [
        'lessons/tests/fixtures/test_data.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email="marty.major@example.org")
        self.form_input = {
            "name":"Term 1",
            "start_date":"2022-09-01",
            "end_date":"2022-10-22"
        }
        self.url = reverse('edit_term', kwargs={'id': 1 })
        self.client.login(email=self.user.email, password='Password123')

    def test_edit_term_url(self):
        self.assertEqual(self.url,f'/edit_term/1')

    def test_get_edit_term(self):
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_term.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TermForm))
        self.assertFalse(form.is_bound)

    def test_unsuccesful_term_edit(self):
        self.form_input['end_date'] = '2020-09-01' # End date before start date
        before_count = Term.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Term.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_term.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TermForm))
        self.assertTrue('End date has to be after the start date' in form.errors.as_text())
        self.assertFalse(form.is_valid())

    def test_succesful_term_edit(self):
        self.form_input['name'] = 'Term 0'
        before_count = Term.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Term.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('terms')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        term = Term.objects.get(id=1)
        self.assertEqual(term.name, self.form_input['name'])

    def test_edit_term_with_id_that_does_not_exist(self):
        url = reverse('edit_term', kwargs={'id': 10000 })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, 'edit_term.html')
        self.assertContains(response, 'Term not found')