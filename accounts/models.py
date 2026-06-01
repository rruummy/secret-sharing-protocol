from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Додаткове поле, якого немає в стандартному User, але є в ТЗ
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username