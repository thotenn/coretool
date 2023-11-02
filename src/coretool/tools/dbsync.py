from django.apps import apps
# from django.contrib import admin
# from django.contrib.admin.sites import AlreadyRegistered
from django.db import IntegrityError, models

from django.contrib.auth.models import User


from django.core.management.base import BaseCommand, CommandError

LISTA_APPS = [
    # 'admin',
    # 'auth',
    # 'sessions',
    # 'system',
    # 'administrador',
    'base',
    # 'asistencia',
    # 'cargos',
    # 'salarios',
    # 'funcionarios',
]

HISTORICAL_PREFIJO = 'Historical'

USER_DEFAULT = User.objects.first()

OMITIR_COLS = [
    'id',
    'createdat',
    'updatedat',
    'eliminado',
    'createdby',
    'updatedby',
    'deleted',
]


def get_data_model_bd_set(row_model_db2, str_bd_name: str):
    """
    se supone que aqui se comprobara que los datos fk de la fila proveniente de una tabla en la bd2 tambien ya este en
    la bd1
    """
    MODEL = row_model_db2.__class__
    fieldsmodel = [i.name for i in MODEL._meta.fields if i.name not in OMITIR_COLS]



class Command(BaseCommand):
    help = ('Copia los datos de una bd a otra.')

    def add_arguments(self, parser):
        pass
        # parser.add_argument('relojid', type=str, nargs='+',
        #                     help='Reloj ID')

    def handle(self, *args, **kwargs):
        # TODO: Agregar en una lista los modelos que tuvieron errores y cuando una clase posterior tenga referencia a
        #  ese modelo con error, tener mejor cuidado con los datos
        # TODO: Verificar que no exista contraints repetidos
        # TODO: Verificar que los pks no se repitan
        try:
            db_2 = 'dev'

            for appname in LISTA_APPS:
                print('Trabajando en la aplicacion ', appname)
                app_models = apps.get_app_config(appname).get_models()
                MODEL: models.Model
                for MODEL in app_models:
                    if MODEL.__name__ == 'Persona':
                        # if issubclass(MODEL, CBAHistoricalRecords):
                        if 'Historical' not in MODEL.__name__:
                            if not MODEL._meta.proxy:
                                print('___________Sincronizando el modelo ', MODEL.__name__)
                                try:
                                    fieldsmodel = [i.name for i in MODEL._meta.fields]
                                    data_list = list()
                                    model_data_all = MODEL.objects.all().using(db_2)
                                    print('data all = ')
                                    print(model_data_all)
                                    print('fields models = ')
                                    print(fieldsmodel)
                                    k = 0
                                    for row in model_data_all:
                                        print(k, ' ', row)
                                        k = k + 1
                                        data_save: dict = {}
                                        for field_k in fieldsmodel:
                                            if field_k in ['createdby', 'updatedby']:
                                                data_save[field_k] = USER_DEFAULT
                                            else:
                                                data_save[field_k] = getattr(row, field_k)
                                        # if hasattr(data_save, 'createdby'):
                                        #     data_save['createdby'] = user_default
                                        # if hasattr(data_save, 'updatedby'):
                                        #     data_save['updatedby'] = user_default
                                        print(data_save)
                                        data_list.append(MODEL(**data_save))
                                    print('data list es igual a =')
                                    print(data_list)
                                    MODEL.objects.bulk_create(n for n in data_list)
                                    print('{} sincronizado totalmente.'.format(MODEL.__name__))
                                except Exception as err:
                                    print('ERROR')
                                    print(err)

                                # print(MODEL.objects.all())
                                # print(MODEL._meta.db_table)
                        # data_model = MODEL.objects.all()
                        # data_model
        except Exception as err:
            print(err)
            raise CommandError('Error')
        self.stdout.write(self.style.SUCCESS('Exito'))

