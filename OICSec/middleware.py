from axes.handlers.proxy import AxesProxyHandler
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpRequest

class BlockedUserMiddleware:
    """
    Middleware para redirigir a los usuarios bloqueados (por IP) a una página de bloqueo personalizada
    antes de que puedan acceder a la página de inicio de sesión.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if request.path in [reverse('login'), reverse('admin:login')]:
            if AxesProxyHandler.is_locked(request):
                return redirect('account_locked')

        return self.get_response(request)