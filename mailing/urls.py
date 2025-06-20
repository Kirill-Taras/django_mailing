from django.urls import path

from .apps import MailingConfig
from .views import home_view, ClientListView, ClientCreateView, ClientUpdateView, ClientDeleteView, ClientDetailView, \
    MessageListView, MessageCreateView, MessageUpdateView, MessageDeleteView, MessageDetailView

app_name = MailingConfig.name

urlpatterns = [
    #Главная страница
    path('', home_view, name='home'),
    #Страницы для работы с получателями рассылок
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('clients/add/', ClientCreateView.as_view(), name='client_add'),
    path('clients/<int:pk>/edit/', ClientUpdateView.as_view(), name='client_edit'),
    path('clients/<int:pk>/delete/', ClientDeleteView.as_view(), name='client_delete'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client_detail'),
    #Страницы для работы с сообщениями
    path('messages/', MessageListView.as_view(), name='message_list'),
    path('messages/add/', MessageCreateView.as_view(), name='message_add'),
    path('messages/<int:pk>/edit/', MessageUpdateView.as_view(), name='message_edit'),
    path('messages/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),
    path('messages/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
]
