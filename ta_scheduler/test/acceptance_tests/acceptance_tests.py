from ta_scheduler.models import User
from django.test import TestCase
from django.urls import reverse

class NavigationAcceptanceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test123')
        self.newUser = User.objects.create_user(username='ADMIN', password='ADMIN', role = 'admin')

    #As a user I should be able to login and successfully access the homepage
    def test_homepage_loads_successfully(self):
        success = self.client.login(username='test', password='test123')
        self.assertTrue(success)
        response = self.client.get(reverse('home'), follow = True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome back, Panther.")
        self.client.logout()

    def test_homepage_to_courses_back_to_homepage_loads_successfully(self):
        success = self.client.login(username='test', password='test123')
        self.assertTrue(success)
        response = self.client.get(reverse('home'), follow = True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome back, Panther.")
        response = self.client.get(reverse('courses'), follow = True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Courses")
        response = self.client.get(reverse('home'), follow = True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome back, Panther.")

    def test_logout_in_courses(self):
        success = self.client.login(username='test', password='test123')
        self.assertTrue(success)
        response = self.client.get(reverse('home'), follow = True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome back, Panther.")
        response = self.client.get(reverse('courses'), follow = True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Courses")
        self.client.logout()
        response = self.client.get(reverse('home'), follow = True)
        self.assertEqual(response.status_code, 404)

    def test_logout_in_homepage(self):
        success = self.client.login(username='test', password='test123')
        self.assertTrue(success)
        response = self.client.get(reverse('home'), follow = True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome back, Panther.")
        self.client.logout()
        response = self.client.get(reverse('home'), follow = True)
        self.assertEqual(response.status_code, 404)