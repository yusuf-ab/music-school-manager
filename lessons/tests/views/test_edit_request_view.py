"""Tests of the edit request view."""
from django.test import TestCase
from django.urls import reverse
from lessons.forms import CreateLessonRequestForm
from lessons.models import User, Request, Child
from lessons.tests.helpers import LogInTester


class EditRequestTestCase(TestCase,LogInTester):
    """Tests of the edit request view."""

    fixtures = [
        'lessons/tests/fixtures/test_data.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email="john.doe@example.org")
        self.user2 = User.objects.get(email="ryan.fuller@example.org")
        self.teacher = User.objects.get(email="jane.doe@example.org")
        self.child = Child.objects.get(first_name="Alice",last_name="Doe")
        self.form_input = {
            'availability': 'Any time',
            'lessons': 1,
            'days_between_lessons': 7,
            'duration': 60,
            'info': 'Piano',
            'child': self.child.id
        }

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
            client=self.user2,
            availability="Any time",
            lessons="1",
            days_between_lessons="7",
            duration="60",
            info="Piano"
        )
        self.url = reverse('edit_request', kwargs={'id': self.request1.id })
        self.client.login(username='john.doe@example.org', password='Password123')

    def test_edit_request_url(self):
        self.assertEqual(self.url,f'/edit_request/{self.request1.id}/')

    def test_get_edit_request(self):
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
        self.assertNotContains(response,"Request updated successfully")
        self.assertTemplateUsed(response, 'create_lesson_request.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateLessonRequestForm))
        self.assertTrue('Ensure this value is greater than or equal to 1.' in form.errors.as_text())
        self.assertFalse(form.is_valid())

    def test_succesful_request(self):
        before_count = Request.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Request.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('list_lessons')
        self.assertContains(response,"Request updated successfully")
        self.assertEqual(response.status_code, 200)
        request = Request.objects.get(id=self.request1.id)
        self.assertEqual(request.availability, self.form_input['availability'])
        self.assertEqual(request.lessons, self.form_input['lessons'])
        self.assertEqual(request.days_between_lessons, self.form_input['days_between_lessons'])
        self.assertEqual(request.duration, self.form_input['duration'])
        self.assertEqual(request.info, self.form_input['info'])
        self.assertEqual(request.availability, self.form_input['availability'])

    def test_succesful_request_with_child(self):
        self.form_input['child'] = self.child.id
        before_count = Request.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Request.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('list_lessons')
        self.assertContains(response,"Request updated successfully")
        self.assertEqual(response.status_code, 200)
        request = Request.objects.get(id=self.request1.id)
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

    def test_view_does_not_allow_edits_to_request_that_does_not_belong_to_user(self):
        url = reverse('edit_request', kwargs={'id': self.request2.id })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, 'create_lesson_request.html')
        self.assertContains(response, 'Unauthorised: Request does not match current user')

    def test_edit_request_with_id_that_does_not_exist(self):
        url = reverse('edit_request', kwargs={'id': 10000 })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, 'create_lesson_request.html')
        self.assertContains(response, 'Request not found')

    def test_client_cannot_edit_fulfilled_request(self):
        self.request1.fulfilled = True
        self.request1.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, 'create_lesson_request.html')
        self.assertContains(response, 'Cannot edit a fulfilled request')

