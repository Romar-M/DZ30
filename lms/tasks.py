from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_course_update_notification(subscriber_emails, course_title):
    """
    Отправляет письма подписчикам об обновлении курса.
    """
    subject = f'Обновление курса "{course_title}"'
    message = f'Курс "{course_title}" был обновлён. Заходите и учитесь!'
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        subscriber_emails,
        fail_silently=False,
    )