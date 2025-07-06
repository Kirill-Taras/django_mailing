from django.contrib.auth.views import LoginView
from django.urls import path

from .apps import UsersConfig
from .views import RegisterView, LogoutView, EmailVerifyView, Re, ResendActivationView

app_name = UsersConfig.name

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('verify/<str:token>/', EmailVerifyView.as_view(), name='verify'),
    path('resend-activation/', ResendActivationView.as_view(), name='resend_activation'),
]
