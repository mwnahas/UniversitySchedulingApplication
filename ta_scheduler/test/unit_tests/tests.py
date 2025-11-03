from django.contrib.auth import get_user_model
from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.urls import reverse
from ta_scheduler.models import Section


#calling this on database tests
class SectionModelTest(TestCase):
    def test_something_about_sections(self):
        # your test code here
        self.assertTrue(True)



# Create your tests here.

User = get_user_model()

class UserModelTests(TestCase):
    def test_user_creation(self):                   #Creates a TA user using Django’s create_user() method.
        user = User.objects.create_user(            #Then checks if email is saved correctly, passwprd is hashed using check_password and role is stored as ta
            username='testuser',
            email='test@example.com',
            full_name='Test User',
            role='ta',
            password='securepass123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('securepass123'))
        self.assertEqual(user.role, 'ta')

    def test_superuser_creation(self):
        admin = User.objects.create_superuser(          #this one creates an admin user  using create_superuser().
            username='adminuser',                       #Then checks that is_superuser is set to true and that role field is "admin"
            email='admin@example.com',
            full_name='Admin',
            role='admin',
            password='adminpass123'
        )
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.role, 'admin')



class SuccessLogin(TestCase):
    def setUp(self):
        #creation of a test user
        self.username = 'testuser'
        self.password = 'test123'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def testLoginGood(self):
        #self.client.login will return true or false if the user was logged in or not
        success = self.client.login(username=self.username, password=self.password)
        self.assertTrue(success)

    def testLoginUserAuth(self):
        #uses urls.py to see if it can reverse from its page back to the login
        response = self.client.post(reverse('login'), {'username': self.username, 'password': self.password},follow = True)
        #This will check if a redirect occured AKA redirecting to the home page
        self.assertEqual(response.status_code, 200)

        #Grabs the users info from the response
        user = response.context['user']
        #checks if the user is logged in and wasnt just redirected
        self.assertTrue(user.is_authenticated, "user should be authenticated")

    def testLoginRedirect(self):
        response = self.client.post(reverse('login'), {'username': self.username, 'password': self.password},)
        self.assertEqual(response.status_code, 302)


class FailedLogin(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'test123'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def testWrongUsername(self):
        login = self.client.login(username= 'wrongUsername', password=self.password)
        self.assertFalse(login)

    def testWrongPassword(self):
        login = self.client.login(username= self.username, password= "wrongPassword")
        self.assertFalse(login)

    def testNoRedirect(self):
        response = self.client.post(reverse('login'), {'username': "wrong", 'password': self.password})
        self.assertNotEqual(response.status_code, 302)

        user = response.context['user']
        self.assertFalse(user.is_authenticated)

    def testCapsUsername(self):
        login = self.client.login(username= 'TESTUSER', password= self.password)
        self.assertFalse(login)

    def testCapsPassword(self):
        login = self.client.login(username= self.username, password= "TEST123")
        self.assertFalse(login)

    def testNoLogin(self):
        #Tell the client to go to home without logging in
        response = self.client.get(reverse('home'),follow = True)
        #this checks to see if the 404 error screen pops up
        self.assertEqual(response.status_code, 404)

class SuccessLogout(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'password'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def testSuccessLogout(self):
        #allow the client to login with proper credentials
        login = self.client.login(username= self.username, password= self.password)
        #assure that the login did properly work (this is tested above but is tested again to be sure for the specfic test)
        self.assertTrue(login, "login failed")

        #this logs the user out and follows the url to the django logout view
        response = self.client.post(reverse('logout'), follow = True)

        #assure the user is no longer authenticated
        self.assertFalse(response.wsgi_request.user.is_authenticated, "User should NOT be authenticated")
        #Checks if the session is done and cleared
        self.assertNotIn('_auth_user_id', self.client.session)

    def testRedirectAfterLogout(self):
        login = self.client.login(username= self.username, password= self.password)
        self.assertTrue(login, "login failed")
        response = self.client.post(reverse('logout'))
        #"/" is the login page because it is the root
        self.assertRedirects(response, '/', msg_prefix='Did not redirect after logout')
