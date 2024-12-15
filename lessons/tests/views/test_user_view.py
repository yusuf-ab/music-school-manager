from django.test import TestCase
from django.urls import reverse
from lessons.models import User
from lessons.forms import UserForm

class UserViewTestCase(TestCase):
    """Tests of the user view."""

    fixtures = [
        'lessons/tests/fixtures/test_data.json',
    ]

    def setUp(self):
        self.user = User.objects.get(email='john.doe@example.org')
        self.director = User.objects.get(email='marty.major@example.org')
        self.url = reverse('user', kwargs={'id': self.user.id})
        self.url2 = reverse('create_user')
        self.client.login(email=self.director.email, password='Password123')

    def test_user_urls(self):
        self.assertEqual(self.url,f'/user/{self.user.id}/')
        self.assertEqual(self.url2,f'/user/create/')
    
    def test_get_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertFalse(form.is_bound)

    def test_get_user_create(self):
        response = self.client.get(self.url2)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertFalse(form.is_bound)

    def test_get_user_fails_with_invalid_id(self):
        self.url = reverse('user', kwargs={'id': 10000})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,'User not found')

    def test_successful_edit_user(self):
        before_count = User.objects.count()
        self.form_input = {
            "first_name":"John","last_name": "Doe","email":"john.doe@example.org","role": "ADMIN"
        }
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        response_url = reverse('permissions')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'permissions.html')
        self.assertEqual(User.objects.get(email='john.doe@example.org').role, User.ADMIN)
        after_count = User.objects.count()
        self.assertEqual(before_count,after_count)

    def test_unsuccessful_edit_user(self):
        before_count = User.objects.count()
        self.form_input = {
            "first_name":"John"*500,"last_name": "Doe","email":"john.doe@example.org","role": "ADMIN"
        }
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertNotEqual(User.objects.get(email='john.doe@example.org').role, User.ADMIN)
        after_count = User.objects.count()
        self.assertEqual(before_count,after_count)

    def test_successful_create_user(self):
        before_count = User.objects.count()
        self.form_input = {
            "first_name":"John2","last_name": "Doe2","email":"john.doe2@example.org","role": "ADMIN","new_password": "Password123","password_confirmation": "Password123"
        }
        response = self.client.post(self.url2, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        response_url = reverse('permissions')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'permissions.html')
        self.assertEqual(User.objects.get(email='john.doe2@example.org').role, User.ADMIN)
        after_count = User.objects.count()
        self.assertEqual(before_count+1,after_count)

    def test_unsuccessful_create_user(self):
        before_count = User.objects.count()
        self.form_input = {
            "first_name":"John","last_name": "Doe","email":"john.doe@example.org","role": "ADMIN","new_password": "Password123","password_confirmation": "Password124" # different password
        }
        response = self.client.post(self.url2, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        after_count = User.objects.count()
        self.assertEqual(before_count,after_count)


        
