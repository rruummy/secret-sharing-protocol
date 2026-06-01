from .models import AuditLog

def log_event(user, action: str, details: str = None):
    """
    Утиліта для швидкого запису дій користувача в журнал аудиту.
    """
    AuditLog.objects.create(
        user=user if user and user.is_authenticated else None,
        action=action,
        details=details
    )