from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages

def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    error = None

    if request.method == 'POST':
        if form.is_valid():
            login(request, form.get_user())
            # Al loguearse, lo ideal es ir al Menú Principal
            return redirect('menu_seleccion') 
        error = 'Usuario o contraseña incorrectos.'

    return render(request, 'pages/login.html', {
        'form': form,
        'error': error,
    })

def menu_seleccion_view(request):
    # Esta vista simplemente carga el panel de control con las tarjetas
    return render(request, 'pages/menu_seleccion.html')

def usuario_view(request):
    return render(request, 'pages/usuario.html', {
        'user': request.user,
    })

def lista_usuario_view(request):
    # Aquí iría la consulta a tu base de datos de beneficiarios
    return render(request, 'pages/lista_usuario.html', {
        'beneficiarios': [],
    })

def registro_beneficiario_view(request):
    # Asegúrate de tener un template específico o manejar la lógica de guardado
    return render(request, 'pages/usuario.html', {
        'user': request.user,
    })

def registro_edificio_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombreEdificio')
        parroquia = request.POST.get('parroquia')
        rif = request.POST.get('rif')
        cant_apartamentos = request.POST.get('cantApartamentos')

        if nombre and parroquia and rif and cant_apartamentos:
            # Aquí guardarías en la base de datos
            messages.success(request, 'Edificio registrado correctamente.')
            return redirect('menu_seleccion')
        
    return render(request, 'pages/registro_edificio.html')

# Vistas de apoyo (mantenimiento)
def editar_beneficiario_view(request, beneficiario_id):
    return render(request, 'pages/usuario.html', {'user': request.user})

def eliminar_beneficiario_view(request, beneficiario_id):
    return redirect('lista_usuario')

def descargar_pdf_view(request):
    return redirect('lista_usuario')