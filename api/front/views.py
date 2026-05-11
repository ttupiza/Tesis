import random
import string

# Django shortcuts y herramientas de mensajes, transacciones y consultas.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Q

# Modelos principales usados en la aplicación.
from core.models import Usuario, Persona, Edificio, UsuarioEdificio, Notificacion


def login_view(request):
    # Vista para el formulario de acceso.
    # Valida el usuario y contraseña contra la tabla Usuario.
    error = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if username and password:
            try:
                usuario = Usuario.objects.get(username=username, password=password)
                request.session['usuario_id'] = usuario.id_usuario
                request.session['usuario_username'] = usuario.username
                return redirect('menu_seleccion')
            except Usuario.DoesNotExist:
                error = 'Usuario o contraseña incorrectos.'
        else:
            error = 'Ingrese usuario y contraseña.'

    return render(request, 'pages/login.html', {
        'error': error,
    })


def menu_seleccion_view(request):
    # Renderiza la página principal después del login.
    return render(request, 'pages/menu_seleccion.html')


def usuario_view(request):
    # Renderiza el formulario de registro de usuario.
    return render(request, 'pages/usuario.html', {
        'user': {},
    })

    return render(request, 'pages/usuario.html', {
        'user': {},
    })


def _build_beneficiario_data(usuario):
    # Construye un diccionario simple para usar en la lista de usuarios.
    persona = usuario.id_persona
    return {
        'id': usuario.id_usuario,
        'cedula': persona.ci if persona else '',
        'nombre': persona.name if persona else usuario.username,
        'apellido': persona.apellido if persona else '',
        'direccion': persona.direccion if persona else '',
        'email': persona.email if persona else '',
        'telefono': persona.telefono if persona else '',
    }


def _next_usuario_edificio_pk():
    # Obtiene el siguiente id manual para usuario_edificio
    # porque la tabla no utiliza auto increment en la base de datos.
    ultimo = UsuarioEdificio.objects.order_by('-id_usuario_beneficiario').first()
    return (ultimo.id_usuario_beneficiario + 1) if ultimo else 1


def _generate_random_password(length=10):
    # Genera una contraseña aleatoria alfanumérica.
    alphabet = string.ascii_letters + string.digits
    return ''.join(random.choice(alphabet) for _ in range(length))


def _build_random_username(primer_nombre, primer_apellido):
    # Genera un nombre de usuario a partir de la inicial del primer nombre
    # y el primer apellido, ajustando con un número si ya existe.
    primer_nombre = primer_nombre.strip()
    primer_apellido = primer_apellido.strip()
    if not primer_nombre or not primer_apellido:
        return None

    base_username = f"{primer_nombre[0].upper()}{primer_apellido.split()[0].capitalize()}"
    username = base_username
    counter = 1
    while Usuario.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    return username


def lista_usuario_view(request):
    # Vista que muestra la lista de beneficiarios y aplica búsqueda.
    query = request.GET.get('q', '').strip()
    usuarios = Usuario.objects.select_related('id_persona').all()

    if query:
        usuarios = usuarios.filter(
            Q(id_persona__ci__icontains=query) |
            Q(id_persona__name__icontains=query) |
            Q(id_persona__apellido__icontains=query) |
            Q(id_persona__email__icontains=query) |
            Q(username__icontains=query) |
            Q(usuarioedificio__id_edificio__nb_edificio__icontains=query)
        ).distinct()

    beneficiarios = [_build_beneficiario_data(usuario) for usuario in usuarios]

    return render(request, 'pages/lista_usuario.html', {
        'beneficiarios': beneficiarios,
        'request': request,
    })


