from django.core.management.base import BaseCommand, CommandError
from ...controllers.cronjobs import CronJobsController as Cj
import datetime as dt
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)
"""
crontab -e
systemctl restart cron
sudo chmod +x run.sh
*/1 * * * *	/.../rrhh/apps/system/controllers/cronjobsf/run.sh

# Para visualizar las tareas:
journalctl -u cron
"""


class Command(BaseCommand):
    help = 'Verifica si en este instante se pueden ejecutar las tareas programadas'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        start = dt.datetime.now()
        try:
            logger.debug('Inicio Cron')
            Cj.start_all(dt.datetime.now())
            fin = dt.datetime.now()
            logger.info('Fin cron: ' + str(fin-start))
        except Exception as e:
            logger.exception(e)
            raise CommandError('No se han podido ejecutar todas las tareas programadas.')
