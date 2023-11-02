import os
import subprocess
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
# from kernel.set.server import DB_HOST, DATABASES, DB_DEFAULT_NAME, DROPBOX_PARAMETERS


class Command(BaseCommand):
    help = 'Crea un backup de la bd default y lo sube a dropbox'

    def handle(self, *args, **kwargs):
        DB_HOST = kwargs.get("DB_HOST")
        DATABASES = kwargs.get("DATABASES")
        DB_DEFAULT_NAME = kwargs.get("DB_DEFAULT_NAME")
        DROPBOX_PARAMETERS = kwargs.get("DROPBOX_PARAMETERS")
        current_date = datetime.now().strftime("%y%m%dTh%Hm%M")
        dir_folder_tmp = "/tmp/"
        file_name = "thb_admin_{date}.backup".format(date=current_date)
        try:
            # PGPASS = "PGPASSWORD=\"{password}\"".format(password=DATABASES[DB_DEFAULT_NAME]["PASSWORD"])
            # print(PGPASS)
            # os.system(PGPASS)
            print('Generando el backup')
            bashCommand = 'PGPASSWORD="{password}" pg_dump -U {user} -h {host} {name} > {dir_folder_tmp}{file_name}'.format(
                password=DATABASES[DB_DEFAULT_NAME]["PASSWORD"],
                user=DATABASES[DB_DEFAULT_NAME]["USER"],
                host=DB_HOST,
                name=DATABASES[DB_DEFAULT_NAME]["NAME"],
                dir_folder_tmp=dir_folder_tmp,
                file_name=file_name
            )
            os.system(bashCommand)
            # process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
            print('Backup generado.')
            print('Uploading to external server')
            bashCommand = "curl -X POST https://content.dropboxapi.com/2/files/upload" + \
                " --header \"Authorization: Bearer {API_KEY} \"".format(
                    API_KEY=DROPBOX_PARAMETERS['API_KEY']
                ) + \
                " --header \"Dropbox-API-Arg: {\\\"path\\\": \\\"" + DROPBOX_PARAMETERS["FOLDER_DIR"] + file_name + \
                "\\\",\\\"mode\\\": \\\"add\\\",\\\"autorename\\\": true,\\\"mute\\\": false,\\\"strict_conflict\\\": false}\"" + \
                " --header \"Content-Type: application/octet-stream\"" + \
                " --data-binary @{dir_folder_tmp}{file_name}".format(
                    dir_folder_tmp=dir_folder_tmp,
                    file_name=file_name
                )
            print(bashCommand)
            results = subprocess.run(
                bashCommand, shell=True, universal_newlines=True, check=True)
            print(results.stdout)
            print("Removiendo archivo temporal.")
            os.system(f"rm {dir_folder_tmp}{file_name}".format(dir_folder_tmp=dir_folder_tmp, file_name=file_name))

            # process_dropbox_upload = subprocess.Popen(bashCommand, stdout=subprocess.PIPE)
            # output, error = process_dropbox_upload.communicate()
            print('Successfully upload.')
        except Exception as exc:
            print("Error, removiendo archivo temporal.")
            os.system(f"rm {dir_folder_tmp}{file_name}".format(dir_folder_tmp=dir_folder_tmp, file_name=file_name))
            raise CommandError('Error: "%s"' % exc)
