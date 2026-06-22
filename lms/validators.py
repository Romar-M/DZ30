from django.core.exceptions import ValidationError

def validate_youtube_link(value):
    if not value:
        return
    if 'youtube.com' not in value:
        raise ValidationError('Ссылка должна вести на youtube.com')