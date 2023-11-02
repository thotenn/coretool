from enum import Enum
from array import array

from django.apps import apps
from typing import Union
from django.db import models
from django.db.models.fields.files import ImageField
from django.db.models.fields import CharField, BooleanField, FloatField, IntegerField
from django.forms.models import model_to_dict

from ..tools.images import image_get_content_file_from_bytearray
from ..tools.objects import tools_objects_getattributes_values
from ..tools.strings import strings_generate_token_urlsafe


# TODO: tambien necesitamos procesar los datos de salida, es decir, no retornar solo los pk, que el usuario decida,
#  como por ej createdat, etc


def get_fks_fields_inarray(fks, choices) -> list:
    res = list()
    if choices is None:
        choices = []
    for item in fks:
        fk = item["field"]
        if fk not in choices:
            res.append(item["field"])
    return res


def get_model_from_col_str(model_base: models.Model, col_str):
    return model_base._meta.get_field(col_str).get_path_info()[0].to_opts.model


def get_data_reg_with_fks(model_base, data, fks, choices) -> dict:
    # Obtenemos las columnas de los fks
    cols_fks = get_fks_fields_inarray(fks, choices)
    # Cargamos los datos que no son fk
    final_data: dict = dict()
    key: str
    for key in data:
        if key not in cols_fks:
            final_data[key] = data[key]
    # Relacionamos el field con el col
    field_col: dict = {}
    item: dict
    for item in fks:
        field_col[item["field"]] = item["col"]
    # Cargamos los datos fk

    item: str
    for item in cols_fks:
        if item in data:
            if data[item] is not None:
                model_item = get_model_from_col_str(model_base, item)
                if data[item] != '':
                    data_item_fk = {field_col[item]: data[item]}
                    final_data[item] = model_item.objects.get(**data_item_fk)
                else:
                    # En caso que el item sea tipo '' entonces un fk no puede ser '' pero si puede ser None
                    final_data[item] = None
    return final_data


def get_values_required(obj, values_req=None):
    res = {"status": True}
    if values_req is not None:
        for item in values_req:
            res[item] = getattr(obj, item)
    return res


def get_choices(fks):
    # Ahora crearemos un array donde esten todos los fields que son choices
    choices = []
    for item in fks:
        field: str = item['field']
        val: str = item['val']
        if val == '__choices__':
            choices.append(field)
    return choices


def format_data_for_upd(data_to_upd: dict, model_base: models.Model):
    """
    Formatea los datos para actualizar, de tal modo que solo se seleccionen las columnas propias del model
    """
    model_cols = model_base._meta.fields

    cols = [field.name for field in model_base._meta.fields]
    res = {}
    for item in data_to_upd:
        if item in cols:
            res[item] = data_to_upd[item]
        elif item == 'pk':
            res['pk'] = data_to_upd[item]
    return res


def processfk(fks, final_content_fk, content):
    # En esta seccion en caso de que se quieran procesar los fks
    # agregaremos columnas extras tipo '_COLUMNAFK' en donde expresaremos con los valores requeridos
    # y no por el pk del fk
    fields_type_fk: list = []
    for item in fks:
        field: str = item['field']
        fields_type_fk.append(field)
    if len(fields_type_fk) == len(final_content_fk):
        def get_fk_final_val(fk_field, fk_val):
            if fk_val is not None:
                for content_fk in final_content_fk:
                    if content_fk['field'] == fk_field:
                        return content_fk['data'][fk_val]
            return None

        for item_content in content:
            for sitem in fields_type_fk:
                item_content['_' + sitem] = get_fk_final_val(sitem, item_content[sitem])
    return content


def data_validation(Model_Class: models.Model, data_reg):
    """
    TODO: Mejorar
    Se supone que valida los datos que se envian en la api
    compara con los tipos de datos del model, si estos tienen default igualan el field al default
    si no, los agrega automaticamente dependiendo del tipo
    """
    # print('datareg: ', data_reg)
    for field_name in data_reg.keys():
        if field_name not in ['pk', 'id']:
            model_field = Model_Class._meta.get_field(field_name)

            field_class = model_field.__class__
            field_default_value = model_field.default
            field_nullable = model_field.null
            # print('name: ', field_class, 'type is: ', field_class)
            if data_reg[field_name] is None:
                if field_nullable is False:
                    if field_default_value is not None:
                        data_reg[field_name] = field_default_value
                    else:
                        print(field_class)
                        if field_class is CharField:
                            data_reg[field_name] = ''
                        elif field_class is IntegerField:
                            data_reg[field_name] = 0
                        elif field_class is FloatField:
                            data_reg[field_name] = 0.0
                        elif field_class is BooleanField:
                            data_reg[field_name] = False
            if field_class is ImageField:
                if data_reg[field_name] is not None:
                    # Creamos una instancia del objeto Model con los datos
                    # que propiamente seran guardados luego
                    # esto para utilizarlo luego en el upload_to
                    reg = Model_Class(**data_reg)

                    # Ya que el elemento enviado es un dict de valores,
                    # extraemos solo los valores y no los keys, y lo
                    # convertimos en un array para luego convertirlo en
                    # un byte array
                    ori_data_array = data_reg[field_name].values()
                    r = bytes(ori_data_array)

                    # Ya que un ImageField contiene una funcion de upload_to
                    # necesitamos esta funcion para tener el path correspondiente
                    upload_to_func = model_field.upload_to
                    file_path = upload_to_func(reg, strings_generate_token_urlsafe())

                    # Con la sgte funcion convertimos el bytearray en el archivo final
                    # y lo guardamos en el path que conseguimos anteriormente
                    # esto me retorna el mismo path pero con la extension del archivo
                    img_path = image_get_content_file_from_bytearray(r, file_path)

                    # Finalmente asignamos el path de la imagen al registro a guardar
                    data_reg[field_name] = img_path


