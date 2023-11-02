import traceback
from collections.abc import Iterable
from datetime import date, datetime, time

from django.contrib import admin
from django.conf import settings
from django.http import HttpResponseNotAllowed
from django.http.response import HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import redirect, render
from django.urls import path, re_path, reverse

from .lib import InlinePdfResponse, PdfResponse, Report


class CustomViewModelAdmin(admin.ModelAdmin):
    """ ModelAdmin abstracto para sitios con vistas personalizadas.

    Este ModelAdmin reemplaza la vista asociada al URL que aparece en el
    menú de cada aplicación (del sitio admin).

    Requiere de:
        view {funcion} -- La vista principal de la página.
    """
    view = None

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name

        urls = [
            path('', self.view, name='%s_%s_changelist' % info),
        ]

        return urls


class BaseReporteModelAdmin(CustomViewModelAdmin):
    """ ModelAdmin abstracto para páginas de reportes.

    Este ModelAdmin ofrece tres vistas:
        1. Vista principal (principal_view)
        2. Vista para servir el reporte (generar_view)
    Los detalles de estas vistas se encuentran más abajo de este documento.

    Nota: si la clase de formulario (forms.Form) posee un atributo 'grupos',
    se pueden agrupar los campos en filas para una visualización más compacta.

    Requiere de:
        titulo_pagina {string} -- Título de la página
        filtro_form {string} -- Formulario de la página
        get_nombre_archivo_generado {funcion}: función que retorna el nombre
            del archivo del reporte generado.
        get_details {funcion} -- función que recolecta y procesa las informaciones
            de la base de datos y retorna un diccionario con las informaciones
            que se mostrarán en el reporte.

    Example:
        from django import forms
        from django.conf import settings
        from apps.reportes.admins.base import BaseReporteModelAdmin
        from apps.rrhh.funcionarios.models.base import Funcionario

        class FiltroForm(forms.Form):
            groups = [
                ["nombre", "apellido"],
            ]
            nombre = forms.CharField(label='Nombre', max_length=100, required=False)
            apellido = forms.CharField(label='Apellido', max_length=100, required=False)

        class PruebaAdmin(BaseReporteModelAdmin):
            titulo_pagina = 'Reporte de Pruebita'
            filtro_form = FiltroForm
            logo = (settings.STATIC_DIR + '.../logo.png')
            header = None
            footer = None
            extra = None
            template_dir = 'rtemplates/base/index.html'

            def get_nombre_archivo_generado(self, request):
                return 'Reporte de Nomina por Sucursal'

            def get_details(self, form):
                details = [{
                    'table_title': 'Cédulas no identificadas',
                    'titles': ['CI'],
                    'details': [['prueba0'], ['prueba1']]
                }, {
                    'table_title': 'Funcionarios sin Cargos',
                    'titles': ['CI', 'Nombre'],
                    'details': [['prueba0', 'prueba1']]
                }]
                return details

    Luego para anhadir esto a la vista en el archivo admin.py anhadir:
    from django.contrib import admin
    from ...,..models import tools_dj_make_model
    def make_model(model_nombre, **kwargs):
        return tools_dj_make_model(model_nombre, make_model.__module__, **kwargs)
    admin.site.register(make_model('Prueba', meta__verbose_name_plural='Reporte de Pruebas'), PruebaAdmin)
    """

    titulo_pagina = None
    filtro_form = None
    logo = None
    header = None
    footer = None
    extra = None
    template_dir = 'rtemplates/base/index.html'

    admin_report_template = 'rtemplates/admin/reportes_form.html'

    def get_nombre_archivo_generado(self, request):
        """
        Debe retornar el nombre del archivo del reporte generado.
        """
        raise NotImplementedError

    def get_details(self, form):
        """
        Debe retornar un diccionario con las informaciones
        que se mostrarán en el reporte.
        """
        raise NotImplementedError

    def __init__(self, *args, **kwargs):
        self.view = self.principal_view
        super(BaseReporteModelAdmin, self).__init__(*args, **kwargs)

    def get_urls(self):
        urls = super(BaseReporteModelAdmin, self).get_urls()
        urls += [
            re_path(r'^generar$', self.generar_view, name='{}_generar_pdf'.format(
                self.__class__.__name__.lower())),
        ]
        return urls

    def principal_view(self, request):
        """
        1. Vista Principal (principal_view):
            Esta vista muestra la página con un formulario y botones
            para generar el reporte.
        """
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

        if request.method not in ['GET', 'POST']:
            return HttpResponseNotAllowed(['GET', 'POST'])

        if request.method == 'POST':
            form = self.filtro_form(request.POST)
        else:
            form = self.filtro_form()

        if request.method == 'POST':
            if '_descargar' in request.POST:
                # Redirige la página a la vista de generar_view
                return HttpResponseRedirect('generar?' + request.POST.urlencode())
            else:
                context = self.generar_context(request, form)
                return render(request, self.admin_report_template, context)
        else:  # if request.method == 'GET'
            context = self.generar_context(request, form)
            return render(request, self.admin_report_template, context)

    def generar_context(self, request, form):
        context = {
            "title": self.titulo_pagina,
            "generar_pdf_url": None,
            "form": form
        }
        if request.method == 'POST' and form.is_valid():
            context["generar_pdf_url"] = reverse('admin:{}_generar_pdf'.format(
                self.__class__.__name__.lower())) + "?" + request.POST.urlencode()
        return context

    def generar_view(self, request):
        """
        2. Vista para servir el reporte (generar_view):
            Esta vista ofrece el archivo de reporte generado por la clase
            Report. El URL asociado a esta vista es '/generar'

            Durante la ejecución de esta vista, se realizan las siguientes tareas:
                2.1 Recolecta las informaciones de la base de datos, luego las procesa
                    y genera un diccionario python que contiene las informaciones que
                    aparecerán en el reporte. Este proceso se realiza en el método
                    get_details().

                2.2 Retorna el reporte, en archivo .pdf, .xls o en otros formatos.
        """
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

        if request.method != 'GET':
            return HttpResponseNotAllowed(['GET'])

        form = self.filtro_form(request.GET)
        if form.is_valid():
            datos = self.get_details(form)
            try:
                reporte_nombre = self.get_nombre_archivo_generado(request)
                params = self.get_parametros(request, form)
                report = Report(
                    title=self.titulo_pagina,
                    filename=reporte_nombre,
                    logo=self.logo or '',
                    template_str=self.template_dir
                )
                response = report.make(
                    details=datos,
                    header_details=params,
                    just_html=False,
                    header=self.header,
                    footer=self.footer,
                    extra=self.extra
                )
                if response.status_code == 200:
                    if '_descargar' in request.GET:
                        return PdfResponse(response.content, reporte_nombre)
                    else:
                        return InlinePdfResponse(response.content, reporte_nombre)
                else:
                    return HttpResponseServerError("<h1>HTTP 500: Ocurrió un error en el servidor de reporte</h1>")
            except Exception as exc:
                print(exc)
                traceback.print_tb(exc.__traceback__)
                return HttpResponseServerError("<h1>HTTP 500: Ocurrió un error durante la creación del reporte</h1>")
        else:
            return HttpResponseServerError("<h1>HTTP 500: Los parámetros del formulario no son válidos.</h1>")

    def get_parametros(self, request, form):
        # Transforma en string los campos del formulario
        form_data = form.cleaned_data
        for field_name, value in form_data.items():
            # Si 'value' es un iterable (una lista o Queryset por ejemplo)
            if not isinstance(value, str) and isinstance(value, Iterable):
                # es concatenado mediante comas.
                form_data[field_name] = ", ".join(
                    map(lambda element: str(element), value))
            # Si 'value' es de tipo fecha+hora
            elif isinstance(value, datetime) and isinstance(value, date):
                form_data[field_name] = value.strftime('%d/%m/%Y %H:%M:%S')
            # Si 'value' es de tipo fecha
            elif not isinstance(value, datetime) and isinstance(value, date):
                form_data[field_name] = value.strftime('%d/%m/%Y')
            # Si 'value' es de tipo hora
            elif isinstance(value, time):
                form_data[field_name] = value.strftime('%H:%M:%S')

        return {**{
            "Usuario": request.user.username},
            **form_data}

    def reporte_de_prueba(self):
        r = Report(
            title='Informe de importación',
            filename='prueba',
            logo=(settings.STATIC_DIR + 'logo.png')
        )
        header_details = {
            'Usuario': 'pruebauser'
        }
        details = [{
            'table_title': 'Cédulas no identificadas',
            'titles': ['CI'],
            'details': [['prueba0'], ['prueba1']]
        }, {
            'table_title': 'Funcionarios sin Cargos',
            'titles': ['CI', 'Nombre'],
            'details': [['prueba0', 'prueba1']]
        }]
        return r.make(
            details=details,
            header_details=header_details,
            just_html=False
        )
