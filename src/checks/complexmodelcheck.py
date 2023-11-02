import json
import os

from django.db import connection

from .messages import (DiferenciaComplexCodigoWarning,
                                         ExisteMultiplesComplexCodigoWarning,
                                         FixtureNoUniformeWarning,
                                         FixtureNoValidoWarning,
                                         NoCoincidenColumnasModeloTablaWarning,
                                         NoExisteComplexCodigoWarning,
                                         NoExisteFixtureWarning,
                                         NoExisteTablaWarning)


def check_database_table(complex_model):
    """
    Verificación de la consistencia entre el modelo y la tabla en la base de datos.

    Verifica la existencia de la tabla y compara las columnas que especifica el
    modelo y las columnas existentes en la base de datos.

    Debe ser ejecutado previo a la función check_fixture(). Si esta función retorna
    algún error, la función check_fixture() no debe ser ejecutado.
    """
    errors = []

    # Verifica si la tabla del modelo no existe en la base de datos
    if complex_model._meta.db_table not in connection.introspection.table_names():
        errors.append(NoExisteTablaWarning(complex_model))
        return errors

    # Verifica si las columnas del modelo coinciden con las columnas de la base de datos
    if hasattr(connection.introspection, 'get_table_description'):
        with connection.cursor() as cursor:
            # Obtiene las columnas a partir del modelo
            model_columns_name = set(
                [field.column for field in complex_model._meta.fields])

            # Obtiene las columnas a partir de la base de datos
            table_description = connection.introspection.get_table_description(
                cursor,
                complex_model._meta.db_table)
            db_columns_name = set(
                [field.name for field in table_description])

            if db_columns_name != model_columns_name:
                errors.append(
                    NoCoincidenColumnasModeloTablaWarning(complex_model))
                return errors

    return errors


def check_fixture(complex_model):
    """
    Verifica los objetos cargados en el fixture con la base de datos.

    Nota: Actualmente esta función sólamente puede manejar los fixtures
    de tipo JSON. No está implementado para los otros formatos como XML
    o para archivos comprimidos como ZIP.
    """
    errors = []

    # Verifica si el fixture existe en la ruta especificada
    if not os.path.exists(complex_model.fixture):
        errors.append(NoExisteFixtureWarning(complex_model))
        return errors

    with open(complex_model.fixture) as json_file:
        try:
            json_data = json.load(json_file)
            # Por cada objeto del fixture
            for json_instance_data in json_data:
                model_label = json_instance_data['model']
                json_instance = json_instance_data['fields']

                # Si el modelo del fixture es correcto
                if model_label == complex_model._meta.label_lower:
                    # Comprueba el objeto del fixture
                    errors += check_instance(
                        complex_model,
                        json_instance)
                else:
                    errors.append(
                        FixtureNoUniformeWarning(complex_model, model_label))
        except ValueError as exc:
            errors.append(FixtureNoValidoWarning(complex_model, exc))

    return errors


def check_instance(complex_model, fixture_instance):
    """
    Comprueba si el objeto del fixture existe y tiene los valores correctos
    en la base de datos.
    """
    errors = []

    queryset = complex_model.objects.filter(codigo=fixture_instance['codigo'])

    # Si no existe el código en la tabla
    if queryset.count() == 0:
        errors.append(NoExisteComplexCodigoWarning(
            complex_model, fixture_instance['codigo']))
    # Si el código no es único en la tabla
    elif queryset.count() > 1:
        errors.append(ExisteMultiplesComplexCodigoWarning(
            complex_model, fixture_instance['codigo']))
    # Si el código es único en la tabla
    else:
        database_instance = queryset.values()[0]
        for field in fixture_instance.keys():
            # Si el dato de la base de datos no coincide con del dato del fixture
            if fixture_instance[field] != database_instance[field]:
                errors.append(DiferenciaComplexCodigoWarning(
                    complex_model, field, database_instance, fixture_instance))

    return errors
