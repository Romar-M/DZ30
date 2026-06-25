from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from .permissions import IsNotModerator, IsModeratorOrOwner, IsOwner
from django.utils import timezone
from datetime import timedelta
from .tasks import send_course_update_notification
from users.models import Subscription

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsNotModerator()]
        elif self.action in ['update', 'partial_update', 'retrieve', 'list']:
            return [IsAuthenticated(), IsModeratorOrOwner()]
        elif self.action == 'destroy':
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.save()
        if not instance.last_notification_sent or \
                (timezone.now() - instance.last_notification_sent) > timedelta(hours=4):
            subscribers = Subscription.objects.filter(course=instance).select_related('user')
            emails = [sub.user.email for sub in subscribers if sub.user.email]
            if emails:
                send_course_update_notification.delay(emails, instance.title)
                instance.last_notification_sent = timezone.now()
                instance.save(update_fields=['last_notification_sent'])


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsNotModerator()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated(), IsModeratorOrOwner()]

    def perform_update(self, serializer):
        lesson = serializer.save()
        course = lesson.course
        if not course.last_notification_sent or \
                (timezone.now() - course.last_notification_sent) > timedelta(hours=4):
            subscribers = Subscription.objects.filter(course=course).select_related('user')
            emails = [sub.user.email for sub in subscribers if sub.user.email]
            if emails:
                send_course_update_notification.delay(emails, course.title)
                course.last_notification_sent = timezone.now()
                course.save(update_fields=['last_notification_sent'])