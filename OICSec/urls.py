from django.urls import path

from .views import *

urlpatterns = [
    path("", login_view, name="login"),
    path("home/", home_view, name="home"),
    path("perfil/", perfil_view, name="perfil"),
    path("logout/", logout_view, name="logout"),
    path("auditorias/", auditorias_view, name="auditorias"),
    path("auditorias/PAA/", upload_paa_view, name="uploadPaa"),
    path("auditorias/cedula/<int:auditoria_id>/", auditoria_cedula_view, name="auditoria_cedula"),
    path("auditorias/<int:auditoria_id>/", auditoria_detalle_view, name="auditoria_detalle"),
    path("controlesinternos/", control_interno_view, name="controlInterno"),
    path("controlesInternos/PACI/", upload_paci_view, name="uploadPaci"),
    path("controlesInternos/cedula/<int:control_id>/", control_cedula_view, name="control_cedula"),
    path("controlesInternos/<int:control_interno_id>/", control_interno_detalle_view, name="control_detalle"),
    path("intervenciones/", intervenciones_view, name="intervenciones"),
    path("intervenciones/PINT/", upload_pint_view, name="uploadPint"),
    path("intervenciones/cedula/<int:intervencion_id>/", intervencion_cedula_view, name="intervencion_cedula"),
    path("intervenciones/<int:intervencion_id>/", intervencion_detalle_view, name="intervencion_detalle"),
    path("supervision/", supervision_view, name="supervision"),
]
