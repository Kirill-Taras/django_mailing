from django.core.management.base import BaseCommand
from mailing.models import Mailing
from mailing.services import send_mailing

class Command(BaseCommand):
    help = 'Отправляет все активные рассылки'

    def handle(self, *args, **options):
        mailings = Mailing.objects.filter(status__in=['created', 'started'])
        for mailing in mailings:
            send_mailing(mailing)
            self.stdout.write(f"Рассылка #{mailing.id} отправлена.")