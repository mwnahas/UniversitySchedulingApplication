
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from ta_scheduler.models import PublicProfile

User = get_user_model()

class UserBioEditTests(TestCase):
    def setUp(self):
        # Create a user and login
        self.user = User.objects.create_user(
            username='testuser',
            password='password123',
            email='test@example.com',
            role='user'
        )
        # Create associated public profile
        self.public_profile = PublicProfile.objects.create(user=self.user, bio="Old bio")

        self.client.login(username='testuser', password='password123')

    def test_edit_public_bio(self):
        # URL for the view that edits the public profile bio
        url = reverse('edit_public_profile')  # Adjust to your actual URL name

        # Data to update the bio
        new_bio = "This is my updated bio."
        response = self.client.post(url, {'bio': new_bio})

        # Check for redirect after successful update
        self.assertEqual(response.status_code, 302)

        # Refresh from DB and check bio updated
        self.public_profile.refresh_from_db()
        self.assertEqual(self.public_profile.bio, new_bio)
