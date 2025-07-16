from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from mailing.models import Mailing


class Command(BaseCommand):
    help = 'Создаёт группу "Менеджеры", назначает права и добавляет пользователей'

    def add_arguments(self, parser):
        # Добавляем опциональный аргумент --users для указания email
        parser.add_argument(
            '--users',
            nargs='+',
            help='Список username пользователей для добавления в группу',
        )

    def handle(self, *args, **options):
        # Создаём группу или получаем существующую
        group, created = Group.objects.get_or_create(name="Менеджеры")

        # Назначаем права на рассылки
        content_type = ContentType.objects.get_for_model(Mailing)
        permissions = Permission.objects.filter(content_type=content_type)
        group.permissions.set(permissions)

        # Добавляем пользователей (если указаны)
        if options['users']:
            users = User.objects.filter(email__in=options['users'])
            group.user_set.add(*users)
            self.stdout.write(
                self.style.SUCCESS(f'Добавлено пользователей: {users.count()}'))
        else:
            self.stdout.write(
                self.style.WARNING('Пользователи не указаны (используйте --users)'))
            self.stdout.write(
                self.style.SUCCESS('Группа "Менеджеры" готова! Права: рассылки'))
