"""Unit tests for the User model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import User

class UserModelTestCase(TestCase):
    """Unit tests for the User model."""

    fixtures = [
        'lessons/tests/fixtures/test_data.json'
    ]
    def setUp(self):
        self.user = User.objects.get(email="john.doe@example.org")

    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_first_name_must_not_be_blank(self):
        self.user.first_name = ''
        self._assert_user_is_invalid()

    def test_first_name_need_not_be_unique(self):
        second_user = User.objects.get(email="petra.pickles@example.org")
        self.user.first_name = second_user.first_name
        self._assert_user_is_valid()

    def test_first_name_may_contain_50_characters(self):
        self.user.first_name = 'x' * 50
        self._assert_user_is_valid()

    def test_first_name_must_not_contain_more_than_50_characters(self):
        self.user.first_name = 'x' * 51
        self._assert_user_is_invalid()

    def test_last_name_must_not_be_blank(self):
        self.user.last_name = ''
        self._assert_user_is_invalid()

    def test_last_name_need_not_be_unique(self):
        second_user = User.objects.get(email="petra.pickles@example.org")
        self.user.last_name = second_user.last_name
        self._assert_user_is_valid()

    def test_last_name_may_contain_50_characters(self):
        self.user.last_name = 'x' * 50
        self._assert_user_is_valid()

    def test_last_name_must_not_contain_more_than_50_characters(self):
        self.user.last_name = 'x' * 51
        self._assert_user_is_invalid()

    def test_email_must_not_be_blank(self):
        self.user.email = ''
        self._assert_user_is_invalid()

    def test_email_must_be_unique(self):
        second_user = User.objects.get(email="petra.pickles@example.org")
        self.user.email = second_user.email
        self._assert_user_is_invalid()

    def test_email_must_contain_username(self):
        self.user.email = '@example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_at_symbol(self):
        self.user.email = 'johndoe.example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain_name(self):
        self.user.email = 'johndoe@.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain(self):
        self.user.email = 'johndoe@example'
        self._assert_user_is_invalid()

    def test_email_must_not_contain_more_than_one_at(self):
        self.user.email = 'johndoe@@example.org'
        self._assert_user_is_invalid()

    def test_role_is_valid(self):
        self.user.role = 'CHEF'
        self._assert_user_is_invalid()

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError):
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()
