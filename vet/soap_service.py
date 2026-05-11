from spyne import Application, rpc, ServiceBase, Integer, Unicode, Float, Array, ComplexModel
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication
from django.views.decorators.csrf import csrf_exempt

# ── Tipos SOAP ────────────────────────────────────────────────────────────────

class DuenoType(ComplexModel):
    id        = Integer
    nombre    = Unicode
    telefono  = Unicode
    email     = Unicode
    direccion = Unicode

class MascotaType(ComplexModel):
    id      = Integer
    nombre  = Unicode
    especie = Unicode
    raza    = Unicode
    edad    = Integer
    dueno   = Unicode   # nombre del dueño

class ConsultaType(ComplexModel):
    id          = Integer
    mascota     = Unicode
    fecha       = Unicode
    diagnostico = Unicode
    costo       = Float
    veterinario = Unicode

# ── Servicio SOAP ─────────────────────────────────────────────────────────────

class VeterinariaService(ServiceBase):

    # ── DUEÑOS ────────────────────────────────────────────────────────────────
    @rpc(_returns=Array(DuenoType))
    def listar_duenos(ctx):
        from vet.models import Dueno
        return [DuenoType(id=d.id, nombre=d.nombre, telefono=d.telefono,
                          email=d.email, direccion=d.direccion)
                for d in Dueno.objects.all()]

    @rpc(Integer, _returns=DuenoType)
    def obtener_dueno(ctx, id):
        from vet.models import Dueno
        d = Dueno.objects.get(pk=id)
        return DuenoType(id=d.id, nombre=d.nombre, telefono=d.telefono,
                         email=d.email, direccion=d.direccion)

    @rpc(Unicode, Unicode, Unicode, Unicode, _returns=DuenoType)
    def crear_dueno(ctx, nombre, telefono, email, direccion):
        from vet.models import Dueno
        d = Dueno.objects.create(nombre=nombre, telefono=telefono,
                                 email=email, direccion=direccion)
        return DuenoType(id=d.id, nombre=d.nombre, telefono=d.telefono,
                         email=d.email, direccion=d.direccion)

    @rpc(Integer, Unicode, Unicode, Unicode, Unicode, _returns=DuenoType)
    def actualizar_dueno(ctx, id, nombre, telefono, email, direccion):
        from vet.models import Dueno
        d = Dueno.objects.get(pk=id)
        d.nombre=nombre; d.telefono=telefono; d.email=email; d.direccion=direccion
        d.save()
        return DuenoType(id=d.id, nombre=d.nombre, telefono=d.telefono,
                         email=d.email, direccion=d.direccion)

    @rpc(Integer, _returns=Unicode)
    def eliminar_dueno(ctx, id):
        from vet.models import Dueno
        Dueno.objects.get(pk=id).delete()
        return "Dueño eliminado correctamente"

    # ── MASCOTAS ──────────────────────────────────────────────────────────────
    @rpc(_returns=Array(MascotaType))
    def listar_mascotas(ctx):
        from vet.models import Mascota
        return [MascotaType(id=m.id, nombre=m.nombre, especie=m.especie,
                            raza=m.raza, edad=m.edad, dueno=m.dueno.nombre)
                for m in Mascota.objects.select_related('dueno').all()]

    @rpc(Unicode, Unicode, Unicode, Integer, Integer, _returns=MascotaType)
    def crear_mascota(ctx, nombre, especie, raza, edad, dueno_id):
        from vet.models import Mascota, Dueno
        d = Dueno.objects.get(pk=dueno_id)
        m = Mascota.objects.create(nombre=nombre, especie=especie,
                                   raza=raza, edad=edad, dueno=d)
        return MascotaType(id=m.id, nombre=m.nombre, especie=m.especie,
                           raza=m.raza, edad=m.edad, dueno=d.nombre)

    @rpc(Integer, Unicode, Unicode, Unicode, Integer, Integer, _returns=MascotaType)
    def actualizar_mascota(ctx, id, nombre, especie, raza, edad, dueno_id):
        from vet.models import Mascota, Dueno
        m = Mascota.objects.get(pk=id)
        m.nombre=nombre; m.especie=especie; m.raza=raza; m.edad=edad
        m.dueno=Dueno.objects.get(pk=dueno_id); m.save()
        return MascotaType(id=m.id, nombre=m.nombre, especie=m.especie,
                           raza=m.raza, edad=m.edad, dueno=m.dueno.nombre)

    @rpc(Integer, _returns=Unicode)
    def eliminar_mascota(ctx, id):
        from vet.models import Mascota
        Mascota.objects.get(pk=id).delete()
        return "Mascota eliminada correctamente"

    # ── CONSULTAS ─────────────────────────────────────────────────────────────
    @rpc(_returns=Array(ConsultaType))
    def listar_consultas(ctx):
        from vet.models import Consulta
        return [ConsultaType(id=c.id, mascota=c.mascota.nombre,
                             fecha=str(c.fecha), diagnostico=c.diagnostico,
                             costo=float(c.costo), veterinario=c.veterinario)
                for c in Consulta.objects.select_related('mascota').all()]

    @rpc(Integer, Unicode, Unicode, Float, Unicode, _returns=ConsultaType)
    def crear_consulta(ctx, mascota_id, fecha, diagnostico, costo, veterinario):
        from vet.models import Consulta, Mascota
        m = Mascota.objects.get(pk=mascota_id)
        c = Consulta.objects.create(mascota=m, fecha=fecha,
                                    diagnostico=diagnostico, costo=costo,
                                    veterinario=veterinario)
        return ConsultaType(id=c.id, mascota=m.nombre, fecha=str(c.fecha),
                            diagnostico=c.diagnostico, costo=float(c.costo),
                            veterinario=c.veterinario)

    @rpc(Integer, Integer, Unicode, Unicode, Float, Unicode, _returns=ConsultaType)
    def actualizar_consulta(ctx, id, mascota_id, fecha, diagnostico, costo, veterinario):
        from vet.models import Consulta, Mascota
        c = Consulta.objects.get(pk=id)
        c.mascota=Mascota.objects.get(pk=mascota_id); c.fecha=fecha
        c.diagnostico=diagnostico; c.costo=costo; c.veterinario=veterinario
        c.save()
        return ConsultaType(id=c.id, mascota=c.mascota.nombre, fecha=str(c.fecha),
                            diagnostico=c.diagnostico, costo=float(c.costo),
                            veterinario=c.veterinario)

    @rpc(Integer, _returns=Unicode)
    def eliminar_consulta(ctx, id):
        from vet.models import Consulta
        Consulta.objects.get(pk=id).delete()
        return "Consulta eliminada correctamente"

    # ── INFORME ───────────────────────────────────────────────────────────────
    @rpc(_returns=Unicode)
    def informe_xml(ctx):
        """Devuelve el XML completo para el informe con árbol y totales."""
        from vet.models import Dueno, Mascota, Consulta
        from xml.etree.ElementTree import Element, SubElement, tostring
        import xml.dom.minidom

        raiz = Element('veterinaria')
        duenos_node = SubElement(raiz, 'duenos')
        total_ingresos = 0

        for d in Dueno.objects.prefetch_related('mascotas__consultas').all():
            d_node = SubElement(duenos_node, 'dueno', id=str(d.id))
            mascotas_node = SubElement(d_node, 'mascotas')
            for m in d.mascotas.all():
                m_node = SubElement(mascotas_node, 'mascota',
                                    id=str(m.id), especie=m.especie)
                consultas_node = SubElement(m_node, 'consultas')
                for c in m.consultas.all():
                    SubElement(consultas_node, 'consulta',
                               id=str(c.id), costo=str(c.costo))
                    total_ingresos += float(c.costo)

        resumen = SubElement(raiz, 'resumen')
        total_mascotas = Mascota.objects.count()
        total_consultas = Consulta.objects.count()
        SubElement(resumen, 'total_ingresos').text = str(round(total_ingresos, 2))
        SubElement(resumen, 'total_mascotas').text = str(total_mascotas)
        SubElement(resumen, 'total_consultas').text = str(total_consultas)

        # Porcentaje por especie
        especies_node = SubElement(resumen, 'especies')
        for esp in ['perro','gato','ave','otro']:
            count = Mascota.objects.filter(especie=esp).count()
            pct = round((count/total_mascotas*100) if total_mascotas else 0, 1)
            SubElement(especies_node, 'especie',
                       nombre=esp, cantidad=str(count), porcentaje=str(pct))

        xml_str = xml.dom.minidom.parseString(
            tostring(raiz, encoding='unicode')).toprettyxml(indent='  ')
        return xml_str


# ── Montar Django + SOAP ──────────────────────────────────────────────────────

soap_app = Application(
    [VeterinariaService],
    tns='veterinaria.soap',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11(),
)

veterinaria_service = csrf_exempt(DjangoApplication(soap_app))