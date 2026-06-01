from django import apps
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """Форма для реєстрації з підтримкою CustomUser."""
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")


class CustomAuthenticationForm(AuthenticationForm):
    """Стандартна форма входу (можна кастомізувати за потреби)."""
    pass