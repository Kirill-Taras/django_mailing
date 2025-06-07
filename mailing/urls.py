from django.urls import path
from .views import home_view, ClientListView, ClientCreateView, ClientUpdateView, ClientDeleteView, ClientDetailView

urlpatterns = [
    path('', home_view, name='home'),
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('clients/add/', ClientCreateView.as_view(), name='client_add'),
    path('clients/<int:pk>/edit/', ClientUpdateView.as_view(), name='client_edit'),
    path('clients/<int:pk>/delete/', ClientDeleteView.as_view(), name='client_delete'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client_detail'),
]
