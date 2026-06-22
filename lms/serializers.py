from rest_framework import serializers
from .models import Course, Lesson
from .validators import validate_youtube_link

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ['owner']
        extra_kwargs = {
            'video_link': {'validators': [validate_youtube_link]}
        }

class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['owner']

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from users.models import Subscription  # Импорт избегает цикла
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False