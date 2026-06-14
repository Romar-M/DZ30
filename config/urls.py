from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from lms.views import CourseViewSet
from users.views import UserViewSet   # если выбрали ViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'users', UserViewSet)   # для доп. задания

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    # Уроки – вручную, без роутера
    path('api/lessons/', include('lms.urls')),
]