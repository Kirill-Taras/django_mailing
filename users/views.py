from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView
from django.contrib import messages

from users.forms import RegisterForm

"""Для регистрации пользователя"""


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, "Регистрация успешна! Проверьте email для активации."
        )
        return response


"""Для выхода пользователя"""


class LogoutView(View):
    def post(self, request):
        if request.user.is_authenticated:
            logout(request)
            messages.info(request, "Вы успешно вышли из системы")
        return redirect("mailing:home")

    def get(self, request):
        return self.post(request)
