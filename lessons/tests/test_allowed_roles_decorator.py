"""Tests of the allow roles decorator."""
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse
from lessons.models import User
from .helpers import LogInTester
from lessons.views import allowed_roles
from django.test import RequestFactory  

class AllowedRolesDecoratorTestCase(TestCase):
    """Tests of the log out view."""

    def setUp(self):
        self.url = reverse('log_out')
        self.student = User.objects.create_user('johndoe@example.com',
            first_name='John',
            last_name='Doe',
            password='Password123',
            role=User.STUDENT,
            is_active=True,
        )
        self.admin = User.objects.create_user('janedoe@example.com',
            first_name='Jane',
            last_name='Doe',
            password='Password123',
            role=User.ADMIN,
            is_active=True,
        )
        self.factory = RequestFactory()

    def test_user_is_logged_in_and_has_required_role(self):
        @allowed_roles([User.ADMIN])
        def exampleView(request):
            return HttpResponse("success")

        request = self.factory.get('/page')
        request.user = self.admin
        response = exampleView(request)
        self.assertEquals(response.content,b'success')
        
    def test_user_is_logged_in_and_does_not_have_required_role(self):
        @allowed_roles([User.ADMIN])
        def exampleView(request):
            return HttpResponse("success")

        request = self.factory.get('/page')
        request.user = self.student
        response = exampleView(request)
        self.assertEquals(response.content,b'403 Forbidden')

    def test_user_is_logged_in_and_no_roles_allowed(self):
        self.client.login(username='janedoe@example.com', password='Password123')

        @allowed_roles([])
        def exampleView(request):
            return HttpResponse("success")

        request = self.factory.get('/page')
        request.user = self.admin
        response = exampleView(request)
        self.assertEquals(response.content,b'403 Forbidden')