from rest_framework import viewsets, generics, permissions
from rest_framework.permissions import IsAuthenticated
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from .permissions import IsModerator, IsOwner

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action == 'create':
            # Создавать могут только аутентифицированные, но не модераторы
            permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ['update', 'partial_update', 'retrieve', 'list']:
            # Просматривать и редактировать могут модераторы ИЛИ владельцы (на уровне объекта)
            permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action == 'destroy':
            # Удалять могут только владельцы (не модераторы)
            permission_classes = [IsAuthenticated, IsOwner]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'POST':

            return [IsAuthenticated(), ~IsModerator()]

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
            # Удалять могут только владельцы (не модераторы)
            return [IsAuthenticated(), IsOwner()]
        elif self.request.method in ['PUT', 'PATCH']:
            # Редактировать могут модераторы или владелец
            return [IsAuthenticated(), IsModerator() | IsOwner()]
        else:  # GET
            # Просматривать могут модераторы или владелец
            return [IsAuthenticated(), IsModerator() | IsOwner()]

    def get_queryset(self):
        # Для детального просмотра также фильтруем, чтобы соблюсти права на уровне queryset
        user = self.request.user
        if user.groups.filter(name='Moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)