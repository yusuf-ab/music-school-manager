from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import User, Child, Request

class RequestModelTestCase(TestCase):
    """Unit tests for the Request model."""

    fixtures = [
        'lessons/tests/fixtures/test_data.json'
    ]
    def setUp(self):
        self.user = User.objects.get(email="john.doe@example.org")
        self.child = Child.objects.get(first_name="Alice",last_name="Doe")
        self.request = Request.objects.create(
            client=self.user,
            availability="Any time",
            lessons="1",
            days_between_lessons="7",
            duration="60",
            info="Piano",
            child=self.child
        )

    def test_valid_request(self):
        self._assert_request_is_valid()

    def test_availability_must_not_be_blank(self):
        self.request.availability = None
        self._assert_request_is_invalid()

    def test_availability_cannot_be_empty(self):
        self.request.availability = ""
        self._assert_request_is_invalid()

    def test_availability_cannot_be_too_long(self):
        self.request.availability = "a"*1001
        self._assert_request_is_invalid()

    def test_info_cannot_be_empty(self):
        self.request.info = ""
        self._assert_request_is_invalid()

    def test_info_cannot_be_too_long(self):
        self.request.info = "a"*1001
        self._assert_request_is_invalid()

    def test_lessons_must_not_be_blank(self):
        self.request.lessons = None
        self._assert_request_is_invalid()

    def test_lessons_cannot_be_negative(self):
        self.request.lessons = -1
        self._assert_request_is_invalid()

    def test_lessons_cannot_be_zero(self):
        self.request.lessons = 0
        self._assert_request_is_invalid()

    def test_days_between_lessons_must_not_be_blank(self):
        self.request.days_between_lessons = None
        self._assert_request_is_invalid()

    def test_duration_must_not_be_blank(self):
        self.request.duration = None
        self._assert_request_is_invalid()

    def test_duration_cannot_be_negative(self):
        self.request.duration = -1
        self._assert_request_is_invalid()

    def test_duration_cannot_be_zero(self):
        self.request.duration = 0
        self._assert_request_is_invalid()

    def test_info_must_not_be_blank(self):
        self.request.info = None
        self._assert_request_is_invalid()

    def test_child_can_be_blank(self):
        self.request.child = None
        self._assert_request_is_valid()

    def test_child_must_belong_to_client(self):
        self.child.parent = User.objects.get(email="ryan.fuller@example.org")
        self.child.save()
        self._assert_request_is_invalid()

    def _assert_request_is_valid(self):
        try:
            self.request.full_clean()
        except (ValidationError):
            self.fail('Test request should be valid')

    def _assert_request_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.request.full_clean()
