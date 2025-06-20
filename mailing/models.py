from django.db import models

"""Модель получателя рассылки"""
class Client(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email")
    full_name = models.CharField(max_length=50, verbose_name="ФИО", null=True, blank=True)
    comment = models.TextField(max_length=150, verbose_name="Комментарий", blank=True, null=True)

    class Meta:
        ordering = ['full_name']
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return f'{self.full_name} <{self.email}>'


"""Модель сообщения"""
class Message(models.Model):
    subject = models.CharField(max_length=150, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Тело письма")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ['-created_at']

    def __str__(self):
        return self.subject

"""Модель рассылки"""
class Mailing(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('completed', 'Завершена'),
    ]

    start_time = models.DateTimeField(verbose_name="Дата и время начала")
    end_time = models.DateTimeField(verbose_name="Дата и время окончания")
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='created',
        verbose_name="Статус"
    )
    message = models.ForeignKey(
        'Message',
        on_delete=models.CASCADE,
        verbose_name="Сообщение"
    )
    clients = models.ManyToManyField(
        'Client',
        verbose_name="Получатели"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ['-created_at']

    def __str__(self):
        return f"Рассылка #{self.id} ({self.get_status_display()})"

"""Модель попытки рассылки"""
class MailingAttempt(models.Model):
    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('failed', 'Не успешно'),
    ]

    mailing = models.ForeignKey(
        'Mailing',
        on_delete=models.CASCADE,
        verbose_name="Рассылка",
        related_name='attempts'
    )
    client = models.ForeignKey(
        'Client',
        on_delete=models.CASCADE,
        verbose_name="Клиент",
        null=True,  # На случай, если клиент был удалён
    )
    attempt_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время попытки"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        verbose_name="Статус"
    )
    server_response = models.TextField(
        verbose_name="Ответ сервера",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"
        ordering = ['-attempt_time']

    def __str__(self):
        return f"Попытка #{self.id} ({self.get_status_display()})"
