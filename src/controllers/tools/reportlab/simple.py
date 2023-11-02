from django.http import FileResponse
from django.http import HttpResponse

from reportlab.lib.pagesizes import letter

from reportlab.platypus import Table

from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm, inch
PAGESIZE = (140 * mm, 216 * mm)
BASE_MARGIN = 5 * mm

class ReportlabController:
    def __init__(self, filename: str = 'file'):
        self.filename = filename
        self.pagesize = letter

    def _new_buff(self):
        self.buff = BytesIO()
    def _close_buff(self):
        self.buff.close()
    def _get_response(self, file_name:str ='pdf', download: bool = True) -> HttpResponse:
        f_split = file_name.split('.')
        if len(f_split) > 1:
            if f_split[len(f_split)-1] != 'pdf':
                file_name = file_name + '.pdf'
        else:
            file_name = file_name + '.pdf'
        response = HttpResponse(content_type='application/pdf')
        if download:
            download_code = 'attachment'
        else:
            download_code = 'inline'
        response['Content-Disposition'] = '{0}; filename={1}'.format(download_code, file_name)
        response.write(self.buff.getvalue())
        self.buff.close()
        return response

    def get_pdf_file(self, buff):
        pass

    def make_simple_table(self, data: list, file_name: str = 'file', download: bool = False) -> HttpResponse:
        self._new_buff()
        table = Table(data)
        menu_pdf = SimpleDocTemplate(self.buff, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        elements = []
        elements.append(table)
        menu_pdf.build(elements)
        return self._get_response(file_name, download)

    def make_table(self, data: list, file_name: str = 'file', download: bool = False) -> HttpResponse:
        self._new_buff()
        table = Table(data)
        menu_pdf = SimpleDocTemplate(self.buff, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        style = TableStyle([
            ('BACKGROUND', (0, 0), (3, 0), colors.green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.antiquewhite),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Courier-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ])
        table.setStyle(style)

        # 2) Alternate backgroud color
        rowNumb = len(data)
        for i in range(1, rowNumb):
            if i % 2 == 0:
                bc = colors.whitesmoke
            else:
                bc = colors.darkgray

            ts = TableStyle(
                [('BACKGROUND', (0, i), (-1, i), bc)]
            )
            table.setStyle(ts)

        # 3) Add borders
        ts = TableStyle(
            [
                ('BOX', (0, 0), (-1, -1), 2, colors.black),

                ('LINEBEFORE', (2, 1), (2, -1), 2, colors.red),
                ('LINEABOVE', (0, 2), (-1, 2), 2, colors.green),

                ('GRID', (0, 1), (-1, -1), 2, colors.black),
            ]
        )
        table.setStyle(ts)

        elements = list()
        elements.append(table)
        menu_pdf.build(elements)

        return self._get_response(file_name, download)



    @staticmethod
    def prueba():
        from reportlab.pdfgen import canvas
        buffer = BytesIO()

        # Create the PDF object, using the buffer as its "file."
        p = canvas.Canvas(buffer)

        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        p.drawString(100, 100, "Hello world.")

        # Close the PDF object cleanly, and we're done.
        p.showPage()
        p.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='hello.pdf')
