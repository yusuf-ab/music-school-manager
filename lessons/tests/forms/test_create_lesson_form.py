from django import forms
from django.test import TestCase
from lessons.forms import CreateLessonRequestForm
from lessons.models import User, Child

class CreateLessonRequestFormTestCase(TestCase):
    """Unit tests of the CreateLessonRequestForm"""
    fixtures = [
        'lessons/tests/fixtures/test_data.json'
    ]
    def setUp(self):
        self.client = User.objects.get(email="john.doe@example.org")
        self.form_input = {
            "availability":"Any time",
            "lessons":"1",
            "days_between_lessons":"7",
            "duration":"60",
            "info":"Piano",
            "child":"1"
            }

    def test_form_has_necessary_fields(self):
        form = CreateLessonRequestForm(user=self.client)
        form.instance.client = self.client
        self.assertIn('availability', form.fields)
        self.assertTrue(isinstance(form.fields['availability'], forms.CharField))
        self.assertIn('lessons', form.fields)
        self.assertTrue(isinstance(form.fields['lessons'], forms.IntegerField))
        self.assertIn('days_between_lessons', form.fields)
        self.assertTrue(isinstance(form.fields['days_between_lessons'], forms.TypedChoiceField))
        self.assertIn('duration', form.fields)
        self.assertTrue(isinstance(form.fields['duration'], forms.TypedChoiceField))
        self.assertIn('info', form.fields)
        self.assertTrue(isinstance(form.fields['info'], forms.CharField))
        self.assertIn('child', form.fields)
        self.assertTrue(isinstance(form.fields['child'], forms.ModelChoiceField))

    def test_form_has_all_clients_children(self):
        form = CreateLessonRequestForm(user=self.client)
        form.instance.client = self.client
        self.assertEqual(len(form.fields['child'].queryset),2)

    def test_form_accepts_valid_input(self):
        form = CreateLessonRequestForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertTrue(form.is_valid())

    def test_form_rejects_no_availability(self):
        self.form_input['availability'] = ''
        form = CreateLessonRequestForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertFalse(form.is_valid())

    def test_form_rejects_no_lessons(self):
        self.form_input['lessons'] = ''
        form = CreateLessonRequestForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertFalse(form.is_valid())

    def test_form_negative_lessons(self):
        self.form_input['lessons'] = '-10'
        form = CreateLessonRequestForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertFalse(form.is_valid())

    def test_form_rejects_0_lessons(self):
        self.form_input['lessons'] = '0'
        form = CreateLessonRequestForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertFalse(form.is_valid())

    def test_form_rejects_no_days_between_lessons(self):
        self.form_input['days_between_lessons'] = ''
        form = CreateLessonRequestForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertFalse(form.is_valid())

    def test_form_rejects_invalid_between_lessons(self):
        self.form_input['days_between_lessons'] = '10'
        form = CreateLessonRequestForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertFalse(form.is_valid())
    
    def test_form_rejects_no_duration(self):
        self.form_input['duration'] = ''
        form = CreateLessonRequestForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertFalse(form.is_valid())

    def test_form_rejects_no_info(self):
        self.form_input['info'] = ''
        form = CreateLessonRequestForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertFalse(form.is_valid())

    def test_form_rejects_info_too_long(self):
        self.form_input['info'] = 'example' * 4000
        form = CreateLessonRequestForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertFalse(form.is_valid())

    def test_form_rejects_availability_too_long(self):
        self.form_input['availability'] = 'example' * 4000
        form = CreateLessonRequestForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertFalse(form.is_valid())

    def test_form_rejects_invalid_child(self):
        self.form_input['child'] = '10000'
        form = CreateLessonRequestForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertFalse(form.is_valid())

    def test_form_works_without_child(self): # Means the parent is the student
        self.form_input['child'] = ''
        form = CreateLessonRequestForm(user=self.client, data=self.form_input)
        form.instance.client = self.client
        self.assertTrue(form.is_valid())