import datetime as dt
from django.utils import timezone
from .tools.classes import tools_classes_import_from_str as t_import
from ..models import CronJobCab, CronJob, CronJobLog as Clog, CronJobLogError as Clogerr
from .cronjobsf.pathjobs import PJOBS
from .cronjobsf.baseclass import Crontab
from .errors import Error

# Hacer lo siguiente
# crontab -e
# */1 * * * * /home/thotenn/www/mg/kernel/shell/cron.sh
# dejar un espacio al final del archivo crontab -e
# systemctl restart cron
# Para visualizar las tareas:
# journalctl -u cron


class CronJobsController:
    # TODO: ahora mismo solo ejecuta tarea por horas, configurar mejor para que acepte a todo tipo de horarios
    @staticmethod
    def start_all(fh: dt):
        """
        Obs:
        Para ejecutar archivos: exec(open('apps/system/controllers/test.py').read())
        O tambien podria ser:
            from subprocess import call
            call(["python","apps/system/controllers/test.py"])
        """
        cabs_arr: list = list(CronJobCab.objects.filter(activo=True).values_list('pk', flat=True))
        jobs = CronJob.objects.filter(cab__pk__in=cabs_arr,
                                      activo=True,
                                      hora=str(fh.hour)
                                      ).select_related('cab')

        # Aqui obtendremos tareas que ya se ejecutaron en este horario
        logs_executed = list(Clog.objects.filter(dtinicio__hour=fh.hour,
                                            dtinicio__day=fh.day,
                                            dtinicio__month=fh.month,
                                            dtinicio__year=fh.year).values_list('job__pk', flat=True)
                             )
        # logs_executed = []  # BORRAR
        for job in jobs:
            if job.pk not in logs_executed:
                if job.hora == str(fh.hour):
                    if job.controllerpath in PJOBS:
                        if 'class' in PJOBS[job.controllerpath]:
                            classpath = PJOBS[job.controllerpath]['class']
                        else:
                            classpath = t_import(PJOBS[job.controllerpath]['class_dir'], '_')().__class__

                        if issubclass(classpath, Crontab):
                            log_in_exec = Clog()
                            try:
                                log_in_exec.job = job
                                log_in_exec.estado = 'EE'
                                log_in_exec.dtinicio = timezone.now()
                                classpath.start(hour=fh.hour)  # AQUI EJECUTAMOS LA CLASE super(CRONTAB)
                                log_in_exec.estado = 'EC'
                            except Exception as err:
                                err_log = Error.send('apps.core.controllers.cronjob.CronJobsController.start_all',
                                           'log_error', 'ad_co_cj_cj', 'E', str(err))
                                log_in_exec.estado = 'EI'
                                Clogerr.objects.create(
                                    log=log_in_exec,
                                    error=err_log
                                )
                            finally:
                                log_in_exec.dtfin = timezone.now()
                                log_in_exec.save()

    @staticmethod
    def create_or_get_cab(viewcode: str, codigocab: str, nombrecab: str, descripcion: str = ''):
        cab = CronJobCab.objects.filter(viewcode=viewcode, valor=codigocab).last()
        if cab:
            return cab
        return CronJobCab.objects.create(viewcode=viewcode, valor=codigocab, nombre=nombrecab, descripcion=descripcion)

    @staticmethod
    def create_or_upd_per_hour(viewcode: str, codigocab: str, nombrecab: str, controllercode: str,
                        hora: str = '*', nombrejob: str = '', descripcioncab: str = None) -> CronJob:
        try:
            cab = CronJobsController.create_or_get_cab(viewcode=viewcode, codigocab=codigocab, nombrecab=nombrecab,
                                                       descripcion=descripcioncab)
            det = CronJob.objects.filter(cab=cab, controllerpath=controllercode, min='0', hora=hora).last()
            if det:
                return det
            return CronJob.objects.create(cab=cab, controllerpath=controllercode, min='0', hora=hora, activo=True,
                                          nombre=nombrejob)
        except Exception as err:
            Error.send('apps.system.controllers.cronjob.CronJobsController.create_or_upd_per_hour',
                       'create_or_upd_per_hour_error', 'rh_sy_cj_cj', 'E', str(err))
            print(err)
