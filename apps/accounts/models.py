from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class UserManager(BaseUserManager):
    """Custom user model manager where email is the unique identifier."""
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser, TimeStampedModel):
    """Custom user model that uses email as the unique identifier."""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Role(models.TextChoices):
        GUEST = 'GUEST', _('Guest')
        CUSTOMER = 'CUSTOMER', _('Customer')
        ADMIN = 'ADMIN', _('Admin')
    
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        max_length=10, 
        choices=Role.choices, 
        default=Role.GUEST,
        verbose_name=_('role')
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('phone number'))
    address = models.TextField(blank=True, verbose_name=_('delivery address'))
    
    objects = UserManager()
    
    def __str__(self):
        return self.email
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser
    
    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER
    
    @property
    def is_guest(self):
        return self.role == self.Role.GUEST


class GuestSession(TimeStampedModel):
    """Model to track guest users and their cart."""
    session_key = models.CharField(max_length=40, unique=True, verbose_name=_('session key'))
    email = models.EmailField(blank=True, verbose_name=_('guest email'))
    
    def __str__(self):
        return f"Guest: {self.session_key}"
