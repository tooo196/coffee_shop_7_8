from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from django.core.exceptions import ValidationError

from ..forms import (
    UserRegistrationForm,
    UserEditForm,
    PasswordChangeForm,
    PasswordResetRequestForm,
    SetNewPasswordForm
)

User = get_user_model()

class UserRegistrationFormTest(TestCase):
    """Test the UserRegistrationForm."""
    
    def test_registration_form_valid_data(self):
        """Test the form with valid data."""
        form_data = {
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+1234567890',
            'agree_to_terms': True
        }
        
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_registration_form_missing_required_fields(self):
        """Test the form with missing required fields."""
        # Test missing email
        form_data = {
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('first_name', form.errors)
        self.assertIn('last_name', form.errors)
        self.assertIn('phone', form.errors)
    
    def test_registration_form_password_mismatch(self):
        """Test that mismatched passwords raise a validation error."""
        form_data = {
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'differentpass123',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+1234567890',
            'agree_to_terms': True
        }
        
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_registration_form_duplicate_email(self):
        """Test that duplicate emails are caught by the form."""
        # Create a user with the same email first
        User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Existing',
            last_name='User'
        )
        
        form_data = {
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+1234567890',
            'agree_to_terms': True
        }
        
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_registration_form_terms_not_accepted(self):
        """Test that terms must be accepted."""
        form_data = {
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+1234567890',
            'agree_to_terms': False
        }
        
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('agree_to_terms', form.errors)


class UserEditFormTest(TestCase):
    """Test the UserEditForm."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            phone='+1234567890'
        )
    
    def test_edit_form_valid_data(self):
        """Test the form with valid data."""
        form_data = {
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'User',
            'phone': '+9876543210'
        }
        
        form = UserEditForm(instance=self.user, data=form_data)
        self.assertTrue(form.is_valid())
        
        # Save the form and verify the user was updated
        user = form.save()
        self.assertEqual(user.email, 'updated@example.com')
        self.assertEqual(user.first_name, 'Updated')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.phone, '+9876543210')
    
    def test_edit_form_invalid_email(self):
        """Test the form with an invalid email."""
        form_data = {
            'email': 'invalid-email',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+1234567890'
        }
        
        form = UserEditForm(instance=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_edit_form_duplicate_email(self):
        """Test that duplicate emails are caught by the form."""
        # Create another user with a different email
        User.objects.create_user(
            email='another@example.com',
            password='testpass123',
            first_name='Another',
            last_name='User'
        )
        
        # Try to update the first user with the second user's email
        form_data = {
            'email': 'another@example.com',  # This email is already taken
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+1234567890'
        }
        
        form = UserEditForm(instance=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class PasswordChangeFormTest(TestCase):
    """Test the PasswordChangeForm."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='oldpassword123',
            first_name='John',
            last_name='Doe'
        )
    
    def test_password_change_form_valid_data(self):
        """Test the form with valid data."""
        form_data = {
            'old_password': 'oldpassword123',
            'new_password1': 'newpassword123',
            'new_password2': 'newpassword123'
        }
        
        form = PasswordChangeForm(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_password_change_form_wrong_old_password(self):
        """Test with incorrect old password."""
        form_data = {
            'old_password': 'wrongpassword',
            'new_password1': 'newpassword123',
            'new_password2': 'newpassword123'
        }
        
        form = PasswordChangeForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('old_password', form.errors)
    
    def test_password_change_form_password_mismatch(self):
        """Test with mismatched new passwords."""
        form_data = {
            'old_password': 'oldpassword123',
            'new_password1': 'newpassword123',
            'new_password2': 'differentpassword123'
        }
        
        form = PasswordChangeForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password2', form.errors)
    
    def test_password_change_form_weak_password(self):
        """Test with a weak password."""
        form_data = {
            'old_password': 'oldpassword123',
            'new_password1': '123',  # Too short
            'new_password2': '123'
        }
        
        form = PasswordChangeForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password2', form.errors)


class PasswordResetRequestFormTest(TestCase):
    """Test the PasswordResetRequestForm."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_reset_request_form_valid_email(self):
        """Test with a valid email that exists in the system."""
        form_data = {'email': 'test@example.com'}
        form = PasswordResetRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_reset_request_form_invalid_email(self):
        """Test with an invalid email format."""
        form_data = {'email': 'invalid-email'}
        form = PasswordResetRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_reset_request_form_nonexistent_email(self):
        """Test with an email that doesn't exist in the system."""
        form_data = {'email': 'nonexistent@example.com'}
        form = PasswordResetRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class SetNewPasswordFormTest(TestCase):
    """Test the SetNewPasswordForm."""
    
    def test_set_password_form_valid_data(self):
        """Test with valid password data."""
        form_data = {
            'new_password1': 'newpassword123',
            'new_password2': 'newpassword123'
        }
        
        form = SetNewPasswordForm(user=None, data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_set_password_form_mismatched_passwords(self):
        """Test with mismatched passwords."""
        form_data = {
            'new_password1': 'newpassword123',
            'new_password2': 'differentpassword123'
        }
        
        form = SetNewPasswordForm(user=None, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password2', form.errors)
    
    def test_set_password_form_weak_password(self):
        """Test with a weak password."""
        form_data = {
            'new_password1': '123',  # Too short
            'new_password2': '123'
        }
        
        form = SetNewPasswordForm(user=None, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password2', form.errors)
