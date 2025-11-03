from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from ta_scheduler.models import PublicProfile, PrivateProfile

class UserCreateViewTest(TestCase):
    def setUp(self):
        # Create admin user who has permission to access AdminRequiredMixin views
        self.admin_user = get_user_model().objects.create_superuser(
            username='admin@example.com',  # Set username to email as done in your form
            email='admin@example.com',
            password='adminpass',
            full_name='Admin User',
            role='admin'
        )

        self.client.login(username='admin@example.com', password='adminpass')

        # URL for the user creation view
        self.create_url = reverse('user-create')

    def test_user_creation_creates_profiles(self):
        user_data = {
            'full_name': 'Test User',
            'email': 'testuser@example.com',
            'password': 'strongpassword123',
            'role': 'ta',
        }

        # Post the data to create a new user
        response = self.client.post(self.create_url, data=user_data)

        # Check redirect to success_url
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user-list'))

        # Get the created user
        User = get_user_model()
        self.assertTrue(User.objects.filter(email='testuser@example.com').exists())
        user = User.objects.get(email='testuser@example.com')

        # Verify username is set to email
        self.assertEqual(user.username, 'testuser@example.com')

        self.assertEqual(user.full_name, 'Test User')
        self.assertEqual(user.role, 'ta')

        # Check if profiles were created
        self.assertTrue(PublicProfile.objects.filter(user=user).exists())
        self.assertTrue(PrivateProfile.objects.filter(user=user).exists())

        # Check profile content
        public_profile = PublicProfile.objects.get(user=user)
        private_profile = PrivateProfile.objects.get(user=user)

        # Verify public profile
        self.assertEqual(public_profile.email, 'testuser@example.com')
        self.assertEqual(public_profile.bio, "") #bio is empty
        self.assertEqual(public_profile.office_location, '')
        self.assertEqual(public_profile.office_hours, '')

        # Verify private profile
        self.assertEqual(private_profile.home_address, '')
        self.assertEqual(private_profile.phone_number, '')
        self.assertEqual(private_profile.emergency_contact, '')

    def test_view_requires_admin(self):
        # Create a non-admin user
        regular_user = get_user_model().objects.create_user(
            username='regular@example.com',
            email='regular@example.com',
            password='userpass',
            full_name='Regular User',
            role='ta'
        )

        # Log out admin and log in as regular user
        self.client.logout()
        self.client.login(username='regular@example.com', password='userpass')

        response = self.client.get(self.create_url)

        # Should redirect to login or permission denied
        self.assertNotEqual(response.status_code, 200)

        # Try to create a user
        user_data = {
            'full_name': 'New User',
            'email': 'newuser@example.com',
            'password': 'password123',
            'role': 'ta',
        }
        response = self.client.post(self.create_url, data=user_data)

        # Should not be able to create
        self.assertNotEqual(response.status_code, 302)
        self.assertFalse(get_user_model().objects.filter(email='newuser@example.com').exists())