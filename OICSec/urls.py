from django.urls import path

from .views import *

urlpatterns = [
    path("", login_view, name="login"),
    path("home/",
         home_view, name="home"),
    path("perfil/",
         perfil_view, name="perfil"),
    path("logout/",
         logout_view, name="logout"),
    path("auditorias/",
         auditorias_view, name="auditorias"),
    path('auditoria/<int:pk>/delete/',
         delete_auditoria, name='auditoria-delete'),
    path("auditorias/PAA/",
         upload_paa_view, name="uploadPaa"),
    path("auditorias/cedula/<int:auditoria_id>/",
         auditoria_cedula_view, name="auditoria_cedula"),
    path("auditorias/<int:auditoria_id>/",
         auditoria_detalle_view, name="auditoria_detalle"),
    path("controlesinternos/",
         control_interno_view, name="controlInterno"),
    path('controlinterno/<int:pk>/delete/',
         delete_controlinterno, name='controlinterno-delete'),
    path("controlesInternos/PACI/",
         upload_paci_view, name="uploadPaci"),
    path("controlesInternos/cedula/<int:control_id>/",
         control_cedula_view, name="control_cedula"),
    path("controlesInternos/<int:control_interno_id>/",
         control_interno_detalle_view, name="control_detalle"),
    path("intervenciones/",
         intervenciones_view, name="intervenciones"),
    path('intervencion/<int:pk>/delete/',
         delete_intervencion, name='intervencion-delete'),
    path("intervenciones/PINT/",
         upload_pint_view, name="uploadPint"),
    path("intervenciones/cedula/<int:intervencion_id>/",
         intervencion_cedula_view, name="intervencion_cedula"),
    path("intervenciones/<int:intervencion_id>/",
         intervencion_detalle_view, name="intervencion_detalle"),
    path("minuta/<int:fiscalizacion_id>/",
         minuta_view, name="minuta"),
    path("minuta/<int:fiscalizacion_id>/mes/<int:mes>/",
         minuta_mes_view, name="minuta_mes"),
    path("personal/",
         personal_view, name="personal"),
    path("personal/oics/",
         oics_view, name="oics"),
    path("personal/direcciones/",
         direcciones_view, name="direcciones"),
    path("personal/oics/<int:oic_id>/",
         personal_oic_view, name="personal_oic"),
    path("personal/direcciones/<str:direccion_nombre>/",
         personal_direccion_view, name="personal_direccion"),
    path('personal/oics/editar-titular/<int:personal_id>/',
         editar_titular_view, name='editar_titular_view'),
    path('personal/direcciones/editar-director/<int:personal_id>',
         editar_director_view, name='editar_director_view'),
    path('personal/oics/asignar-cargo-titular/<int:personal_id>/<int:tipo_cargo_id>/',
         asignar_cargo_titular, name='asignar_cargo_titular'),
    path('personal/oics/eliminar-titular/<int:personal_id>/',
         eliminar_titular_view, name='eliminar_titular'),
    path('personal/oics/editar-personal/<int:personal_id>/',
         editar_personal_view, name='editar_personal_view'),
    path('personal/oics/asignar-cargo-personal/<int:personal_id>/<int:tipo_cargo_id>/',
         asignar_cargo_personal, name='asignar_cargo_personal'),
    path('personal/oics/eliminar-personal/<int:personal_id>/',
         eliminar_personal_oic_view, name='eliminar_personal'),
    path("personal/oics/crear_titular/<int:oic_id>",
         crear_titular_view, name='crear_titular'),
    path("personal/oics/crear_personal/<int:oic_id>",
         crear_personal_view, name='crear_personal'),
    path('personal/direcciones/eliminar-director/<int:personal_id>/',
         eliminar_director_view, name='eliminar_director'),
    path("personal/direcciones/<str:direccion_nombre>/crear_director/",
         crear_director_view, name='crear_director'),
    path('personal/direcciones/editar-personal/<int:personal_id>/',
         editar_personal_direccion_view, name='editar_personal_direccion_view'),
    path('personal/direcciones/eliminar-personal-direccion/<int:personal_id>/',
         eliminar_personal_direccion_view, name='eliminar_personal_direccion'),
    path("personal/direcciones/<str:direccion_nombre>/crear_personal/",
         crear_personal_direccion_view, name='crear_personal_direccion'),
    path("download/<int:archivo_id>/",
         download_archivo, name='download_archivo'),
    path("personal/oics/<int:oic_id>/limpiar",
         limpiar_personal_oic, name='limpiar_personal_oic'),
    path("personal/direcciones/<str:direccion_nombre>/limpiar",
         limpiar_personal_direccion, name='limpiar_personal_direccion'),
    path("estructuras/",
         estructuras_view, name='estructuras'),
    path("estructuras/oics/",
         estructuras_oics_view, name='estructuras_oics'),
    path('estructuras/oics/<int:oic_id>/',
         editar_oic, name='editar_oic'),
    path("estructuras/actividades/",
         estructuras_actividades_view, name='estructuras_actividades'),
]
