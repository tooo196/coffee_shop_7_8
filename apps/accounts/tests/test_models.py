from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class UserModelTest(TestCase):
    """Test the custom User model."""
    
    def test_create_user(self):
        """Test creating a regular user with required fields."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            phone='+1234567890'
        )
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.phone, '+1234567890')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIsNotNone(user.date_joined)
    
    def test_create_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='',
                password='testpass123',
                first_name='John',
                last_name='Doe'
            )
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        
        self.assertEqual(user.email, 'admin@example.com')
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_create_superuser_with_non_staff_raises_error(self):
        """Test that creating a superuser with is_staff=False raises a ValueError."""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123',
                is_staff=False
            )
    
    def test_create_superuser_with_non_superuser_raises_error(self):
        """Test that creating a superuser with is_superuser=False raises a ValueError."""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123',
                is_superuser=False
            )
    
    def test_user_str_representation(self):
        """Test the string representation of a user."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        expected_str = f"{user.email} ({user.get_full_name()})"
        self.assertEqual(str(user), expected_str)
    
    def test_user_get_full_name(self):
        """Test the get_full_name method."""
        user = User(
            email='test@example.com',
            first_name='John',
            last_name='Doe'
        )
        
        self.assertEqual(user.get_full_name(), 'John Doe')
    
    def test_user_get_short_name(self):
        """Test the get_short_name method."""
        user = User(
            email='test@example.com',
            first_name='John',
            last_name='Doe'
        )
        
        self.assertEqual(user.get_short_name(), 'John')
    
    def test_user_phone_validation(self):
        """Test phone number validation."""
        # Test valid phone number
        user = User(
            email='test@example.com',
            password='testpass123',
            phone='+1234567890'
        )
        user.full_clean()  # Should not raise ValidationError
        
        # Test invalid phone number (too short)
        user.phone = '123'
        with self.assertRaises(ValidationError):
            user.full_clean()
        
        # Test invalid phone number (contains letters)
        user.phone = '+123abc4567'
        with self.assertRaises(ValidationError):
            user.full_clean()
    
    def test_user_email_normalization(self):
        """Test that email is normalized during user creation."""
        email = 'test@EXAMPLE.COM'
        user = User.objects.create_user(
            email=email,
            password='testpass123'
        )
        
        self.assertEqual(user.email, email.lower())
    
    def test_user_email_uniqueness(self):
        """Test that email addresses are unique."""
        User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        with self.assertRaises(Exception):  # Should raise IntegrityError
            User.objects.create_user(
                email='test@example.com',
                password='anotherpass123'
            )
