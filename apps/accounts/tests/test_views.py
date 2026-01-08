from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core import mail

User = get_user_model()

class UserRegistrationViewTest(TestCase):
    """Test the user registration view."""
    
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('accounts:register')
        self.valid_data = {
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+1234567890'
        }
    
    def test_register_view_get(self):
        """Test GET request to register view."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
    
    def test_register_view_post_valid_data(self):
        """Test POST request to register view with valid data."""
        response = self.client.post(self.register_url, self.valid_data)
        
        # Should redirect to login page on success
        self.assertRedirects(response, reverse('accounts:login'))
        
        # Check that a new user was created
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
        
        # Check that the user is not active until email confirmation
        user = User.objects.get(email='test@example.com')
        self.assertFalse(user.is_active)
        
        # Check that an activation email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Activate your account', mail.outbox[0].subject)
    
    def test_register_view_post_invalid_data(self):
        """Test POST request to register view with invalid data."""
        # Test with missing required field (email)
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = ''
        
        response = self.client.post(self.register_url, invalid_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
        self.assertContains(response, 'This field is required.')
        
        # No user should be created
        self.assertFalse(User.objects.filter(email='').exists())
    
    def test_register_view_duplicate_email(self):
        """Test registering with an email that already exists."""
        # Create a user with the same email first
        User.objects.create_user(
            email='test@example.com',
            password='existingpass123',
            first_name='Existing',
            last_name='User'
        )
        
        response = self.client.post(self.register_url, self.valid_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
        self.assertContains(response, 'A user with that email already exists.')


class UserLoginViewTest(TestCase):
    """Test the user login view."""
    
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('accounts:login')
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            is_active=True
        )
    
    def test_login_view_get(self):
        """Test GET request to login view."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
    
    def test_login_view_post_valid_credentials(self):
        """Test POST request to login view with valid credentials."""
        response = self.client.post(self.login_url, {
            'username': 'test@example.com',
            'password': 'testpass123'
        })
        
        # Should redirect to home page on success
        self.assertRedirects(response, reverse('home'))
        
        # User should be authenticated
        self.assertTrue('_auth_user_id' in self.client.session)
    
    def test_login_view_post_invalid_credentials(self):
        """Test POST request to login view with invalid credentials."""
        response = self.client.post(self.login_url, {
            'username': 'test@example.com',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('Please enter a correct email and password.', str(messages[0]))
        
        # User should not be authenticated
        self.assertFalse('_auth_user_id' in self.client.session)
    
    def test_login_view_inactive_user(self):
        """Test login attempt with an inactive user account."""
        self.user.is_active = False
        self.user.save()
        
        response = self.client.post(self.login_url, {
            'username': 'test@example.com',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('This account is inactive.', str(messages[0]))
        
        # User should not be authenticated
        self.assertFalse('_auth_user_id' in self.client.session)


class UserLogoutViewTest(TestCase):
    """Test the user logout view."""
    
    def setUp(self):
        self.client = Client()
        self.logout_url = reverse('accounts:logout')
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(email='test@example.com', password='testpass123')
    
    def test_logout_view(self):
        """Test that a user can log out."""
        # User should be logged in initially
        self.assertTrue('_auth_user_id' in self.client.session)
        
        response = self.client.get(self.logout_url)
        
        # Should redirect to home page
        self.assertRedirects(response, reverse('home'))
        
        # User should be logged out
        self.assertFalse('_auth_user_id' in self.client.session)


class UserProfileViewTest(TestCase):
    """Test the user profile view."""
    
    def setUp(self):
        self.client = Client()
        self.profile_url = reverse('accounts:profile')
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            phone='+1234567890'
        )
        self.client.login(email='test@example.com', password='testpass123')
    
    def test_profile_view_requires_login(self):
        """Test that the profile view requires authentication."""
        self.client.logout()
        response = self.client.get(self.profile_url)
        
        # Should redirect to login page
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={self.profile_url}")
    
    def test_profile_view_get(self):
        """Test GET request to profile view."""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        self.assertEqual(response.context['user'], self.user)
    
    def test_profile_view_post_valid_data(self):
        """Test POST request to update profile with valid data."""
        updated_data = {
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updated@example.com',
            'phone': '+9876543210'
        }
        
        response = self.client.post(self.profile_url, updated_data)
        
        # Should redirect to profile page on success
        self.assertRedirects(response, self.profile_url)
        
        # User data should be updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertEqual(self.user.phone, '+9876543210')
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('Your profile has been updated.', str(messages[0]))
    
    def test_profile_view_post_invalid_data(self):
        """Test POST request with invalid data."""
        invalid_data = {
            'email': 'invalid-email',  # Invalid email format
            'phone': '123'  # Invalid phone number format
        }
        
        response = self.client.post(self.profile_url, invalid_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        
        # Form should have errors
        self.assertTrue(response.context['form'].errors)
        
        # User data should not be updated
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.email, 'invalid-email')
        self.assertNotEqual(self.user.phone, '123')
