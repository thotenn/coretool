from django.db import models


def tools_dj_model_getfields(model_class):
    """
    Retorna todos los campos de un Model
    :param obj:
    :return:
    """
    return [field.name for field in model_class._meta.fields]


def tools_dj_models_getfields(obj):
    """
    Se supone que retorna todos los campos de un objeto (Model)
    Falta verificar esta funcion
    :param obj:
    :return:
    """
    return [field.name for field in obj.__class__._meta.fields]


def tools_dj_make_model(model_nombre, module=None, **kwargs):
    """ Genera un modelo Django dinámicamente
    El modelo generado tiene un propósito de ser un modelo 'dummy'
    para el sitio de Django Admin.

    Example:
        molde_clase = generar_django_model('MiModelo',
            modelo_atributo1='valor1',
            modelo_atributo2='valor2',
            Meta__meta_atributo1='m_valor1',
            Meta__meta_atributo2='m_valor2')

        // molde_clase es una clase equivalente a:
        from django.db import models

        class MiModelo(models.Model):
            modelo_atributo1 = 'valor1'
            modelo_atributo2 = 'valor2'

            class Meta:
                meta_atributo1 = 'm_valor1'
                meta_atributo2 = 'm_valor2'

    Arguments:
        _model_name {string} -- Nombre de la clase
        kwargs {dict} -- Atributos para la clase
        module: seria el modulo en el cual se encuentra el archivo, para rellener esto es necesario escribir,
                el nombre de la funcion o clase en la cual se requiere esta funcion y '.__module__, por ejemplo
                module = mifuncion.__module__
    """

    # Este diccionario guarda los atributos del modelo
    model_attr = {}
    # Este diccionario guarda los atributos de la clase Meta
    model_meta_attr = {
        "managed": False  # Por defecto, no persiste en la base de datos.
    }

    # Separa los argumentos de kwargs en los diccionarios model_attr y model_meta_attr
    # Los argumentos con la clave que inicia con 'Meta__' se copia al model_meta_attr
    # El resto se copia al model_attr
    for key, value in kwargs.items():
        if '__' in key:
            attr_type = key[:key.index('__')]
            # Si la clave comienza con 'Meta__'
            if attr_type == 'meta':
                meta_attr_key = key[6:]
                if len(meta_attr_key) == 0:
                    raise TypeError(
                        'Se esperaba un atributo de la clase meta luego del \'__\' en el argumento \'%s\'' % key)
                model_meta_attr[meta_attr_key] = value
            else:
                # Comentario: en esta función, se reserva las claves de los argumentos que contiene '__' para separar argumentos
                raise TypeError('Se obtuvo un \'argumento de clave\' (kwargs) inesperado \'%s\'' % key)
        else:
            model_attr[key] = value

    # Creación del modelo con el nombre 'model_nombre'
    if module is None:
        module = tools_dj_make_model.__module__
    model_class = type(model_nombre, (models.Model,),
                       {**model_attr, **{
                           "__module__": module,
                           "Meta": type("Meta", (), model_meta_attr)
                       }}
                       )

    return model_class
