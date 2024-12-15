from django.test import TestCase
from django.urls import reverse
from lessons.models import User, Child
from lessons.forms import ChildForm

class ChildrenViewTest(TestCase):

    fixtures = ['lessons/tests/fixtures/test_data.json']

    def setUp(self):
        self.form_input = {
            'first_name':'Jim',
            'last_name':'Doe',
        }
        self.url = reverse('children')
        self.client.login(username='john.doe@example.org', password='Password123')

    def test_children_view_url(self):
        self.assertEqual(self.url,'/children/')

    def test_get_children(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'children.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ChildForm))
        self.assertFalse(form.is_bound)

    def test_unsuccesful_child_addition(self):
        self.form_input['first_name'] = 'x'*51
        before_count = Child.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Child.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'children.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ChildForm))
        self.assertFalse(form.is_bound)

    def test_successful_child_addition(self):
        before_count = Child.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Child.objects.count()
        self.assertEqual(after_count, before_count+1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'children.html')
        child = Child.objects.get(first_name='Jim')
        self.assertEqual(child.first_name, 'Jim')
        self.assertEqual(child.last_name, 'Doe')
        self.assertEqual(child.parent.email, 'john.doe@example.org')