def get_api_types(types: Union[str, list]):
    if type(types) == str:
        api_type = types
        types = api_type.split('_')
    return {
        "app_label": types[0],
        "model_name": types[1],
        "type_process": types[2]
    }


class PROCESS_TYPES(Enum):
    getall = 0
    contentfk = 1
    getbypk = 2
    create = 3
    update = 4
    delete = 5
    mdelete = 6


class CrudBasic:
    @staticmethod
    def crud_basic_getcontentfk(model_class: models.Model, fks: Union[list, None] = None,
                                choices: Union[list, None] = None) -> dict:
        # Esta var. seria un array tipo [{field: str, data: Array<{fk: val}>}]
        final_content_fk: list = list()
        if fks is not None:
            for item in fks:
                field: str = item['field']
                val: str = item['val']
                col: str = item['col']
                sub_fields_array = field.split('__')
                model_item = None
                if val != '__choices__':
                    # Solo si el val es distinto a esto, extraemos el model del sub item, ej: empresa__cliente__persona en donde
                    # el model del sub item final seria Persona
                    for sf in sub_fields_array:
                        model_item = model_class._meta.get_field(sf).get_path_info()[0].to_opts.model
                if field in choices:
                    choices_array = model_class._meta.get_field(field).choices
                    reg = [{col: obj[0], val: obj[1]} for obj in choices_array]
                elif val == '__str__':
                    qs = model_item.objects.all()
                    reg = [{col: getattr(obj, col), val: str(obj)} for obj in qs]
                else:
                    reg = list(model_item.objects.all().values(val, col))
                fdata: dict = {}
                for fitem in reg:  # [[{val, col},...], ...]
                    fdata[fitem[col]] = fitem[val]

                final_content_fk.append({"field": field, "data": fdata})
        return {"content": final_content_fk}

    @staticmethod
    def crud_basic_getall(model_class: models.Model, columns: list, fks: Union[list, None] = None,
                          choices: Union[list, None] = None, process_fks: bool = False) -> dict:
        if len(columns) == 0:
            # Si no hay columnas enviadas, se las envia todas
            content = list(model_class.objects.all())
        else:
            # En cambio si las hay, envia solo los valores de estas
            content = list(model_class.objects.all().values(*columns))
        # Esta var. seria un array tipo [{field: str, data: Array<{fk: val}>}]
        final_content_fk: list = list()
        if fks is not None:
            final_content_fk = CrudBasic.crud_basic_getcontentfk(
                model_class=model_class,
                fks=fks,
                choices=choices
            )["content"]
            if process_fks and len(final_content_fk) > 0:
                content = processfk(fks, final_content_fk, content)


                # fields_type_fk: list = []
                # for item in fks:
                #     field: str = item['field']
                #     fields_type_fk.append(field)
                # if len(fields_type_fk) == len(final_content_fk):
                #     def get_fk_final_val(fk_field, fk_val):
                #         if fk_val is not None:
                #             for content_fk in final_content_fk:
                #                 if content_fk['field'] == fk_field:
                #                     return content_fk['data'][fk_val]
                #         return None
                #     for item_content in content:
                #         for sitem in fields_type_fk:
                #             item_content['_' + sitem] = get_fk_final_val(sitem, item_content[sitem])
        return {"content": content, "content_fk": final_content_fk}

        # return obj
        # res = serializers.serialize('json', Banco.objects.all(), fields=('habilitado', 'nombre', 'oficialdecuenta',
        #                                                                  'telefono', 'descripcion'))
        # struct = json.loads(res)
        # res = [{**item['fields'], 'pk': item['pk']} for item in struct]
        # return res

    @staticmethod
    def crud_basic_getbypk(model_class: models.Model, data_pk: int, columns=None, fks: Union[list, None] = None,
                           choices: Union[list, None] = None, process_fks: bool = False) -> dict:
        """
        Obtiene la fila que coincide con la pk
        """
        if columns is None:
            columns = []
        temp_content = model_to_dict(model_class.objects.get(pk=data_pk))
        if len(columns) != 0:
            # Si no hay columnas enviadas, se las envia todas
            content = {}
            for item in columns:
                if item == 'pk':
                    item = 'id'
                content[item] = temp_content[item]
            content = [content]
        else:
            content = [temp_content]
        """
        else:
            # TODO: AQUI ENVIAR SOLO LAS COLUMNS REQUERIDAS, NO FUNCIONA CON GET SI PONGO values(*columns)
            # En cambio si las hay, envia solo los valores de estas
            content = [model_to_dict(model_class.objects.values(*columns).get(pk=data_pk))]
            print('hola que tal')
        """
        if fks is not None:
            final_content_fk = CrudBasic.crud_basic_getcontentfk(
                model_class=model_class,
                fks=fks,
                choices=choices
            )["content"]
            if process_fks and len(final_content_fk) > 0:
                content = processfk(fks, final_content_fk, content)
        return {"content": content[0]}

    @staticmethod
    def crud_basic_create(model_class, data, fks=None, choices=None, values_req=None) -> dict:
        try:
            if fks:
                data_reg = get_data_reg_with_fks(model_class, data, fks, choices)
            else:
                data_reg = data
            data_validation(model_class, data_reg)
            new_reg = model_class(**data_reg)
            try:
                new_reg.save()
            except Exception as err:
                print('Error en CrudBasic.crud_basic_create.reg_save:', err)
            return get_values_required(new_reg, values_req)
        except Exception as err:
            print('Error en CrudBasic.crud_basic_create:', err)
        # return {"pk": new_reg.pk}

    @staticmethod
    def crud_basic_update(model_class, data, fks=None, choices=None, values_req=None) -> dict:
        if fks:
            data_reg = get_data_reg_with_fks(model_class, data, fks, choices)
        else:
            data_reg = data
        data_validation(model_class, data_reg)
        upd_reg = model_class(**format_data_for_upd(data_reg, model_class))
        upd_reg.save()
        return get_values_required(upd_reg, values_req)
        # return {"pk": upd_reg.pk}

    @staticmethod
    def crud_basic_delete(model_class, data) -> dict:
        reg = model_class.objects.get(pk=data['pk'])
        reg.delete()
        return {"status": True}

    @staticmethod
    def crud_basic_delete_multiple(model_class, data) -> dict:
        try:
            model_class.objects.filter(pk__in=data).delete()
            return {"status": True}
        except Exception as err:
            print(err)
            return {"status": False}

    @staticmethod
    def crud_basic_get_content(types, data_set) -> Union[dict, None]:
        # print('dataset: ', data_set['data'])
        api_types = get_api_types(types)
        model_class = apps.get_model(app_label=api_types['app_label'], model_name=api_types['model_name'])
        type_process = api_types['type_process']
        content = None
        if 'fks' not in data_set:
            data_set['fks'] = None
        if 'data' not in data_set:
            data_set['data'] = None
        if 'columns' not in data_set:
            data_set['columns'] = None
        if 'process_fks' not in data_set:
            data_set['process_fks'] = False
        if 'choices' not in data_set:
            if data_set['fks'] is not None:
                data_set['choices'] = get_choices(data_set['fks'])
            else:
                data_set['choices'] = []
        if 'values_req' not in data_set:
            data_set['values_req'] = ["pk"]
        if 'pk' not in data_set:
            data_set['pk'] = 0
        data_set: dict = {
            "columns": data_set['columns'],
            "data": data_set['data'],
            "fks": data_set['fks'],
            "pk": data_set['pk'],
            "choices": data_set['choices'],
            "values_req": data_set['values_req'],
            "process_fks": data_set['process_fks']
        }
        if type_process == PROCESS_TYPES.getall.name:
            content = CrudBasic.crud_basic_getall(model_class, data_set['columns'], data_set['fks'],
                                                  data_set['choices'], data_set['process_fks'])
        elif type_process == PROCESS_TYPES.contentfk.name:
            content = CrudBasic.crud_basic_getcontentfk(model_class, data_set['fks'], data_set['choices'])
        elif type_process == PROCESS_TYPES.getbypk.name:
            content = CrudBasic.crud_basic_getbypk(model_class, data_set['pk'], data_set['columns'], data_set['fks'],
                                                   data_set['choices'], data_set['process_fks'])
        elif type_process == PROCESS_TYPES.create.name:
            content = CrudBasic.crud_basic_create(model_class, data_set['data'], data_set['fks'], data_set['choices'],
                                                  data_set['values_req'])
        elif type_process == PROCESS_TYPES.update.name:
            content = CrudBasic.crud_basic_update(model_class, data_set['data'], data_set['fks'], data_set['choices'],
                                                  data_set['values_req'])
        elif type_process == PROCESS_TYPES.delete.name:
            content = CrudBasic.crud_basic_delete(model_class, data_set['data'])
        elif type_process == PROCESS_TYPES.mdelete.name:
            content = CrudBasic.crud_basic_delete_multiple(model_class, data_set['data'])
        return content
