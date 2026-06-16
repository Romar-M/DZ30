from django.core.management.base import BaseCommand
from users.models import User, Payment
from lms.models import Course, Lesson

class Command(BaseCommand):
    help = 'Создаёт тестовые платежи'

    def handle(self, *args, **options):
        # Создаём пользователя, если его нет
        user, created = User.objects.get_or_create(
            email='test@test.com',
            defaults={'password': 'testpass123'}
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(f'Создан пользователь {user.email}')

        # Создаём курс и урок
        course, _ = Course.objects.get_or_create(
            title='Основы Python',
            description='Тестовый курс'
        )
        lesson, _ = Lesson.objects.get_or_create(
            title='Установка Python',
            course=course,
            defaults={
                'description': 'Установка Python на Windows',
                'video_link': 'https://example.com/video1'
            }
        )

        # Создаём платежи
        Payment.objects.create(user=user, course=course, amount=5000, method='transfer')
        Payment.objects.create(user=user, lesson=lesson, amount=1500, method='cash')
        self.stdout.write(self.style.SUCCESS('Платежи созданы'))