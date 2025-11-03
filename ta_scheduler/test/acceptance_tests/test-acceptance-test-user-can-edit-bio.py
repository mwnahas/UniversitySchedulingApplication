from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from ta_scheduler.models import PublicProfile

User = get_user_model()

class UserBioEditTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123',
            full_name='Test User',
            role='ta'
        )
        PublicProfile.objects.create(user=self.user, bio='Old bio')

    def test_user_can_edit_bio(self):
        login = self.client.login(username='testuser', password='testpass123')
        self.assertTrue(login)

        url = reverse('user-edit', kwargs={'pk': self.user.pk})

        new_bio = 'This is my updated bio'
        post_data = {
            'full_name': self.user.full_name,
            'email': self.user.email,
            'role': self.user.role,
            'password': '',  # No password change


            'office_location': 'New Office',
            'office_hours': '9am - 5pm',
            'bio': new_bio,
        }

        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)

        self.user.public_profile.first().refresh_from_db()
        self.assertEqual(self.user.public_profile.first().bio, new_bio)