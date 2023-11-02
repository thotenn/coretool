import os
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Cambiar el nombre del Proyecto'

    def add_arguments(self, parser):
        parser.add_argument('configname', type=str, nargs='+',
                            help='El nombre de la configuracion o settings a aplicar, ejemplo: local')

    def handle(self, *args, **kwargs):
        configname = kwargs['configname'][0]
        try:
            cmd = "python manage.py makemigrations administrador --settings=kernel.set." + configname
            os.system(cmd)
            cmd = "python manage.py makemigrations base --settings=kernel.set." + configname
            os.system(cmd)
            cmd = "python manage.py makemigrations asistencia --settings=kernel.set." + configname
            os.system(cmd)
            cmd = "python manage.py makemigrations cargos --settings=kernel.set." + configname
            os.system(cmd)
            cmd = "python manage.py makemigrations funcionarios --settings=kernel.set." + configname
            os.system(cmd)
            cmd = "python manage.py makemigrations postulantes --settings=kernel.set." + configname
            os.system(cmd)
            cmd = "python manage.py makemigrations salarios --settings=kernel.set." + configname
            os.system(cmd)
            cmd = "python manage.py makemigrations inventario --settings=kernel.set." + configname
            os.system(cmd)
            cmd = "python manage.py makemigrations ventas --settings=kernel.set." + configname
            os.system(cmd)
            cmd = "python manage.py migrate --settings=kernel.set." + configname
            os.system(cmd)
        except Exception as err:
            raise CommandError('Error. "%s"' % err)




