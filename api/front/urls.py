from django.urls import path
from .views import (
    login_view,
    menu_seleccion_view,
    usuario_view,
    lista_usuario_view,
    registro_beneficiario_view,
    editar_beneficiario_view,
    eliminar_beneficiario_view,
    descargar_pdf_view,
    registro_edificio_view,
    lista_edificios_view,
    editar_edificio_view,
    eliminar_edificio_view,
)

urlpatterns = [
    # Ruta de acceso al login del sistema.
    path('login/', login_view, name='login'),
    
    # Página principal después del inicio de sesión.
    path('menu_seleccion/', menu_seleccion_view, name='menu_seleccion'),
    
    # Rutas para el registro y la edición de beneficiarios.
    path('usuario/', usuario_view, name='usuario'),
    path('lista_usuario/', lista_usuario_view, name='lista_usuario'),
    path('registro_beneficiario/', registro_beneficiario_view, name='registro_beneficiario'),
    path('registro_edificio/', registro_edificio_view, name='registro_edificio'),
    # Rutas para administrar edificios.
    path('lista_edificios/', lista_edificios_view, name='lista_edificios'),
    path('editar_edificio/<int:edificio_id>/', editar_edificio_view, name='editar_edificio'),
    path('eliminar_edificio/<int:edificio_id>/', eliminar_edificio_view, name='eliminar_edificio'),
    
    # Rutas para administrar beneficiarios existentes.
    path('editar_beneficiario/<int:beneficiario_id>/', editar_beneficiario_view, name='editar_beneficiario'),
    path('eliminar_beneficiario/<int:beneficiario_id>/', eliminar_beneficiario_view, name='eliminar_beneficiario'),
    path('descargar_pdf/', descargar_pdf_view, name='descargar_pdf'),
]