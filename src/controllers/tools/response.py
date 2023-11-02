from django.http import HttpResponse

def ZipResponse(zip_file, zip_filename):
    """Genera una respuesta HTTP con el archivo zip.

    Example:
        from apps.base.controllers.tools.files import empaquetar_zip

        def get_archivo(self, request):
            zip_file = empaquetar_zip(["archivo1.txt", "archivo2.txt"],
                "empaquetado")
            return ZipResponse(zip_file, "empaquetado.zip")

    
    Arguments:
        zip_file {bytes} -- Archivo zip en binario.
        zip_filename {string} -- Nombre del archivo Zip.
    
    Returns:
        HttpResponse -- Respuesta HTTP con el archivo zip.
    """
    response = HttpResponse(
        zip_file, content_type="application/x-zip-compressed")
    response['Content-Disposition'] = 'attachment; filename={}'.format(
        zip_filename)
    return response
