from io import BytesIO

from django.http import HttpResponse

from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER


class Report:
    def __init__(self, filename: str = 'file'):
        self.filename = filename
        self.pagesize = letter

    def _new_buff(self):
        self.buff = BytesIO()

    def _get_buff(self):
        return self.buff

    def _close_buff(self):
        self.buff.close()

    def _get_response(self, file_name: str = 'pdf', download: bool = False) -> HttpResponse:
        f_split = file_name.split('.')
        if len(f_split) > 1:
            if f_split[len(f_split)-1] != 'pdf':
                file_name = file_name + '.pdf'
        else:
            file_name = file_name + '.pdf'
        response: HttpResponse = HttpResponse(content_type='application/pdf')
        download_code: str = 'inline'
        if download:
            download_code = 'attachment'
        response['Content-Disposition'] = '{0}; filename={1}'.format(download_code, file_name)
        response.write(self.buff.getvalue())
        self.buff.close()
        return response

    def header_title(self, text: str):
        self.c.setLineWidth(.3)
        self.c.setFont('Helvetica', 22)
        self.c.drawString(30, 750, text)

    def header_title_sub(self, text: str):
        self.c.setFont('Helvetica', 12)
        self.c.drawString(30, 735, text)

    def header_date(self, text: str):
        self.c.setFont('Helvetica-Bold', 12)
        self.c.drawString(480, 750, text)
        self.c.line(460, 747, 560, 747)

    def table_head_styles(self, cols: list):
        pass

    def table(self, data: list):
        self.styles = getSampleStyleSheet()


    def prueba(self):
        self._new_buff()
        self.c = canvas.Canvas(self.buff, pagesize=A4)
        self.header_title('Reporte')
        self.header_title_sub('Sub titulo')
        self.header_date('12/12/12')
        self.c.save()
        return self._get_response()
