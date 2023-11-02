import csv
import io
import os
import zipfile

from django import forms
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import path


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()


class CsvExportMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Exportar a CSV"

class CsvImport(admin.ModelAdmin):
    #AVISO para que esto funcione, un modelo debera extenderse de esta clase
    #lo cual no es muy recomendable, habra que hacer una clase interfaz en la cual
    #se usaran estas funciones para el manejo especifico de estos csv

    #https://medium.com/@simathapa111/how-to-upload-a-csv-file-in-django-3a0d6295f624
    class CsvImportForm(forms.Form):
        csv_file = forms.FileField()

    change_list_template = "templates/admin/extended/change_list.html"

    def get_urls(urls):
        #urls = super().get_urls()
        print(urls)
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(obj_class, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]

            data_set = csv_file.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            next(io_string)
            for column in csv.reader(io_string, delimiter=',', quotechar="|"):
                print('____________________________')
                for item in column:
                    print(item)

            '''
            reader = csv.reader(csv_file)
            print(reader)
            '''
            obj_class.message_user(request, "Tu archivo CSV ha sido importado")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "templates/admin/forms/csv_form.html", payload
        )

def empaquetar_zip(filenames, zip_subdir):
    """Genera un archivo ZIP dada una lista de las
        ubicaciones de los archivos a empaquetar.

    Example:
        filenames = ["media/files/archivo1.txt",
                     "media/files/archivo2.csv"]
        z = empaquetar_zip(filenames, "comprimido")
    
    Arguments:
        filenames {list of string} -- Lista de directorios de los
            archivos que contendrá.
        zip_subdir {string} -- Carpeta dentro del archivo ZIP en
            donde contendrán los archivos especificados en filenames.
    
    Returns:
        bytes -- Archivo ZIP en binario con los archivos empaquetados.
    """
    bio = io.BytesIO()
    zf = zipfile.ZipFile(bio, "w")

    for fpath in filenames:
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)
        zf.write(fpath, zip_path)
    zf.close()

    return bio.getvalue()
