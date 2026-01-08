from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from .models import User, GuestSession
from .forms import UserRegistrationForm, UserEditForm, GuestRegistrationForm


def register(request):
    """Handle user registration."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.role = User.Role.CUSTOMER
            user.save()
            
            # Авторизуем пользователя после регистрации
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно! Добро пожаловать в наш кофейный магазин!')
            return redirect('products:product_list')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def register_guest(request):
    """Handle guest user registration."""
    if request.method == 'POST':
        form = GuestRegistrationForm(request.POST)
        if form.is_valid():
            guest_session = GuestSession.objects.create(
                session_key=request.session.session_key,
                email=form.cleaned_data['email']
            )
            # Сохраняем ID гостевой сессии в сессии
            request.session['guest_session_id'] = str(guest_session.id)
            messages.success(request, 'Добро пожаловать! Теперь вы можете делать покупки как гость.')
            return redirect('products:product_list')
    else:
        form = GuestRegistrationForm()
    
    return render(request, 'accounts/guest_register.html', {'form': form})


@login_required
def profile(request):
    """Display user profile."""
    return render(request, 'accounts/profile.html')


@login_required
def edit_profile(request):
    """Handle profile editing."""
    if request.method == 'POST':
        form = UserEditForm(instance=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('accounts:profile')
    else:
        form = UserEditForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})


def convert_guest_to_user(request):
    """Convert guest user to registered user."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.role = User.Role.CUSTOMER
            user.save()
            
            # Авторизуем пользователя
            login(request, user)
            
            # Переносим корзину гостя в аккаунт пользователя (реализуйте в приложении корзины)
            # migrate_cart(request, user)
            
            # Удаляем гостевую сессию
            if 'guest_session_id' in request.session:
                try:
                    guest_session = GuestSession.objects.get(id=request.session['guest_session_id'])
                    guest_session.delete()
                except GuestSession.DoesNotExist:
                    pass
                del request.session['guest_session_id']
            
            messages.success(request, 'Your account has been created successfully!')
            return redirect('products:product_list')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/convert_guest.html', {'form': form})


class UserDashboardView(TemplateView):
    """User dashboard view."""
    template_name = 'accounts/dashboard.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем дополнительные данные в контекст
        return context
