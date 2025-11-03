from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from ta_scheduler.models import PublicProfile
from ta_scheduler.models import PrivateProfile, PublicProfile
from ta_scheduler.views import PublicProfileView

User = get_user_model()

class PrivateProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')

    def test_valid_phone_number_saves(self):
        profile = PrivateProfile(
            user=self.user,
            phone_number='1234567890'
        )
        try:
            profile.save()
        except ValueError:
            self.fail("Valid phone number raised ValueError unexpectedly!")

    def test_invalid_phone_number_raises_error(self):
        profile = PrivateProfile(
            user=self.user,
            phone_number='123-456-7890'  # contains non-digit characters
        )
        with self.assertRaises(ValueError):
            profile.save()

    def test_blank_phone_number_saves(self):
        profile = PrivateProfile(
            user=self.user,
            phone_number=''  # allowed because blank=True
        )
        try:
            profile.save()
        except ValueError:
            self.fail("Blank phone number raised ValueError unexpectedly!")



class PublicProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='testuser',
            password='password123',
            full_name='Test User',
            role='ta'
        )
        self.profile = PublicProfile.objects.create(
            user=self.user,
            email='test@example.com',
            office_location='Room 101',
            office_hours='MWF 10–12',
            bio='This is a test bio.'
        )

    def test_public_profile_view_success(self):
        response = self.client.get(reverse('public_profile', kwargs={'username': 'testuser'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public_profile.html')
        self.assertContains(response, 'This is a test bio.')
        self.assertEqual(response.context['profile'], self.profile)

    def test_public_profile_view_user_not_found(self):
        response = self.client.get(reverse('public_profile', kwargs={'username': 'nonexistent'}))
        self.assertEqual(response.status_code, 404)

    def test_public_profile_view_profile_not_found(self):
        user2 = User.objects.create_user(username='nopublicprofile', password='password123')
        response = self.client.get(reverse('public_profile', kwargs={'username': 'nopublicprofile'}))
        self.assertEqual(response.status_code, 404)




class PrivateProfileViewTest(TestCase):
    def setUp(self):
        # Create a user
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123',
            full_name='Test User',
            role='ta'
        )

        # Create a non-owner user
        self.other_user = get_user_model().objects.create(
            username='otheruser',
            password='password456',
            full_name='Other User',
            role='ta'
        )

        # Create an admin user
        self.admin_user = get_user_model().objects.create_user(
            username='adminuser',
            password='adminpass',
            full_name='Admin User',
            role='admin'
        )

        # Create a private profile for the user with sensitive info
        self.private_profile = PrivateProfile.objects.create(
            user=self.user,
            home_address='123 Main St',
            phone_number='1234567890',
            emergency_contact='test, 987-654-3210'
        )
        self.url = reverse('private_profile', kwargs={'username': 'testuser'})

    def test_private_profile_view_success(self):
        # Log in the user
        self.client.login(username='testuser', password='password123')

        # Generate the URL for the user's private profile
        response = self.client.get(reverse('private_profile', kwargs={'username': 'testuser'}))

        # Check if the profile is rendered correctly
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'private_profile.html')

        # Check if sensitive information is visible
        self.assertContains(response, '123 Main St')
        self.assertContains(response, '1234567890')
        self.assertContains(response, 'test, 987-654-3210')

        # Ensure that the correct private profile object is passed to the context
        self.assertEqual(response.context['profile'], self.private_profile)

    def test_anonymous_user_cannot_view_profile(self):
        url = reverse('private_profile', kwargs={'username': 'testuser'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # PermissionDenied → 403

    def test_only_owner_or_admin_can_view_private_profile(self):
        # Owner access should be allowed
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        # Admin access should be allowed
    def test_admin_can_view_private_profile(self):
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)  # Admin access should be allowed
        self.client.logout()

        # Other user's access should be denied
    def test_other_user_cannot_view_private_profile(self):
        self.client.login(username='otheruser', password='password456')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)  # PermissionDenied should return 403
        self.client.logout()

        # Unauthenticated access should be denied
    def test_unauthenticated_user_cannot_view_private_profile(self):
         response = self.client.get(self.url)
         self.assertEqual(response.status_code, 403)  # PermissionDenied should return 403
