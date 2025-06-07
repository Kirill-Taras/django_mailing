from django.db import models

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

