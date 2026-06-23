from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from lms.views import CourseViewSet
from users.views import (
    UserViewSet,
    PaymentViewSet,
    SubscriptionAPIView,
    PaymentCreateAPIView,
    PaymentStatusAPIView,
    payment_success,
    payment_cancel,
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'users', UserViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/lessons/', include('lms.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/subscribe/', SubscriptionAPIView.as_view(), name='subscribe'),
    path('api/payment/create/', PaymentCreateAPIView.as_view(), name='payment-create'),
    path('api/payment/<int:payment_id>/status/', PaymentStatusAPIView.as_view(), name='payment-status'),
    path('api/payment/success/', payment_success, name='payment-success'),
    path('api/payment/cancel/', payment_cancel, name='payment-cancel'),
    # Swagger / ReDoc
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)