"""Tests of the log in view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from lessons.forms import LogInForm
from lessons.models import User
from lessons.tests.helpers import LogInTester

class LogInViewTestCase(TestCase, LogInTester):
    """Tests of the log in view."""
    fixtures = [
        'lessons/tests/fixtures/test_data.json'
    ]
    def setUp(self):
        self.url = reverse('log_in')
        self.user = User.objects.get(email='john.doe@example.org')
        self.director = User.objects.get(email="marty.major@example.org")

    def test_log_in_url(self):
        self.assertEqual(self.url,'/log_in/')

    def test_get_log_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_unsuccesful_log_in(self):
        form_input = { 'email': 'john.doe@example.org', 'password': 'WrongPassword123' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_log_in_with_blank_email(self):
        form_input = { 'email': '', 'password': 'Password123' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_log_in_with_blank_password(self):
        form_input = { 'email': 'john.doe@example.org', 'password': '' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_succesful_log_in(self):
        form_input = { 'email': 'john.doe@example.org', 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('list_lessons')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        #messages_list = response.context['messages']
        #self.assertEqual(len(messages_list), 0)

    def test_succesful_log_in_with_redirect(self):
        redirect_url = reverse('children')
        form_input = { 'email': 'john.doe@example.org', 'password': 'Password123','next': redirect_url}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_student_log_in_redirect(self):
        form_input = { 'email': 'john.doe@example.org', 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('list_lessons')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_admin_log_in_redirect(self):
        form_input = { 'email': 'petra.pickles@example.org', 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('manage_lessons')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_director_log_in_redirect(self):
        form_input = { 'email': 'marty.major@example.org', 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('permissions')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_teacher_redirect(self):
        form_input = { 'email': 'jane.doe@example.org', 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('schedule')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_other_role_redirect(self):
        self.user.role = "Other Role"
        self.user.save()
        form_input = { 'email': 'john.doe@example.org', 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_valid_log_in_by_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        form_input = { 'email': 'john.doe@example.com', 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
