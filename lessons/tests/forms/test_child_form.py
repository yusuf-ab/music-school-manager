from django import forms
from django.test import TestCase
from lessons.forms import ChildForm
from lessons.models import User

class ChildFormTestCase(TestCase):
    """Unit tests of the ChildForm"""
    fixtures = [
        'lessons/tests/fixtures/test_data.json'
    ]
    def setUp(self):
        self.form_input = {
            'first_name':'Jim',
            'last_name':'Doe'
        }

    def test_form_has_necessary_fields(self):
        form = ChildForm()
        self.assertIn('first_name', form.fields)
        self.assertTrue(isinstance(form.fields['first_name'], forms.CharField))
        self.assertIn('last_name', form.fields)
        self.assertTrue(isinstance(form.fields['last_name'], forms.CharField))

    def test_form_accepts_valid_input(self):
        form = ChildForm(data=self.form_input)
        form.instance.parent = User.objects.get(id=1)
        self.assertTrue(form.is_valid())

    def test_form_rejects_no_first_name(self):
        self.form_input['first_name'] = ''
        form = ChildForm(data=self.form_input)
        form.instance.parent = User.objects.get(id=1)
        self.assertFalse(form.is_valid())
    
    def test_form_rejects_no_last_name(self):
        self.form_input['last_name'] = ''
        form = ChildForm(data=self.form_input)
        form.instance.parent = User.objects.get(id=1)
        self.assertFalse(form.is_valid())

    def test_form_rejects_too_long_name(self):
        self.form_input['first_name'] = 'a'*51
        form = ChildForm(data=self.form_input)
        form.instance.parent = User.objects.get(id=1)
        self.assertFalse(form.is_valid())