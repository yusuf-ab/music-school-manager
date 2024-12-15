from django import forms
from django.test import TestCase
from lessons.forms import UserForm
from lessons.models import User

class UserFormTestCase(TestCase):
    """Unit tests of the User Form"""
    fixtures = [
        'lessons/tests/fixtures/test_data.json'
    ]
    def setUp(self):
        self.form_input = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test.user@example.com',
            'role': 'STUDENT',
            'new_password': 'Password123',
            'password_confirmation': 'Password123'
        }

    def test_form_has_necessary_fields(self):
        form = UserForm()
        self.assertIn('first_name', form.fields)
        self.assertTrue(isinstance(form.fields['first_name'], forms.CharField))
        self.assertIn('last_name', form.fields)
        self.assertTrue(isinstance(form.fields['last_name'], forms.CharField))
        self.assertIn('email', form.fields)
        self.assertTrue(isinstance(form.fields['email'], forms.EmailField))
        self.assertIn('role', form.fields)
        self.assertTrue(isinstance(form.fields['role'], forms.TypedChoiceField))
        self.assertIn('new_password', form.fields)
        self.assertTrue(isinstance(form.fields['new_password'], forms.CharField))
        self.assertIn('password_confirmation', form.fields)
        self.assertTrue(isinstance(form.fields['password_confirmation'], forms.CharField))

    def test_form_accepts_valid_input_when_creating_user(self):
        form = UserForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_no_first_name(self):
        self.form_input['first_name'] = ''
        form = UserForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_no_last_name(self):
        self.form_input['last_name'] = ''
        form = UserForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_no_email(self):
        self.form_input['email'] = ''
        form = UserForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_no_role(self):
        self.form_input['role'] = ''
        form = UserForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_invalid_role(self):
        self.form_input['role'] = 'DOCTOR'
        form = UserForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_no_passwords(self):
        self.form_input.pop('new_password')
        self.form_input.pop('password_confirmation')
        form = UserForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_no_confirmation(self):
        self.form_input.pop('password_confirmation')
        form = UserForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_invalid_confirmation(self):
        self.form_input['password_confirmation'] = 'wrongconfirmation'
        form = UserForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_can_edit_user(self):
        self.form_input['email'] = "john.doe@example.org"
        form = UserForm(data=self.form_input, instance=User.objects.get(email="john.doe@example.org"))
        self.assertTrue(form.is_valid())
        form.normal_save()
        user = User.objects.get(email="john.doe@example.org")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")

    def test_form_can_edit_user_without_setting_new_password(self):
        self.form_input.pop('new_password')
        self.form_input.pop('password_confirmation')
        self.form_input['email'] = "john.doe@example.org"
        form = UserForm(data=self.form_input, instance=User.objects.get(email="john.doe@example.org"))
        self.assertTrue(form.is_valid())
        form.normal_save()
        user = User.objects.get(email="john.doe@example.org")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")

    def test_form_requires_confirmation_when_new_password_is_set_when_editing_user(self):
        self.form_input.pop('new_password')
        self.form_input['email'] = "john.doe@example.org"
        form = UserForm(data=self.form_input, instance=User.objects.get(email="john.doe@example.org"))
        self.assertFalse(form.is_valid())
