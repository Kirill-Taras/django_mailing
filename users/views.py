from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import redirect, get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.views import View
from django.views.generic import CreateView
from django.contrib import messages
from django.contrib.auth.views import LoginView as BaseLoginView
from config.settings import DEFAULT_FROM_EMAIL
from users.forms import RegisterForm
from users.models import User


class RegisterView(CreateView):
    """Для регистрации пользователя"""
    form_class = RegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.verification_token = get_random_string(32)
        user.save()

        # Отправка письма
        current_site = get_current_site(self.request)
        mail_subject = 'Активация аккаунта на MailSender'
        message = render_to_string('users/email_verification.html', {
            'user': user,
            'domain': current_site.domain,
            'token': user.verification_token,
        })
        send_mail(
            mail_subject,
            message,
            DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        messages.success(self.request, 'Письмо с подтверждением отправлено на ваш email.')
        return super().form_valid(form)

class LogoutView(View):
    """Для выхода пользователя"""
    def post(self, request):
        if request.user.is_authenticated:
            logout(request)
            messages.info(request, "Вы успешно вышли из системы")
        return redirect("mailing:home")

    def get(self, request):
        return self.post(request)


class EmailVerifyView(View):
    def get(self, request, token):
        try:
            user = User.objects.get(verification_token=token)

            if not user.email_verified:
                user.email_verified = True
                user.is_active = True
                user.verification_token = None
                user.save()
                messages.success(request, 'Email успешно подтвержден! Теперь вы можете войти.')
                return render(request, 'users/email_verified.html')
            else:
                messages.info(request, 'Ваш email уже был подтвержден ранее.')
                return redirect('users:login')

        except User.DoesNotExist:
            return render(request, 'users/verify_error.html', status=400)


class LoginView(BaseLoginView):
    template_name = 'users/login.html'

    def form_valid(self, form):
        user = form.get_user()
        if not user.email_verified:
            messages.error(
                self.request,
                'Ваш email не подтвержден. Проверьте почту для активации.'
            )
            return self.form_invalid(form)
        return super().form_valid(form)


class ResendActivationView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.email_verified:
            messages.info(request, "Ваш email уже подтвержден")
            return redirect('mailing:home')

        # Повторная отправка письма (код аналогичный RegisterView)
        current_site = get_current_site(request)
        mail_subject = 'Активация аккаунта на MailSender'
        message = render_to_string('users/email_verification.html', {
            'user': request.user,
            'domain': current_site.domain,
            'token': request.user.verification_token,
        })
        send_mail(
            mail_subject,
            message,
            DEFAULT_FROM_EMAIL,
            [request.user.email],
            fail_silently=False,
        )

        messages.success(request, 'Письмо с подтверждением отправлено повторно.')
        return redirect('mailing:home')