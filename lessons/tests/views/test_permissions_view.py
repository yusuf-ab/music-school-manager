from django.test import TestCase
from django.urls import reverse
from lessons.models import User

class PermissionsViewTestCase(TestCase):
    """Tests of the permissions view."""

    fixtures = [
        'lessons/tests/fixtures/test_data.json',
    ]

    def setUp(self):
        self.user = User.objects.get(email='marty.major@example.org')
        self.user2 = User.objects.get(email='petra.pickles@example.org')
        self.user3 = User.objects.get(email='john.doe@example.org')
        self.url = reverse('permissions', kwargs={})
        self.client.login(username=self.user.email, password='Password123')

    def test_permissions_url(self):
        self.assertEqual(self.url,'/permissions/')
    
    def test_get_permissions(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'permissions.html')

    def test_change_role_of_user(self):
        data = {
            'id': self.user3.id,
            'role': User.TEACHER
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(User.objects.get(email=self.user3.email).role, User.TEACHER)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'permissions.html')

    def test_invalid_change_role_of_user(self):
        data = {
            'id': self.user3.id,
            'role': "invalid role"
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(User.objects.get(email=self.user3.email).role, User.STUDENT)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'permissions.html')

    def test_invalid_user_id(self):
        data = {
            'id': 100000,
            'role':  User.STUDENT
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'permissions.html')

    def test_cant_change_users_to_director(self):
        data = {
            'id': self.user3.id,
            'role': User.DIRECTOR
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(User.objects.get(email=self.user3.email).role, User.STUDENT)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'permissions.html')

    def test_page_displays_all_users(self):
        response = self.client.get(self.url)
        for user in User.objects.all():
            self.assertContains(response,f'user-{user.id}')