from django.contrib import admin
from .models import Client, Mailing


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "comment")
    search_fields = ("full_name", "email")


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "owner")
    list_filter = ("status", "owner")
    actions = ["disable_mailings"]

    def disable_mailings(self, request, queryset):
        queryset.update(status="completed")

    disable_mailings.short_description = "Отключить выбранные рассылки"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.has_perm("mailing.can_view_all_mailings"):
            return qs.filter(owner=request.user)
        return qs
