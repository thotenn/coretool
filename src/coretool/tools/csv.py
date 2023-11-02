import csv
import io
from django.core.files.base import File


class ToolsCsv:
    def __init__(self, **kwargs):
        if 'path' in kwargs:
            self.path = kwargs['path']

    def csv_to_array(self, filecsv_path: File or None, delimiter: str or None = ';', cols=None) -> list or None:
        '''
        Esta funcion convierte los datos de un archivo CSV a uno de formato array tipo [[],...]

        filecsv_path : seria el objeto que referencia al archivo en cuestion
        delimiter : seria el delimitador de las columnas del csv
        cols : seria las columnas que queremos capturar, si dejamos en None, trae todos los registros

        return Array[]
        '''
        #print('delimiter===')
        #print(delimiter)
        try:
            if filecsv_path is None:
                if self.path is not None:
                    filecsv_path = self.path
                else:
                    return None
            if delimiter is None:
                delimiter = ';'
            result = []
            data_set = filecsv_path.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            next(io_string)
            for column in csv.reader(io_string, delimiter='|'):
                if cols is None:
                    result.append(column[0].split(delimiter))
                else:
                    subrow = []
                    for col in cols:
                        column[0] = column[0].replace('"', '')
                        subrow.append(column[0].split(delimiter)[col])
                    result.append(subrow)
            return result
        except Exception as error:
            print('Error en core.controllers.tools.csv.csv_to_array')
            print(error)
            return Exception
