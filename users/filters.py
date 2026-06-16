import django_filters
from .models import Payment

class PaymentFilter(django_filters.FilterSet):
    course = django_filters.NumberFilter(field_name='course__id')
    lesson = django_filters.NumberFilter(field_name='lesson__id')
    method = django_filters.ChoiceFilter(choices=Payment.METHOD_CHOICES)

    class Meta:
        model = Payment
        fields = ['course', 'lesson', 'method']