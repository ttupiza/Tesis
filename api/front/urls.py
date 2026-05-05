from django.urls import path
from .views import (
    login_view,
    usuario_view,
    lista_usuario_view,
    registro_beneficiario_view,
    editar_beneficiario_view,
    eliminar_beneficiario_view,
    descargar_pdf_view,
)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('usuario/', usuario_view, name='usuario'),
    path('lista_usuario/', lista_usuario_view, name='lista_usuario'),
    path('registro_beneficiario/', registro_beneficiario_view, name='registro_beneficiario'),
    path('editar_beneficiario/<int:beneficiario_id>/', editar_beneficiario_view, name='editar_beneficiario'),
    path('eliminar_beneficiario/<int:beneficiario_id>/', eliminar_beneficiario_view, name='eliminar_beneficiario'),
    path('descargar_pdf/', descargar_pdf_view, name='descargar_pdf'),
]
