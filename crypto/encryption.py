import os
from cryptography.fernet import Fernet
from django.core.exceptions import ImproperlyConfigured

# Отримуємо ключ із середовища .env
_key = os.getenv('ENCRYPTION_KEY')

if not _key:
    raise ImproperlyConfigured("Ключ ENCRYPTION_KEY не знайдено в змінних оточення (.env).")

# Ініціалізуємо об'єкт Fernet
try:
    _cipher = Fernet(_key.encode() if isinstance(_key, str) else _key)
except Exception as e:
    raise ImproperlyConfigured(f"Невалідний ENCRYPTION_KEY для Fernet: {e}")


def encrypt_data(data: str) -> str:
    """
    Приймає звичайний рядок тексту, шифрує його за допомогою Fernet
    і повертає зашифрований рядок у форматі Base64.
    """
    if not data:
        return ""
    # Конвертуємо рядок у байти -> шифруємо -> декодуємо назад у строку для збереження в TextField
    encrypted_bytes = _cipher.encrypt(data.encode('utf-8'))
    return encrypted_bytes.decode('utf-8')


def decrypt_data(encrypted_data: str) -> str:
    """
    Приймає зашифрований рядок Base64, розшифровує його
    і повертає оригінальний текст.
    """
    if not encrypted_data:
        return ""
    decrypted_bytes = _cipher.decrypt(encrypted_data.encode('utf-8'))
    return decrypted_bytes.decode('utf-8')