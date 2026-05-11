import json
import requests
from xml.etree import ElementTree as ET
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Dueno, Mascota, Consulta
import os 
SOAP_URL = os.environ.get('SOAP_URL', 'http://localhost:8000/soap/')
SOAP_TIMEOUT = int(os.environ.get('SOAP_TIMEOUT', '30'))
HEADERS  = {'Content-Type': 'text/xml; charset=utf-8'}
TNS      = 'veterinaria.soap'

def soap_call(action, body_xml):
    envelope = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="{TNS}">
  <soap:Body>{body_xml}</soap:Body>
</soap:Envelope>"""
    resp = requests.post(SOAP_URL, data=envelope.encode('utf-8'),
                     headers={**HEADERS, 'SOAPAction': action},
                     timeout=SOAP_TIMEOUT)
    return ET.fromstring(resp.content)

# AUTH
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    error = None
    if request.method == 'POST':
        user = authenticate(request,
                            username=request.POST.get('username'),
                            password=request.POST.get('password'))
        if user is not None:
            login(request, user)
            return redirect(request.GET.get('next', 'index'))
        error = 'Usuario o contraseña incorrectos.'
    return render(request, 'vet/login.html', {'error': error})

def logout_view(request):
    logout(request)
    return redirect('login')

# HOME
@login_required
def index(request):
    return render(request, 'vet/index.html')

# DUENOS
@login_required
def duenos(request):
    data = Dueno.objects.all()
    return render(request, 'vet/duenos.html', {'duenos': data})

@login_required
def crear_dueno(request):
    if request.method == 'POST':
        try:
            soap_call('crear_dueno',
                f'<tns:crear_dueno>'
                f'<tns:nombre>{request.POST["nombre"]}</tns:nombre>'
                f'<tns:telefono>{request.POST["telefono"]}</tns:telefono>'
                f'<tns:email>{request.POST["email"]}</tns:email>'
                f'<tns:direccion>{request.POST["direccion"]}</tns:direccion>'
                f'</tns:crear_dueno>')
            messages.success(request, 'Dueño creado correctamente.')
        except Exception as e:
            messages.error(request, f'Error al crear dueño: {e}')
    return redirect('duenos')

@login_required
def editar_dueno(request, id):
    dueno = get_object_or_404(Dueno, pk=id)
    if request.method == 'POST':
        try:
            soap_call('actualizar_dueno',
                f'<tns:actualizar_dueno>'
                f'<tns:id>{id}</tns:id>'
                f'<tns:nombre>{request.POST["nombre"]}</tns:nombre>'
                f'<tns:telefono>{request.POST["telefono"]}</tns:telefono>'
                f'<tns:email>{request.POST["email"]}</tns:email>'
                f'<tns:direccion>{request.POST["direccion"]}</tns:direccion>'
                f'</tns:actualizar_dueno>')
            messages.success(request, 'Dueño actualizado.')
        except Exception as e:
            messages.error(request, f'Error al actualizar: {e}')
        return redirect('duenos')
    all_duenos = Dueno.objects.all()
    return render(request, 'vet/duenos.html', {'editar': dueno, 'duenos': all_duenos})

@login_required
def eliminar_dueno(request, id):
    try:
        soap_call('eliminar_dueno',
            f'<tns:eliminar_dueno><tns:id>{id}</tns:id></tns:eliminar_dueno>')
        messages.success(request, 'Dueño eliminado.')
    except Exception as e:
        messages.error(request, f'Error al eliminar: {e}')
    return redirect('duenos')

# MASCOTAS
@login_required
def mascotas(request):
    data         = Mascota.objects.select_related('dueno').all()
    todos_duenos = Dueno.objects.all()
    return render(request, 'vet/mascotas.html',
                  {'mascotas': data, 'duenos': todos_duenos})

@login_required
def crear_mascota(request):
    if request.method == 'POST':
        try:
            soap_call('crear_mascota',
                f'<tns:crear_mascota>'
                f'<tns:nombre>{request.POST["nombre"]}</tns:nombre>'
                f'<tns:especie>{request.POST["especie"]}</tns:especie>'
                f'<tns:raza>{request.POST["raza"]}</tns:raza>'
                f'<tns:edad>{request.POST["edad"]}</tns:edad>'
                f'<tns:dueno_id>{request.POST["dueno_id"]}</tns:dueno_id>'
                f'</tns:crear_mascota>')
            messages.success(request, 'Mascota registrada.')
        except Exception as e:
            messages.error(request, f'Error al crear mascota: {e}')
    return redirect('mascotas')

@login_required
def editar_mascota(request, id):
    mascota = get_object_or_404(Mascota, pk=id)
    if request.method == 'POST':
        try:
            soap_call('actualizar_mascota',
                f'<tns:actualizar_mascota>'
                f'<tns:id>{id}</tns:id>'
                f'<tns:nombre>{request.POST["nombre"]}</tns:nombre>'
                f'<tns:especie>{request.POST["especie"]}</tns:especie>'
                f'<tns:raza>{request.POST["raza"]}</tns:raza>'
                f'<tns:edad>{request.POST["edad"]}</tns:edad>'
                f'<tns:dueno_id>{request.POST["dueno_id"]}</tns:dueno_id>'
                f'</tns:actualizar_mascota>')
            messages.success(request, 'Mascota actualizada.')
        except Exception as e:
            messages.error(request, f'Error al actualizar: {e}')
        return redirect('mascotas')
    todos_duenos = Dueno.objects.all()
    all_mascotas = Mascota.objects.select_related('dueno').all()
    return render(request, 'vet/mascotas.html',
                  {'editar': mascota, 'mascotas': all_mascotas, 'duenos': todos_duenos})

@login_required
def eliminar_mascota(request, id):
    try:
        soap_call('eliminar_mascota',
            f'<tns:eliminar_mascota><tns:id>{id}</tns:id></tns:eliminar_mascota>')
        messages.success(request, 'Mascota eliminada.')
    except Exception as e:
        messages.error(request, f'Error al eliminar: {e}')
    return redirect('mascotas')

# CONSULTAS
@login_required
def consultas(request):
    data           = Consulta.objects.select_related('mascota').all()
    todas_mascotas = Mascota.objects.all()
    return render(request, 'vet/consultas.html',
                  {'consultas': data, 'mascotas': todas_mascotas})

@login_required
def crear_consulta(request):
    if request.method == 'POST':
        try:
            soap_call('crear_consulta',
                f'<tns:crear_consulta>'
                f'<tns:mascota_id>{request.POST["mascota_id"]}</tns:mascota_id>'
                f'<tns:fecha>{request.POST["fecha"]}</tns:fecha>'
                f'<tns:diagnostico>{request.POST["diagnostico"]}</tns:diagnostico>'
                f'<tns:costo>{request.POST["costo"]}</tns:costo>'
                f'<tns:veterinario>{request.POST["veterinario"]}</tns:veterinario>'
                f'</tns:crear_consulta>')
            messages.success(request, 'Consulta registrada.')
        except Exception as e:
            messages.error(request, f'Error al crear consulta: {e}')
    return redirect('consultas')

@login_required
def editar_consulta(request, id):
    consulta = get_object_or_404(Consulta, pk=id)
    if request.method == 'POST':
        try:
            soap_call('actualizar_consulta',
                f'<tns:actualizar_consulta>'
                f'<tns:id>{id}</tns:id>'
                f'<tns:mascota_id>{request.POST["mascota_id"]}</tns:mascota_id>'
                f'<tns:fecha>{request.POST["fecha"]}</tns:fecha>'
                f'<tns:diagnostico>{request.POST["diagnostico"]}</tns:diagnostico>'
                f'<tns:costo>{request.POST["costo"]}</tns:costo>'
                f'<tns:veterinario>{request.POST["veterinario"]}</tns:veterinario>'
                f'</tns:actualizar_consulta>')
            messages.success(request, 'Consulta actualizada.')
        except Exception as e:
            messages.error(request, f'Error al actualizar: {e}')
        return redirect('consultas')
    todas_mascotas = Mascota.objects.all()
    all_consultas  = Consulta.objects.select_related('mascota').all()
    return render(request, 'vet/consultas.html',
                  {'editar': consulta, 'consultas': all_consultas, 'mascotas': todas_mascotas})

@login_required
def eliminar_consulta(request, id):
    try:
        soap_call('eliminar_consulta',
            f'<tns:eliminar_consulta><tns:id>{id}</tns:id></tns:eliminar_consulta>')
        messages.success(request, 'Consulta eliminada.')
    except Exception as e:
        messages.error(request, f'Error al eliminar: {e}')
    return redirect('consultas')

# INFORME
@login_required
def informe(request):
    from xml.etree.ElementTree import Element, SubElement, tostring
    import xml.dom.minidom

    raiz           = Element('veterinaria')
    duenos_node    = SubElement(raiz, 'duenos')
    total_ingresos = 0

    for d in Dueno.objects.prefetch_related('mascotas__consultas').all():
        d_node      = SubElement(duenos_node, 'dueno', id=str(d.id), nombre=d.nombre)
        mascotas_nd = SubElement(d_node, 'mascotas')
        for m in d.mascotas.all():
            m_node       = SubElement(mascotas_nd, 'mascota',
                                      id=str(m.id), nombre=m.nombre, especie=m.especie)
            consultas_nd = SubElement(m_node, 'consultas')
            for c in m.consultas.all():
                SubElement(consultas_nd, 'consulta',
                           id=str(c.id), fecha=str(c.fecha), costo=str(c.costo))
                total_ingresos += float(c.costo)

    resumen         = SubElement(raiz, 'resumen')
    total_mascotas  = Mascota.objects.count()
    total_consultas = Consulta.objects.count()
    SubElement(resumen, 'total_ingresos').text  = str(round(total_ingresos, 2))
    SubElement(resumen, 'total_mascotas').text  = str(total_mascotas)
    SubElement(resumen, 'total_consultas').text = str(total_consultas)

    especies_node = SubElement(resumen, 'especies')
    especies_data = []
    for esp in ['perro', 'gato', 'ave', 'otro']:
        count = Mascota.objects.filter(especie=esp).count()
        pct   = round((count / total_mascotas * 100) if total_mascotas else 0, 1)
        SubElement(especies_node, 'especie',
                   nombre=esp, cantidad=str(count), porcentaje=str(pct))
        especies_data.append({'nombre': esp, 'cantidad': count, 'porcentaje': pct})

    xml_text = xml.dom.minidom.parseString(
        tostring(raiz, encoding='unicode')).toprettyxml(indent='  ')

    def build_tree(el):
        children = [build_tree(c) for c in el]
        return {'name': el.tag, 'children': children if children else None}

    return render(request, 'vet/informe.html', {
        'xml_text':  xml_text,
        'resumen':   {'total_ingresos': round(total_ingresos, 2),
                      'total_mascotas': total_mascotas,
                      'total_consultas': total_consultas},
        'especies':  especies_data,
        'tree_json': json.dumps(build_tree(raiz)),
    })
