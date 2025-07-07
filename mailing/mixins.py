from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import AccessMixin


class OwnerRequiredMixin(AccessMixin):
    """Миксин для проверки, что пользователь является владельцем объекта"""

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != request.user and not request.user.has_perm(
            "mailing.can_view_all_mailings"
        ):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
