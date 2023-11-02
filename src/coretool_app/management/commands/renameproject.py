import os
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Cambiar el nombre del Proyecto'

    def add_arguments(self, parser):
        parser.add_argument('current', type=str, nargs='+',
                            help='El actual nombre de la carpeta de proyecto Django')
        parser.add_argument('new', type=str, nargs='+',
                            help='El nuevo nombre del proyecto')

    def handle(self, *args, **kwargs):
        current_project_name = kwargs['current'][0]
        new_project_name = kwargs['new'][0]

        # logic for renaming the files

        files_to_rename = [f'{current_project_name}/settings/base.py',
                           f'{current_project_name}/wsgi.py', 'manage.py',
                           f'{current_project_name}/asgi.py']

        for f in files_to_rename:
            try:
                with open(f, 'r') as file:
                    filedata = file.read()

                filedata = filedata.replace(current_project_name, new_project_name)

                with open(f, 'w') as file:
                    file.write(filedata)
            except Exception as exc:
                raise CommandError('Error, no se encuentran los archivos. "%s"' % exc)

        os.rename(current_project_name, new_project_name)

        self.stdout.write(self.style.SUCCESS(
            'El nombre del proyecto ha cambiado por %s' % new_project_name))
