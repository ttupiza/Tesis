from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect


def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    error = None

    if request.method == 'POST':
        if form.is_valid():
            login(request, form.get_user())
            return redirect('login')
        error = 'Usuario o contraseña incorrectos.'

    return render(request, 'pages/login.html', {
        'form': form,
        'error': error,
    })


def usuario_view(request):
    return render(request, 'pages/usuario.html', {
        'user': request.user,
    })


def lista_usuario_view(request):
    return render(request, 'pages/lista_usuario.html', {
        'beneficiarios': [],
    })


def registro_beneficiario_view(request):
    return render(request, 'pages/usuario.html', {
        'user': request.user,
    })


def editar_beneficiario_view(request, beneficiario_id):
    return render(request, 'pages/usuario.html', {
        'user': request.user,
    })


def eliminar_beneficiario_view(request, beneficiario_id):
    return redirect('lista_usuario')


def descargar_pdf_view(request):
    return redirect('lista_usuario')
