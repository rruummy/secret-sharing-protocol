from django.db import models
from django.conf import settings

class Secret(models.Model):
    title = models.CharField(max_length=255)
    # Зберігаємо зашифрований текст. Оскільки Fernet повертає bytes, 
    # у БД зручно зберігати як TextField (текст у форматі base64)
    encrypted_secret = models.TextField()
    shares_count = models.IntegerField()  # n
    threshold = models.IntegerField()     # k
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='secrets'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Share(models.Model):
    secret = models.ForeignKey(
        Secret, 
        on_delete=models.CASCADE, 
        related_name='shares'
    )
    # Кому призначена частка (у ТЗ вказано participant_id)
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='assigned_shares'
    )
    x = models.IntegerField()
    y = models.TextField()  # Координата Y може бути дуже великим числом, краще зберегти як текст
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Share ({self.x}) for {self.secret.title}"