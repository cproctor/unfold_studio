from django.views import View
from django.contrib.auth.mixins import AccessMixin
from django.http import JsonResponse

class BaseView(AccessMixin, View):
    pass


class AuthenticatedView(BaseView):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {"error": "Authentication required to access this resource."},
                status=401
            )
        return super().dispatch(request, *args, **kwargs)