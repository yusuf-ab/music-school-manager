from django import forms
from django.test import TestCase
from lessons.forms import TermForm
from lessons.models import User

class TermFormTestCase(TestCase):
    """Unit tests of the TermForm"""
    fixtures = [
        'lessons/tests/fixtures/test_data.json'
    ]
    def setUp(self):
        self.form_input = {
            "name":"Term 0",
            "start_date":"2020-1-1",
            "end_date":"2020-1-10"
        }
    def test_form_has_necessary_fields(self):
        form = TermForm()
        self.assertIn('name', form.fields)
        self.assertTrue(isinstance(form.fields['name'], forms.CharField))
        self.assertIn('start_date', form.fields)
        self.assertTrue(isinstance(form.fields['start_date'], forms.DateField))
        self.assertIn('end_date', form.fields)
        self.assertTrue(isinstance(form.fields['end_date'], forms.DateField))
        
    def test_form_accepts_valid_input(self):
        form = TermForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_name(self):
        self.form_input['name'] = ''
        form = TermForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_no_start_date(self):
        self.form_input['start_date'] = ' '
        form = TermForm(data=self.form_input)
        self.assertFalse(form.is_valid())
    
    def test_form_rejects_invalid_start_date(self):
        self.form_input['start_date'] = '2022/2022/2022'
        form = TermForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_no_end_date(self):
        self.form_input['end_date'] = ' '
        form = TermForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_end_date_before_start_date(self):
        self.form_input['start_date'] = '2020-1-1'
        self.form_input['end_date'] = '2019-1-1'
        form = TermForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_dates_that_overlap_with_existing_term(self):
        self.form_input['start_date'] = '2022-1-1'
        self.form_input['end_date'] = '2022-12-1'
        form = TermForm(data=self.form_input)
        self.assertFalse(form.is_valid())


    