from django.test import TestCase
from lessons.models import User
from lessons.models import CustomUserManager


class CustomUserManagerTestCase(TestCase):
    def setUp(self):
        self.user_manager = CustomUserManager()
        self.user_manager.model = User
        self.email = 'user@example.org'
        self.password='Password123'

    def test_create_valid_user(self):
        user = self.user_manager.create_user(self.email, self.password)
        self.assertEqual(user.email, self.email)
        self.assertTrue(user.check_password(self.password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_with_no_password(self):
        with self.assertRaises(ValueError):
            self.user_manager.create_user(None, self.password)

    def test_create_valid_superuser(self):
        user = self.user_manager.create_superuser(self.email, self.password)
        self.assertEqual(user.email, self.email)
        self.assertTrue(user.check_password(self.password))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_superuser_with_no_email(self):
        with self.assertRaises(ValueError):
            self.user_manager.create_superuser(None, self.password)

    def test_create_superuser_with_staff_false(self):
        with self.assertRaises(ValueError):
            self.user_manager.create_superuser(self.email, self.password, is_staff=False)

    def test_create_superuser_with_superuser_false(self):
        with self.assertRaises(ValueError):
            self.user_manager.create_superuser(self.email, self.password, is_superuser=False)