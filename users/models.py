from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from lms.models import Course, Lesson
from django.conf import settings

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # email и пароль обязательны по умолчанию

    def __str__(self):
        return self.email


class Payment(models.Model):
    CASH = 'cash'
    TRANSFER = 'transfer'
    METHOD_CHOICES = [
        (CASH, 'Наличные'),
        (TRANSFER, 'Перевод на счёт'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата оплаты')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, verbose_name='Способ оплаты')

    def __str__(self):
        return f'{self.user.email} – {self.amount} ({self.date})'

class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subscriptions')

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f'{self.user.email} подписан на {self.course.title}'