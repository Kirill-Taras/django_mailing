from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.shortcuts import render
from mailing.models import Client, Message

"""Главная страница"""
def home_view(request):
    return render(request, 'home.html')

"""Страницы для работы с клиентами"""
class ClientListView(ListView):
    model = Client
    template_name = 'mailing/client_list.html'
    context_object_name = 'clients'

class ClientCreateView(CreateView):
    model = Client
    fields = ['email', 'full_name', 'comment']
    template_name = 'mailing/client_form.html'
    success_url = reverse_lazy('client_list')

class ClientUpdateView(UpdateView):
    model = Client
    fields = ['email', 'full_name', 'comment']
    template_name = 'mailing/client_form.html'
    success_url = reverse_lazy('client_list')

class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'mailing/client_confirm_delete.html'
    success_url = reverse_lazy('client_list')

class ClientDetailView(DetailView):
    model = Client
    template_name = 'mailing/client_detail.html'
    context_object_name = 'client'

"""Страницы для работы с сообщениями"""
class MessageListView(ListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'messages'

class MessageCreateView(CreateView):
    model = Message
    fields = ['subject', 'body']
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

class MessageUpdateView(UpdateView):
    model = Message
    fields = ['subject', 'body']
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')

class MessageDetailView(DetailView):
    model = Message
    template_name = 'mailing/message_detail.html'
    context_object_name = 'message'
