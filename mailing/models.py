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
