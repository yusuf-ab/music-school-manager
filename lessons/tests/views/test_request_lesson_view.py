"""Tests of the lesson request view."""
from django.test import TestCase
from django.urls import reverse
from lessons.forms import CreateLessonRequestForm
from lessons.models import User, Request
from lessons.tests.helpers import LogInTester


class LessonRequestTestCase(TestCase,LogInTester):
    """Tests of the lesson request view."""

    fixtures = [
        'lessons/tests/fixtures/test_data.json'
    ]

    def setUp(self):
        self.url = reverse('lessons')
        self.form_input = {
            'availability': 'I prefer lessons on Friday, after school',
            'lessons': 3,
            'days_between_lessons': 14,
            'duration': 60,
            'info': 'I would like to learn how to play the piano',
            'child': ''
        }
        self.client.login(username='john.doe@example.org', password='Password123')

    def test_request_form_url(self):
        self.assertEqual(self.url,'/lessons/')

    def test_get_request(self):
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_lesson_request.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateLessonRequestForm))
        self.assertFalse(form.is_bound)

    def test_unsuccesful_request(self):
        self.form_input['lessons'] = '-1' # Incorrect number of lessons
        before_count = Request.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Request.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_lesson_request.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateLessonRequestForm))
        self.assertTrue('Ensure this value is greater than or equal to 1.' in form.errors.as_text())
        self.assertFalse(form.is_valid())

    def test_succesful_request(self):
        before_count = Request.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Request.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('list_lessons')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        request = Request.objects.get(info='I would like to learn how to play the piano')
        self.assertEqual(request.availability, self.form_input['availability'])
        self.assertEqual(request.lessons, self.form_input['lessons'])
        self.assertEqual(request.days_between_lessons, self.form_input['days_between_lessons'])
        self.assertEqual(request.duration, self.form_input['duration'])
        self.assertEqual(request.info, self.form_input['info'])
        self.assertEqual(request.availability, self.form_input['availability'])

    def test_succesful_request_with_child(self):
        self.form_input['child'] = 1
        before_count = Request.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Request.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('list_lessons')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        request = Request.objects.get(info='I would like to learn how to play the piano')
        self.assertEqual(request.availability, self.form_input['availability'])
        self.assertEqual(request.lessons, self.form_input['lessons'])
        self.assertEqual(request.days_between_lessons, self.form_input['days_between_lessons'])
        self.assertEqual(request.duration, self.form_input['duration'])
        self.assertEqual(request.info, self.form_input['info'])
        self.assertEqual(request.availability, self.form_input['availability'])
        self.assertEqual(request.child.id, self.form_input['child'])

    def test_unsuccesful_request_child(self):
        self.form_input['child'] = 10 # Invalid child id
        before_count = Request.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Request.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_lesson_request.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateLessonRequestForm))
        self.assertTrue('That choice is not one of the available choices.' in form.errors.as_text())
        self.assertFalse(form.is_valid())
