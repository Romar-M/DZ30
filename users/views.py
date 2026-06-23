from rest_framework import viewsets, generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import User, Payment, Subscription
from .serializers import UserFullSerializer, UserLimitedSerializer, PaymentSerializer
from .filters import PaymentFilter
from lms.models import Course
from config.services import create_stripe_product, create_stripe_price, create_stripe_checkout_session, retrieve_stripe_session


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
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
            return [permissions.AllowAny()]
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


class PaymentCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        course_id = request.data.get('course_id')
        amount = request.data.get('amount')

        if not course_id or not amount:
            return Response({'error': 'course_id и amount обязательны'}, status=status.HTTP_400_BAD_REQUEST)

        course = get_object_or_404(Course, pk=course_id)

        # Создаём платёж в нашей БД
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=amount,
            method='transfer',
        )

        # Stripe: создаём продукт, цену и сессию
        product_name = f"Course: {course.title}"
        product_id = create_stripe_product(product_name, description=course.description)
        price_id = create_stripe_price(product_id, int(amount * 100))  # сумма в копейках

        success_url = 'http://127.0.0.1:8000/api/payment/success/'
        cancel_url = 'http://127.0.0.1:8000/api/payment/cancel/'
        session_id, payment_url = create_stripe_checkout_session(price_id, success_url, cancel_url)

        # Обновляем платёж данными из Stripe
        payment.stripe_product_id = product_id
        payment.stripe_price_id = price_id
        payment.stripe_session_id = session_id
        payment.payment_url = payment_url
        payment.save()

        return Response({
            'id': payment.id,
            'payment_url': payment_url,
            'session_id': session_id,
            'message': 'Ссылка для оплаты создана'
        }, status=status.HTTP_201_CREATED)


class PaymentStatusAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)

        if not payment.stripe_session_id:
            return Response({'error': 'Сессия Stripe не найдена'}, status=status.HTTP_404_NOT_FOUND)

        session_info = retrieve_stripe_session(payment.stripe_session_id)
        payment.status = session_info['payment_status']
        payment.save()

        return Response({
            'payment_id': payment.id,
            'status': payment.status,
            'session_info': session_info,
        })


def payment_success(request):
    return HttpResponse("Оплата прошла успешно! Можете закрыть страницу.")


def payment_cancel(request):
    return HttpResponse("Оплата отменена.")