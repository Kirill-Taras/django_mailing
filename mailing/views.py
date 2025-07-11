from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views import View
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DetailView,
    DeleteView,
)
from django.shortcuts import render, get_object_or_404, redirect

from mailing.mixins import OwnerRequiredMixin
from mailing.models import Client, Message, Mailing, MailingAttempt
from mailing.services import send_mailing
from django.contrib import messages

from users.models import User


@cache_page(60 * 15)
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


# Страницы для работы с клиентами
@cache_page(60 * 15)
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "mailing/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        cache_key = f"clients_{self.request.user.id}"
        queryset = cache.get(cache_key)

        if not queryset:
            if self.request.user.has_perm("mailing.can_view_all_clients"):
                queryset = Client.objects.all()
            else:
                queryset = Client.objects.filter(owner=self.request.user)
            cache.set(cache_key, queryset, 60 * 15)
        return queryset


class ClientCreateView(OwnerRequiredMixin, LoginRequiredMixin, CreateView):
    model = Client
    fields = ["email", "full_name", "comment"]
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(OwnerRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Client
    fields = ["email", "full_name", "comment"]
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("client_list")


class ClientDeleteView(OwnerRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Client
    template_name = "mailing/client_confirm_delete.html"
    success_url = reverse_lazy("client_list")


class ClientDetailView(OwnerRequiredMixin, LoginRequiredMixin, DetailView):
    model = Client
    template_name = "mailing/client_detail.html"
    context_object_name = "client"


# Страницы для работы с сообщениями
@cache_page(60 * 15)
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ["subject", "body"]
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    fields = ["subject", "body"]
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "mailing/message_detail.html"
    context_object_name = "message"


# Страницы для работы с рассылками
@cache_page(60 * 15)
class MailingListView(OwnerRequiredMixin, LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        if self.request.user.has_perm("mailing.can_view_all_mailings"):
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    fields = ["start_time", "end_time", "status", "message", "clients"]
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(OwnerRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Mailing
    fields = ["start_time", "end_time", "status", "message", "clients"]
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")


class MailingDeleteView(OwnerRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")


class MailingDetailView(OwnerRequiredMixin, LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"
    context_object_name = "mailing"


@login_required
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
                    status="success",
                    server_response=result,
                )
            except Exception as e:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    client=client,
                    status="failed",
                    server_response=str(e),
                )
        messages.success(request, "Рассылка обработана! Результаты в логах.")
    return redirect("mailing:mailing_detail", pk=pk)


class StatisticsView(LoginRequiredMixin, ListView):
    """Страница для статистики"""

    model = MailingAttempt
    template_name = "mailing/statistics.html"
    context_object_name = "stats"

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailings = self.get_queryset()

        context.update(
            {
                "total_mailings": mailings.count(),
                "active_mailings": mailings.filter(status="started").count(),
                "success_count": MailingAttempt.objects.filter(
                    mailing__in=mailings, status="success"
                ).count(),
                "failed_count": MailingAttempt.objects.filter(
                    mailing__in=mailings, status="failed"
                ).count(),
                "recent_attempts": MailingAttempt.objects.filter(
                    mailing__in=mailings
                ).order_by("-attempt_time")[:10],
            }
        )
        return context


class UsersListView(PermissionRequiredMixin, ListView):
    """
    Просмотр списка пользователей (для менеджеров)
    Требует права can_view_users
    """

    permission_required = "users.can_view_users"
    template_name = "mailing/users_list.html"
    model = User
    context_object_name = "users"

    def get_queryset(self):
        return User.objects.filter(is_superuser=False).order_by("-date_joined")


class BlockUserView(PermissionRequiredMixin, View):
    """
    Блокировка пользователя (для менеджеров)
    Требует права can_block_user
    """

    permission_required = "users.can_block_user"

    def post(self, request, user_id):
        user_to_block = get_object_or_404(User, id=user_id)
        if user_to_block == request.user:
            messages.error(request, "Вы не можете заблокировать себя")
            return redirect("mailing:users_list")

        user_to_block.is_active = False
        user_to_block.save()
        messages.success(request, f"Пользователь {user_to_block.email} заблокирован")
        return redirect("mailing:users_list")


class DisableMailingView(PermissionRequiredMixin, View):
    """Отключение рассылки"""

    permission_required = "mailing.can_disable_mailing"

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.status = "completed"
        mailing.save()
        messages.success(request, f"Рассылка #{mailing.id} отключена")
        return redirect("mailing:mailing_list")