def registro_beneficiario_view(request):
    # Vista para registrar un beneficiario y generar credenciales automáticas.
    generated_username = None
    generated_password = None
    user_data = {}
    form_error = None

    if request.method == 'POST':
        primer_nombre = request.POST.get('primerNombre', '').strip()
        segundo_nombre = request.POST.get('segundoNombre', '').strip()
        primer_apellido = request.POST.get('primerApellido', '').strip()
        segundo_apellido = request.POST.get('segundoApellido', '').strip()
        email = request.POST.get('email', '').strip()
        cedula = request.POST.get('cedula', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        id_edificio = request.POST.get('id_edificio', '').strip()

        user_data = {
            'primerNombre': primer_nombre,
            'segundoNombre': segundo_nombre,
            'primerApellido': primer_apellido,
            'segundoApellido': segundo_apellido,
            'email': email,
            'cedula': cedula,
            'telefono': telefono,
            'direccion': direccion,
            'id_edificio': int(id_edificio) if id_edificio else '',
        }

        if not (primer_nombre and primer_apellido and email and cedula):
            # Validación de campos obligatorios en el registro.
            form_error = 'Complete los campos obligatorios: nombre, apellido, email y cédula.'
        else:
            nombre_completo = f"{primer_nombre} {segundo_nombre}".strip()
            apellido_completo = f"{primer_apellido} {segundo_apellido}".strip()
            generated_username = _build_random_username(primer_nombre, primer_apellido)
            generated_password = _generate_random_password(10)

            if not generated_username:
                form_error = 'No se pudo generar un nombre de usuario. Verifica los datos ingresados.'
            else:
                persona = Persona.objects.create(
                    ci=cedula,
                    name=nombre_completo,
                    apellido=apellido_completo,
                    email=email,
                    telefono=telefono,
                    direccion=direccion,
                )
                usuario = Usuario.objects.create(
                    username=generated_username,
                    password=generated_password,
                    id_persona=persona,
                )
                if id_edificio:
                    # Si se seleccionó edificio, guarda la relación usuario-edificio.
                    UsuarioEdificio.objects.create(
                        id_usuario_beneficiario=_next_usuario_edificio_pk(),
                        id_usuario=usuario,
                        id_edificio_id=id_edificio,
                    )

    edificios = Edificio.objects.all()
    return render(request, 'pages/usuario.html', {
        'user': user_data,
        'edificios': edificios,
        'generated_username': generated_username,
        'generated_password': generated_password,
        'form_error': form_error,
    })


def editar_beneficiario_view(request, beneficiario_id):
    # Vista para editar los datos de un beneficiario existente.
    usuario = get_object_or_404(Usuario, id_usuario=beneficiario_id)
    persona = usuario.id_persona

    if request.method == 'POST':
        primer_nombre = request.POST.get('primerNombre', '').strip()
        segundo_nombre = request.POST.get('segundoNombre', '').strip()
        primer_apellido = request.POST.get('primerApellido', '').strip()
        segundo_apellido = request.POST.get('segundoApellido', '').strip()
        email = request.POST.get('email', '').strip()
        cedula = request.POST.get('cedula', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        id_edificio = request.POST.get('id_edificio', '').strip()

        if not (primer_nombre and primer_apellido and email and cedula):
            # Validación de campos obligatorios al editar el beneficiario.
            messages.error(request, 'Complete los campos obligatorios para actualizar.')
        else:
            persona.name = f"{primer_nombre} {segundo_nombre}".strip()
            persona.apellido = f"{primer_apellido} {segundo_apellido}".strip()
            persona.email = email
            persona.ci = cedula
            persona.telefono = telefono
            persona.direccion = direccion
            persona.save()

            usuario.username = email or cedula
            usuario.password = cedula
            usuario.save()

            # Actualizar la relación de edificio si el usuario seleccionó uno.
            if id_edificio:
                UsuarioEdificio.objects.filter(id_usuario=usuario).delete()  # Eliminar anterior
                UsuarioEdificio.objects.create(
                    id_usuario_beneficiario=_next_usuario_edificio_pk(),
                    id_usuario=usuario,
                    id_edificio_id=id_edificio,
                )
            else:
                UsuarioEdificio.objects.filter(id_usuario=usuario).delete()

            messages.success(request, 'Beneficiario actualizado correctamente.')
            return redirect('lista_usuario')

    # Obtener edificio actual
    usuario_edificio = UsuarioEdificio.objects.filter(id_usuario=usuario).first()
    id_edificio_actual = usuario_edificio.id_edificio.id_edificio if usuario_edificio else None

    data = {
        'primerNombre': persona.name.split(' ')[0] if persona and persona.name else '',
        'segundoNombre': ' '.join(persona.name.split(' ')[1:]) if persona and persona.name else '',
        'primerApellido': persona.apellido.split(' ')[0] if persona and persona.apellido else '',
        'segundoApellido': ' '.join(persona.apellido.split(' ')[1:]) if persona and persona.apellido else '',
        'email': persona.email if persona else '',
        'cedula': persona.ci if persona else '',
        'telefono': persona.telefono if persona else '',
        'direccion': persona.direccion if persona else '',
        'id_edificio': id_edificio_actual,
    }

    edificios = Edificio.objects.all()
    return render(request, 'pages/usuario.html', {
        'user': data,
        'editing': True,
        'beneficiario_id': beneficiario_id,
        'edificios': edificios,
    })


def eliminar_beneficiario_view(request, beneficiario_id):
    # Elimina un beneficiario y todas sus relaciones asociadas.
    usuario = get_object_or_404(Usuario, id_usuario=beneficiario_id)

    with transaction.atomic():
        # Eliminar registros relacionados antes de borrar el usuario.
        # Se hace en una transacción para evitar datos huérfanos.
        Notificacion.objects.filter(id_usuario=usuario).delete()
        UsuarioEdificio.objects.filter(id_usuario=usuario).delete()
        usuario.delete()
        if usuario.id_persona:
            Persona.objects.filter(id_persona=usuario.id_persona.id_persona).delete()

    messages.success(request, 'Beneficiario eliminado correctamente.')
    return redirect('lista_usuario')


def descargar_pdf_view(request):
    # Vista pared, actualmente solo muestra un mensaje de aviso.
    messages.warning(request, 'Funcionalidad de descarga PDF aún no implementada.')
    return redirect('lista_usuario')


def registro_edificio_view(request):
    # Vista para registrar un nuevo edificio.
    if request.method == 'POST':
        nombre = request.POST.get('nombreEdificio', '').strip()
        parroquia = request.POST.get('parroquia', '').strip()
        rif = request.POST.get('rif', '').strip()

        if not (nombre and rif):
            # Validación de campos obligatorios del edificio.
            messages.error(request, 'Complete el nombre del edificio y el RIF.')
        else:
            Edificio.objects.create(
                nb_edificio=nombre,
                rif=rif,
                direccion=parroquia,
            )
            messages.success(request, 'Edificio registrado correctamente.')
            return redirect('menu_seleccion')

    return render(request, 'pages/registro_edificio.html', {
        'editing': False,
    })


def editar_edificio_view(request, edificio_id):
    # Vista para editar los datos de un edificio existente.
    edificio = get_object_or_404(Edificio, id_edificio=edificio_id)

    if request.method == 'POST':
        nombre = request.POST.get('nombreEdificio', '').strip()
        parroquia = request.POST.get('parroquia', '').strip()
        rif = request.POST.get('rif', '').strip()

        if not (nombre and rif):
            # Validación de campos obligatorios al editar el edificio.
            messages.error(request, 'Complete el nombre del edificio y el RIF para guardar los cambios.')
        else:
            edificio.nb_edificio = nombre
            edificio.direccion = parroquia
            edificio.rif = rif
            edificio.save()
            messages.success(request, 'Edificio actualizado correctamente.')
            return redirect('lista_edificios')

    return render(request, 'pages/registro_edificio.html', {
        'editing': True,
        'edificio': edificio,
    })


def lista_edificios_view(request):
    # Vista que lista los edificios y permite búsqueda por nombre, rif o dirección.
    query = request.GET.get('q', '').strip()
    edificios = Edificio.objects.all()

    if query:
        # Filtra la lista de edificios según el texto de búsqueda.
        edificios = edificios.filter(
            Q(nb_edificio__icontains=query) |
            Q(rif__icontains=query) |
            Q(direccion__icontains=query)
        )

    return render(request, 'pages/lista_edificios.html', {
        'edificios': list(edificios),
        'request': request,
    })


def eliminar_edificio_view(request, edificio_id):
    # Elimina el edificio y sus relaciones con usuarios antes de borrar.
    edificio = get_object_or_404(Edificio, id_edificio=edificio_id)

    with transaction.atomic():
        # Eliminar registros relacionados antes de borrar el edificio
        UsuarioEdificio.objects.filter(id_edificio=edificio).delete()
        edificio.delete()

    messages.success(request, 'Edificio eliminado correctamente.')
    return redirect('lista_edificios')
