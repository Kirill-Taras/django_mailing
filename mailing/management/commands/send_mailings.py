from datetime import timezone

from django.core.management.base import BaseCommand
from mailing.models import Mailing
from mailing.services import send_mailing

class Command(BaseCommand):
    help = 'Отправляет все активные рассылки'

    def handle(self, *args, **options):
        now = timezone.now()
        mailings = Mailing.objects.filter(
            status__in=['created', 'started'],
            start_time__lte=now,
            end_time__gte=now
        )
        for mailing in mailings:
            send_mailing(mailing)
            self.stdout.write(f"Рассылка #{mailing.id} отправлена.")
        Mailing.objects.filter(
            status='started',
            end_time__lt=now).update(status='completed')