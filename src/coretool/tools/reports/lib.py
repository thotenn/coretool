import datetime as dt
from io import BytesIO

from django.template.loader import get_template
from django.http import HttpResponse
from django.conf import settings

from xhtml2pdf import pisa


class PdfResponse(HttpResponse):
    """
    Una clase HTTP Response que contiene un PDF descargable.
    """

    def __init__(self, report_content, filename, *args, **kwargs):
        super(PdfResponse, self).__init__(*args, **kwargs)

        self['Content-Length'] = len(report_content)
        self['Content-Type'] = 'application/pdf'
        self['Content-Disposition'] = 'attachment; filename="{}.pdf"'.format(
            filename)
        self['mimetype'] = 'application/pdf'

        self.write(report_content)


class InlinePdfResponse(PdfResponse):
    """
    Una clase HTTP Response que contiene un PDF desplegable en pantalla.
    """

    def __init__(self, report_content, filename, *args, **kwargs):
        super(InlinePdfResponse, self).__init__(
            report_content, filename, *args, **kwargs)
        self['Content-Disposition'] = 'inline; filename="{}.pdf"'.format(
            filename)


class Report:
    def __init__(self, title: str = None, template_str: str = None,
                 filename: str = None, logo: str = None, logo_info: str = None):
        self.default_title = title or 'Reporte'
        # Para anhadir el sub directorio de templates add esto en el TEMPLATE/DIR del settings:
        # os.path.join(BASE_PROJECT, '. . . /controllers/tools/reports')
        self.template_default = template_str or 'rtemplates/base/index.html'
        self.default_filename = filename or self.default_title + '_' + dt.datetime.now().strftime("%Y_%m_%d")
        self.logo = logo or ''
        self.logo_info = logo_info or ''

    def _get_abs_url(request):
        '''
        Esta funcion retorna la url root o absoluta de la que se ha enviado el request
        ej.: https://127.0.0.1:8000
        '''
        urls = {
            'ABSOLUTE_ROOT': request.build_absolute_uri('/')[:-1].strip("/"),
            'ABSOLUTE_ROOT_URL': request.build_absolute_uri('/').strip("/"),
        }

        return urls

    @staticmethod
    def _tools_dict_merge(principal: dict, json_for_merge: dict, replace: bool = False) -> dict:
        for key in principal.keys():
            if key in json_for_merge:
                if replace:
                    principal[key] = json_for_merge[key]
        for key, value in json_for_merge.items():
            if not key in principal:
                principal[key] = value
        return principal

    @staticmethod
    def _tools_pdf_render(template_src, context_dict={}):
        template = get_template(template_src)
        html = template.render(context_dict)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("latin-1")), result)
        if not pdf.err:
            return HttpResponse(result.getvalue(), content_type='application/pdf')
        return None

    @staticmethod
    def _tools_pdf_generate(template_src: str, context_data: dict, download_direct: bool = False,
                            filename: str = None, just_html: bool = False) -> HttpResponse:
        # TODO crear una pagina de Not Found
        """
        Retorna un HttpResponse ya sea en html simple o pdf dependiendo de los parametros de entrada,
        claro que para hacer funcionar el generador necesitaremos un template y el context_data debe
        cubrir las variables del template
        :param template_src:
        :param context_data:
        :param download_direct:
        :param filename:
        :param just_html:
        :return: HttpResponse (pdf o html)
        """

        if just_html:
            html = get_template(template_src).render(context_data)
            return HttpResponse(html)
        pdf = Report._tools_pdf_render(template_src, context_data)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            if filename is None:
                filename = 'download_' + dt.datetime.now().strftime("%Y_%m_%d")
            filename = "%s.pdf" % filename
            content = "inline; filename=%s" % filename

            if download_direct:
                content = "attachment; filename=%s" % filename
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not Found")

    def get_css_for_static_pages(self, header_id: str = 'pdf_content_header', footer_id: str = 'pdf_content_footer',
                                 static_header_footer: bool = True):
        """
        Este seria el css para que el pdf contenga encabezado y footer estatico, tiene que estar del siguiente modo
        en el template:
        {{ css_base.css|safe }}
        """
        css = ''
        if static_header_footer:
            css = ('<style type="text/css">@page {' +
                'size: a4 portrait;' +
                '@frame header_frame {' +
                    '-pdf-frame-content: ' + header_id +';' +
                    'left: 50pt; width: 512pt; top: 20pt; height: 90pt;' +
                '}' +
                '@frame content_frame {' +
                    'left: 50pt; width: 512pt; top: 75pt; height: 700pt;' +
                '}' +
                '@frame footer_frame {' +
                    '-pdf-frame-content: ' + footer_id + ';' +
                    'left: 50pt; width: 512pt; top: 785pt; height: 25pt;' +
                '}}</style>')
        return {
            'header_id': header_id,
            'footer_id': footer_id,
            'css': css
        }

    def make(self, details: list, title: str = None, filename: str = None,
             template_str: str = None, to_download: bool = False,
             just_html: bool = False, header_details: dict = None, header: dict = None,
             footer: dict = None, static_header_footer: bool = True, extra: dict = None) -> HttpResponse:
        """
        :param details: Tiene que tener la forma:
            [{
                table_title: '...',
                titles: ['...',],
                details: [ ['...',], ]
            }]
        :param title:
        :param filename:
        :param template_str:
        :param to_download:
        :param just_html:
        :param header_details:
        :param header:
        :param footer:
        :param static_header_footer:
        :return:
        """

        if not title:
            title = self.default_title
        header_principal = {
            'id': 'pdf_content_header',
            'title': title,
            'logo': self.logo,
            'logo_info': self.logo_info,
            'date': dt.datetime.now().strftime("%Y/%m/%d"),
            'header_details': header_details
        }
        if settings.DEBUG:
            # Cuando el DEBUG esta activado, por alguna razon no toma en cuenta la url static de las imagenes
            #header_principal['logo'] = + header_principal['logo']
            pass
        if header:
            header_principal = Report._tools_dict_merge(header_principal, header, True)
        footer_principal = {
            'id': 'pdf_content_footer',
            'date': dt.datetime.now().strftime("%Y/%m/%d"),
            'hour': dt.datetime.now().strftime("%H:%M:%S")
        }
        if footer:
            footer_principal = Report._tools_dict_merge(footer_principal, footer, True)

        css_base = self.get_css_for_static_pages(header_id=header_principal['id'],
                                                 footer_id=footer_principal['id'],
                                                 static_header_footer=static_header_footer)
        if details:
            empty_total = True
            for sdet in details:
                if 'details' in sdet:
                    if len(sdet['details']) > 0:
                        empty_total = False
                        break
            empty_details = empty_total
        else:
            empty_details = True

        content_data = {
            'css_base': css_base,
            'header': header_principal,
            'empty_details': empty_details,
            'details': details,
            'footer': footer_principal,
            'extra': extra
        }
        if filename is None:
            filename = self.default_filename
        if template_str is None:
            template_str = self.template_default
        return Report._tools_pdf_generate(template_str, content_data, to_download, filename, just_html)

"""
Links utiles:
https://xhtml2pdf.readthedocs.io/en/latest/format_html.html?highlight=head#example-with-2-static-frames-and-1-content-frame
"""
