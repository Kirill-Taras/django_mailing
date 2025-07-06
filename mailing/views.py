from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DetailView,
    DeleteView,
)
from django.shortcuts import render, get_object_or_404, redirect
from mailing.models import Client, Message, Mailing, MailingAttempt
from mailing.services import send_mailing
from django.contrib import messages


def home_view(request):
    """Главная страница"""
    total_mailings = Mailing.objects.count()
    active_mailings = Mailing.objects.filter(status="started").count()
    unique_clients = Client.objects.distinct().count()

    context = {
        "total_mailings": total_mailings,
        "active_mailings": active_mailings,
        "unique_clients": unique_clients,
    }
    return render(request, "home.html", context)


#Страницы для работы с клиентами
class ClientListView(ListView):
    model = Client
    template_name = "mailing/client_list.html"
    context_object_name = "clients"


class ClientCreateView(CreateView):
    model = Client
    fields = ["email", "full_name", "comment"]
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("client_list")


class ClientUpdateView(UpdateView):
    model = Client
    fields = ["email", "full_name", "comment"]
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("client_list")


class ClientDeleteView(DeleteView):
    model = Client
    template_name = "mailing/client_confirm_delete.html"
    success_url = reverse_lazy("client_list")


class ClientDetailView(DetailView):
    model = Client
    template_name = "mailing/client_detail.html"
    context_object_name = "client"


#Страницы для работы с сообщениями
class MessageListView(ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"


class MessageCreateView(CreateView):
    model = Message
    fields = ["subject", "body"]
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")


class MessageUpdateView(UpdateView):
    model = Message
    fields = ["subject", "body"]
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")


class MessageDeleteView(DeleteView):
    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")


class MessageDetailView(DetailView):
    model = Message
    template_name = "mailing/message_detail.html"
    context_object_name = "message"


#Страницы для работы с рассылками
class MailingListView(ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"


class MailingCreateView(CreateView):
    model = Mailing
    fields = ["start_time", "end_time", "status", "message", "clients"]
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")


class MailingUpdateView(UpdateView):
    model = Mailing
    fields = ["start_time", "end_time", "status", "message", "clients"]
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")


class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")


class MailingDetailView(DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"
    context_object_name = "mailing"


def send_mailing_view(request, pk):
    """Функция для отправки рассылки"""
    mailing = get_object_or_404(Mailing, pk=pk)
    if mailing.status in ["created", "started"]:
        for client in mailing.clients.all():
            try:
                result = send_mailing(mailing, client)
                MailingAttempt.objects.create(
                    mailing=mailing,
                    client=client,
                    status='success',
                    server_response=result
                )
            except Exception as e:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    client=client,
                    status='failed',
                    server_response=str(e)
                )
        messages.success(request, "Рассылка обработана! Результаты в логах.")
    return redirect("mailing:mailing_detail", pk=pk)


class StatisticsView(LoginRequiredMixin, ListView):
    """Страница для статистики"""
    model = MailingAttempt
    template_name = 'mailing/statistics.html'
    context_object_name = 'stats'

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailings = self.get_queryset()

        context.update({
            'total_mailings': mailings.count(),
            'active_mailings': mailings.filter(status='started').count(),
            'success_count': MailingAttempt.objects.filter(
                mailing__in=mailings,
                status='success'
            ).count(),
            'failed_count': MailingAttempt.objects.filter(
                mailing__in=mailings,
                status='failed'
            ).count(),
            'recent_attempts': MailingAttempt.objects.filter(
                mailing__in=mailings
            ).order_by('-attempt_time')[:10]
        })
        return context