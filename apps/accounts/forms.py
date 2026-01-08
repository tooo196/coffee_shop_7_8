from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _

from .models import User


class UserRegistrationForm(UserCreationForm):
    """Form for user registration."""
    email = forms.EmailField(
        label=_('Email'),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control'})
    )
    first_name = forms.CharField(
        label=_('First name'),
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label=_('Last name'),
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label=_('Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
        help_text=_(
            'Your password must contain at least 8 characters, can\'t be too similar to your other personal information, can\'t be a commonly used password, and can\'t be entirely numeric.'
        ),
    )
    password2 = forms.CharField(
        label=_('Password confirmation'),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
        strip=False,
        help_text=_('Enter the same password as before, for verification.'),
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')
        field_classes = {'email': forms.EmailField}


class UserEditForm(UserChangeForm):
    """Форма для редактирования профиля пользователя."""
    password = None  # Удаляем поле пароля из формы
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'address')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class GuestRegistrationForm(forms.Form):
    """Form for guest user registration."""
    email = forms.EmailField(
        label=_('Email (optional)'),
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your email to receive order updates')
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('A user with this email already exists.'))
        return email


class UserAddressForm(forms.ModelForm):
    """Form for user address."""
    class Meta:
        model = User
        fields = ('address',)
        widgets = {
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
