from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from users.models import User, Subscription
from .models import Course, Lesson
from rest_framework_simplejwt.tokens import AccessToken

class BaseTestCase(APITestCase):
    def setUp(self):
        # Пользователи
        self.user = User.objects.create_user(email='user@test.com', password='test123')
        self.moderator = User.objects.create_user(email='mod@test.com', password='test123')
        from django.contrib.auth.models import Group
        mod_group, _ = Group.objects.get_or_create(name='Moderators')
        self.moderator.groups.add(mod_group)

        # Курс
        self.course = Course.objects.create(title='Тестовый курс', description='Описание', owner=self.user)
        # Урок
        self.lesson = Lesson.objects.create(
            title='Тестовый урок',
            description='Описание урока',
            video_link='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            course=self.course,
            owner=self.user
        )

        # URL-ы
        self.lesson_list_url = reverse('lesson-list-create')
        self.lesson_detail_url = reverse('lesson-detail', args=[self.lesson.pk])
        self.subscribe_url = reverse('subscribe')

    def get_token(self, user):
        token = AccessToken.for_user(user)
        return f'Bearer {token}'

    def auth(self, user):
        self.client.credentials(HTTP_AUTHORIZATION=self.get_token(user))


class LessonCRUDTests(BaseTestCase):
    def test_create_lesson_authenticated(self):
        self.auth(self.user)
        data = {
            'title': 'Новый урок',
            'description': 'Описание',
            'video_link': 'https://www.youtube.com/watch?v=abc123',
            'course': self.course.pk
        }
        response = self.client.post(self.lesson_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        self.assertEqual(Lesson.objects.last().owner, self.user)

    def test_create_lesson_moderator_forbidden(self):
        self.auth(self.moderator)
        data = {'title': 'Модератор', 'description': '...', 'video_link': 'https://www.youtube.com/watch?v=abc', 'course': self.course.pk}
        response = self.client.post(self.lesson_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_lesson_invalid_link(self):
        self.auth(self.user)
        data = {'title': 'Плохой', 'description': '...', 'video_link': 'https://rutube.ru/video', 'course': self.course.pk}
        response = self.client.post(self.lesson_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('youtube.com', str(response.data))

    def test_update_lesson_owner(self):
        self.auth(self.user)
        data = {'title': 'Обновленный урок', 'video_link': 'https://www.youtube.com/watch?v=updated'}
        response = self.client.patch(self.lesson_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Обновленный урок')

    def test_update_lesson_not_owner(self):
        other_user = User.objects.create_user(email='other@test.com', password='test123')
        self.auth(other_user)
        data = {'title': 'Чужой урок'}
        response = self.client.patch(self.lesson_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_owner(self):
        self.auth(self.user)
        response = self.client.delete(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_delete_lesson_moderator_forbidden(self):
        self.auth(self.moderator)
        response = self.client.delete(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SubscriptionTests(BaseTestCase):
    def test_subscribe(self):
        self.auth(self.user)
        data = {'course_id': self.course.pk}
        response = self.client.post(self.subscribe_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('подписка добавлена', response.data['message'])
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_unsubscribe(self):
        Subscription.objects.create(user=self.user, course=self.course)
        self.auth(self.user)
        data = {'course_id': self.course.pk}
        response = self.client.post(self.subscribe_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('подписка удалена', response.data['message'])
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_subscribe_unauthenticated(self):
        data = {'course_id': self.course.pk}
        response = self.client.post(self.subscribe_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)