"""Unit tests of the user select form."""
from django import forms
from django.test import TestCase
from lessons.forms import UserSelectForm
from lessons.models import User

class UserSelectFormTestCase(TestCase):
    """Unit tests of the user select form."""
    fixtures = [
        'lessons/tests/fixtures/test_data.json'
    ]

    def setUp(self):

        self.form_input = {}
        self.student = User.objects.get(email='john.doe@example.org')
        self.student2 = User.objects.get(email='ryan.fuller@example.org')
        self.admin = User.objects.get(email='petra.pickles@example.org')

    def test_form_has_necessary_fields(self):
        form = UserSelectForm()
        self.assertIn('client', form.fields)
        self.assertTrue(isinstance(form.fields['client'], forms.ModelChoiceField))

    def test_form_rejects_invalid_input_string(self):
        self.form_input['client'] = 'badinput'
        form = UserSelectForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_invalid_input_choosing_admin(self):
        self.form_input['client'] = self.admin.id # admin
        form = UserSelectForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_accepts_valid_input_choosing_student(self):
        self.form_input['client'] = self.student.id #student
        form = UserSelectForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_only_contains_students(self):
        form = UserSelectForm(data=self.form_input)
        self.assertEqual(set(form.fields['client'].queryset),set(User.objects.filter(role=User.STUDENT)))
