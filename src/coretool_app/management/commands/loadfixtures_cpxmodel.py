"""
Comando updatecomplex

Carga el fixture de los submodelos de *ComplexModel a la base de datos.

*De hecho que podemos hacer que sea apto para todas las bases de modelos

Actualmente soporta solo los fixtures JSON.

Ejemplo de uso:
    # Actualiza los constantes de todos los submodelos de ComplexModel
    # de todas las aplicaciones
    python manage.py updatecomplex --settings=cbarh.settings.tu_settings

    # Actualiza los constantes de todos los submodelos de ComplexModel
    # de la aplicación administrador
    python manage.py updatecomplex administrador --settings=cbarh.settings.tu_settings

    # Actualiza los constantes de los modelos Moneda y Moneda2
    python manage.py updatecomplex administrador.Moneda administrador.Moneda2 --settings=cbarh.settings.tu_settings

    # Actualiza los constantes de todos los modelos excepto el modelo Moneda
    python manage.py updatecomplex -exclude administrador.Moneda --settings=cbarh.settings.tu_settings
"""

import os

import django.apps
from django.core import serializers
from django.core.management.base import BaseCommand, CommandError
from django.core.management.utils import parse_apps_and_model_labels
from django.db import DEFAULT_DB_ALIAS

from ...base import ComplexModel


class MultiplesCodigosError(CommandError):
    def __init__(self, codigo, tabla):
        super().__init__('El código \'{codigo}\' está repetido en la tabla {tabla}'.format(
            codigo=codigo,
            tabla=tabla.upper()))


class NoCoincidenClaveDelCodigoError(CommandError):
    def __init__(self, codigo, tabla, columna_clave, clave_existente, clave_nuevo):
        super().__init__('El registro con código \'{codigo}\' de la tabla {tabla}'
                         ' tiene la columna \'{columna_clave}\' con el valor \'{clave_existente}\' en la base de datos'
                         ' pero en el fixture se encontró el valor \'{clave_nuevo}\''.format(
                             codigo=codigo,
                             tabla=tabla.upper(),
                             columna_clave=columna_clave,
                             clave_existente=clave_existente,
                             clave_nuevo=clave_nuevo))


class SinClaveNiCodigoError(CommandError):
    def __init__(self, fixture):
        super().__init__('Se encontró un objeto sin una clave primaria ni código en el fixture {fixture}'.format(
            fixture=fixture))


class SinClaveError(CommandError):
    def __init__(self, fixture):
        super().__init__('Se encontró un objeto sin clave primaria en el fixture {fixture}'.format(
            fixture=fixture))


class FixtureNotExistsError(CommandError):
    def __init__(self, fixture_path):
        super().__init__('El fixture \'{fixture_path}\' no existe.'.format(
            fixture_path=fixture_path))


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'labels', nargs='*',
            help='Lista de etiqueta de aplicaciones o modelos (formato: app_label o app_label.ModelName).')
        parser.add_argument(
            '--database', default=DEFAULT_DB_ALIAS,
            help='Especifica la base de datos en la que se carga los constantes. Por defecto, es la base de datos "default".',
        )
        parser.add_argument(
            '-e', '--exclude', action='append', default=[],
            help='La aplicación (app_label) o el modelo (app_label.ModelName) a excluir. Esta opción puede ser utilizado varias veces.',
        )

    def handle(self, *args, **kwargs):
        # Carga los parámetros del comando
        models, apps = parse_apps_and_model_labels(kwargs['labels'])
        using = kwargs['database']
        excluded_models, excluded_apps = parse_apps_and_model_labels(
            kwargs['exclude'])

        # Obtiene la lista de los modelos a actualizar
        modelset = self.modelos_filtrados(
            models, apps, excluded_models, excluded_apps)

        # Obtiene la lista de los modelos a actualizar
        for model in modelset:
            if issubclass(model, ComplexModel):
                self.actualizar_fixtures(model, using)

    def actualizar_fixtures(self, model, using):
        fixture_path = model.fixture

        # Si el modelo tiene especificado un fixture
        if fixture_path:
            # Si el fixture no existe
            if not os.path.exists(fixture_path):
                raise FixtureNotExistsError(fixture_path)

            print("Cargando el fixture {fixture_path}".format(
                fixture_path=fixture_path))

            # Deserializa los objetos del fixture
            fixture = open(fixture_path, "r")
            objects = serializers.deserialize(
                "json", fixture, using=using, ignorenonexistent=True,
                handle_forward_references=True,
            )

            instancias_actualizadas = 0
            instancias_creadas = 0
            # Para cada objeto deserializado
            for obj in objects:
                # Si el objeto del fixture no tiene ni codigo ni la clave primaria
                if obj.object.codigo is None and obj.object.pk is None:
                    raise SinClaveNiCodigoError(fixture_path)
                elif obj.object.pk is None:
                    raise SinClaveError(fixture_path)
                # Si el objeto solo tiene la clave primaria
                elif obj.object.codigo is None:
                    obj.save()
                else:
                    # Busca objeto con el código 'codigo' en la base de datos
                    queryset = model.objects.filter(codigo=obj.object.codigo)

                    # Si no existe el valor en la columna 'codigo' en la base de datos
                    if queryset.count() == 0:
                        # Se crea una nueva instancia
                        obj.save()
                        instancias_creadas += 1
                    # Si existe un único valor en la columna 'codigo' en la base de datos
                    elif queryset.count() == 1:
                        # Si las claves primarias coinciden, actualiza la instancia.
                        if obj.object.pk is None:
                            obj.object.pk = queryset.first().pk
                        if obj.object.pk == queryset.first().pk:
                            obj.save()
                            instancias_actualizadas += 1
                        else:
                            raise NoCoincidenClaveDelCodigoError(
                                obj.object.codigo,
                                model._meta.db_table,
                                model._meta.pk.column,
                                queryset.first().id,
                                obj.object.id)
                    # Si existe multiples filas con el valor repetidos en la columna 'codigo' en la base de datos
                    else:
                        raise MultiplesCodigosError(
                            obj.object.codigo, model._meta.db_table)

            print("    Se han cargado {instancias_total} instancias de {nombre_modelo} (nuevos: {instancias_creadas}, actualizados: {instancias_actualizadas})".format(
                nombre_modelo=model.__name__,
                instancias_total=instancias_creadas + instancias_actualizadas,
                instancias_creadas=instancias_creadas,
                instancias_actualizadas=instancias_actualizadas
            ))

    def modelos_filtrados(self, models, apps, excluded_models, excluded_apps):
        modelset = set()

        if models or apps:
            # Carga los modelos de la lista 'models'
            modelset.update(models)

            # Carga todos los modelos de las aplicaciones de 'apps'
            for app in apps:
                for model in app.get_models():
                    modelset.add(model)
        else:
            # Carga todos los modelos de todas las aplicaciones
            modelset.update(django.apps.apps.get_models())

        # Filtra por lista de modelos 'excluded_models'
        for excluded_model in excluded_models:
            if excluded_model in modelset:
                modelset.remove(excluded_model)

        # Filtra todos los modelos de la lista de aplicaciones 'excluded_apps'
        for excluded_app in excluded_apps:
            for excluded_model in excluded_app.get_models():
                if excluded_model in modelset:
                    modelset.remove(excluded_model)

        return modelset
