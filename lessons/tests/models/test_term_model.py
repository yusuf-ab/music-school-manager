from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import Term
from datetime import date, timedelta

class TermModelTestCase(TestCase):
    """Unit tests for the Term model."""

    fixtures = [
        'lessons/tests/fixtures/test_data.json'
    ]
    def setUp(self):
        self.term = Term.objects.get(name="Term one")
        self.second_term = Term.objects.get(name="Term two")

    def test_valid_term(self):
        self._assert_term_is_valid()

    def test_name_must_not_be_blank(self):
        self.term.name = ''
        self._assert_term_is_invalid()

    def test_start_date_must_not_be_blank(self):
        self.term.start_date = None
        self._assert_term_is_invalid()

    def test_end_date_must_not_be_blank(self):
        self.term.end_date = None
        self._assert_term_is_invalid()

    def test_name_need_not_be_unique(self):
        self.term.name = self.second_term.name
        self._assert_term_is_valid()

    def test_name_can_be_50_chars(self):
        self.term.name = "a"*50
        self._assert_term_is_valid()

    def test_name_cannot_be_larger_than_50_chars(self):
        self.term.name = "a"*51
        self._assert_term_is_invalid()

    def test_end_date_cannot_be_before_start_date(self):
        self.term.start_date = date(2022,2,1)
        self.term.end_date = date(2022,1,1)
        self._assert_term_is_invalid()

    def test_dates_cannot_overlap_another_term(self):
        self.term.end_date = self.second_term.start_date
        self._assert_term_is_invalid()

    def test_dates_can_end_before_another_term_starts(self):
        self.term.end_date = self.second_term.start_date - timedelta(1)
        self._assert_term_is_valid()

    def test_string_format(self):
        string = self.term.name + ' ' + self.term.start_date.strftime('%d/%m/%Y') + '-' + self.term.end_date.strftime('%d/%m/%Y')
        self.assertEqual(str(self.term),string)

    def test_current_and_next_term(self):
        Term.objects.all().delete()
        self.test_term1 = Term.objects.create(name="test term 1",start_date=date.today(),end_date=date.today()+timedelta(14))
        self.test_term2 = Term.objects.create(name="test term 2",start_date=date.today()+timedelta(30),end_date=date.today()+timedelta(47))
        self.assertEqual(Term.current_term(),self.test_term1)
        self.assertEqual(Term.next_term(),self.test_term2)

    def _assert_term_is_valid(self):
        try:
            self.term.full_clean()
        except (ValidationError):
            self.fail('Test term should be valid')

    def _assert_term_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.term.full_clean()
