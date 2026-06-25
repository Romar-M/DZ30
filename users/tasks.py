from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task
def deactivate_inactive_users():
    """
    Блокирует пользователей, не заходивших более 30 дней.
    """
    threshold = timezone.now() - timedelta(days=30)
    users = User.objects.filter(is_active=True, last_login__lt=threshold)
    count = users.update(is_active=False)
    return f'Deactivated {count} users'