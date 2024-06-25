from django.urls import path


from .views import login_view, home_view, auditorias_view, minutas_view, perfil_view, logout_view, upload_paa_view, \
    auditoria_detalle_view, control_interno_view, upload_paci_view

urlpatterns = [
    path("", login_view, name="login"),
    path("home/", home_view, name="home"),
    path("perfil/", perfil_view, name="perfil"),
    path("logout/", logout_view, name="logout"),
    path("auditorias/", auditorias_view, name="auditorias"),
    path("auditorias/PAA/", upload_paa_view, name="uploadPaa"),
    path("auditorias/<int:auditoria_id>/", auditoria_detalle_view, name="auditoria_detalle"),
    path("controlesinternos/", control_interno_view, name="controlInterno"),
    path("controlesInternos/PACI/", upload_paci_view, name="uploadPaci"),
    path("minutas/", minutas_view, name="minutas"),
]