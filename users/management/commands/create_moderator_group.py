from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'Создаёт группу Moderators'

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='Moderators')
        if created:
            self.stdout.write(self.style.SUCCESS('Группа Moderators создана'))
        else:
            self.stdout.write('Группа Moderators уже существует')