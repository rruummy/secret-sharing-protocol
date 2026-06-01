from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages

from logs.utils import log_event
from .forms import CustomUserCreationForm, CustomAuthenticationForm


def home_view(request):
    """Головна сторінка сайту (/). Якщо авторизований — редирект на дашборд."""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    return render(request, 'home.html')


def register_view(request):
    """Реєстрація нового користувача."""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            log_event(user, "Реєстрація", f"Користувач {user.username} успішно зареєструвався.")
            messages.success(request, 'Реєстрація успішна! Тепер ви можете увійти.')
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Вхід у систему."""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
        
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                log_event(user, "Вхід у систему", f"Користувач {user.username} увійшов через веб-інтерфейс.")
                return redirect('accounts:dashboard')
    else:
        form = CustomAuthenticationForm()
        
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Вихід із системи."""
    if request.user.is_authenticated:
        log_event(request.user, "Вихід із системи", f"Користувач {request.user.username} вийшов із системи.")
        logout(request)
    return redirect('accounts:home')


@login_required
def dashboard_view(request):
    """Панель користувача (Dashboard)."""
    # Передаємо у шаблон останні секрети та логи цього користувача
    user_secrets = request.user.secrets.all().order_by('-created_at')[:5]
    user_logs = request.user.auditlog_set.all().order_by('-created_at')[:5]
    
    context = {
        'secrets': user_secrets,
        'logs': user_logs
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def change_password_view(request):
    """Зміна паролю користувача."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Оновлюємо сесію, щоб користувач не розлогінився після зміни паролю
            update_session_auth_hash(request, user)
            log_event(user, "Зміна паролю", "Користувач успішно змінив свій пароль.")
            messages.success(request, 'Ваш пароль було успішно оновлено!')
            return redirect('accounts:dashboard')
    else:
        form = PasswordChangeForm(request.user)
        
    return render(request, 'accounts/change_password.html', {'form': form})