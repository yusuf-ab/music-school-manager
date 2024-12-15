from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import User, Child

class ChildModelTestCase(TestCase):
    """Unit tests for the Child model."""

    fixtures = [
        'lessons/tests/fixtures/test_data.json'
    ]
    def setUp(self):
        self.user = User.objects.get(email="john.doe@example.org")
        self.second_user = User.objects.get(email="ryan.fuller@example.org")
        self.child = Child.objects.get(first_name="Alice",last_name="Doe")

    def test_valid_child(self):
        self._assert_child_is_valid()

    def test_first_name_must_not_be_blank(self):
        self.child.first_name = ''
        self._assert_child_is_invalid()

    def test_last_name_must_not_be_blank(self):
        self.child.last_name = ''
        self._assert_child_is_invalid()

    def test_parent_must_not_be_none(self):
        self.child.parent = None
        self._assert_child_is_invalid()

    def test_first_name_and_last_name_cannot_be_same_for_same_parent(self):
        second_child = Child.objects.get(first_name="Bob",last_name="Doe")
        self.child.first_name = second_child.first_name
        self._assert_child_is_invalid()

    def test_first_name_and_last_name_can_be_same_for_different_parent(self):
        second_child = Child.objects.get(first_name="Bob",last_name="Doe")
        self.child.first_name = second_child.first_name
        self.child.parent = self.second_user
        self._assert_child_is_valid()

    def test_first_name_and_cannot_be_larger_than_50_chars(self):
        self.child.first_name= "a"*51
        self._assert_child_is_invalid()

    def test_first_name_and_can_be_50_chars(self):
        self.child.first_name= "a"*50
        self._assert_child_is_valid()

    def test_last_name_and_cannot_be_larger_than_50_chars(self):
        self.child.last_name= "a"*51
        self._assert_child_is_invalid()

    def test_last_name_and_can_be_50_chars(self):
        self.child.last_name= "a"*50
        self._assert_child_is_valid()

    def _assert_child_is_valid(self):
        try:
            self.child.full_clean()
        except (ValidationError):
            self.fail('Test child should be valid')

    def _assert_child_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.child.full_clean()
