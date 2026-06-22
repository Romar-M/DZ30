from rest_framework import viewsets, permissions, status
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Payment, Subscription
from .serializers import UserFullSerializer, UserLimitedSerializer, PaymentSerializer
from .filters import PaymentFilter
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from lms.models import Course

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    # Базовый сериализатор, будет переопределяться в get_serializer_class
    serializer_class = UserFullSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return UserLimitedSerializer
        if self.action == 'retrieve':
            if self.request.user == self.get_object():
                return UserFullSerializer
            return UserLimitedSerializer
        return UserFullSerializer

    def get_permissions(self):
        if self.action == 'create':
            # Регистрация доступна всем
            return [permissions.AllowAny()]
        # Все остальные действия требуют аутентификации
        return [permissions.IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance != request.user:
            return Response(
                {"detail": "Вы не можете редактировать чужой профиль."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance != request.user:
            return Response(
                {"detail": "Вы не можете редактировать чужой профиль."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Только администратор или сам пользователь может удалить
        if not request.user.is_staff and instance != request.user:
            return Response(
                {"detail": "Удаление запрещено."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['date']
    ordering = ['-date']

class SubscriptionAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')
        if not course_id:
            return Response({'error': 'course_id обязателен'}, status=status.HTTP_400_BAD_REQUEST)

        course = get_object_or_404(Course, pk=course_id)
        subscription = Subscription.objects.filter(user=user, course=course)

        if subscription.exists():
            subscription.delete()
            message = 'подписка удалена'
        else:
            Subscription.objects.create(user=user, course=course)
            message = 'подписка добавлена'

        return Response({'message': message})