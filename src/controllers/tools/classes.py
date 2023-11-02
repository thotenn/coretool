from pydoc import locate


class AbstractStatic(staticmethod):
    """
    Esto servira para convertir una funcion de una clase en un metodo estatico y abstracto


    Ejemplo:
    from abc import ABC
    class Persona(ABC):
        @AbstractStatic
        def set_nombre(texto):
            ...
    """
    __slots__ = ()

    def __init__(self, function):
        super(AbstractStatic, self).__init__(function)
        function.__isabstractmethod__ = True
    __isabstractmethod__ = True


def tools_classes_import_from_str2(str_dir: str, splitter='.'):
    """
    Esta funcion retorna la clase correspondiente a la direccion del archivo, str_dir,
    Pero si se ira por un archivo en carpetas profundas, estas tienen que estar incluidas en algun o los inits de las
    carpetas principales
    """
    components = str_dir.split(splitter)
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def tools_classes_import_from_str(str_dir: str, splitter='.'):
    """
    Esta funcion retorna la clase correspondiente a la direccion del archivo, str_dir, no hace falta incluir en el init
    """
    if splitter != '.':
        str_dir = str_dir.replace(splitter, '.')
    return locate(str_dir)
