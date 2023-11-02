from django.db import models
from ..base import BaseModel, ComplexModel
from ..controllers.pstruct import pstruct_get_full_tuple as pstruct_full
from ..controllers.cronjobsf.pathjobs import PJOBS

from .errors import ErrorLog


class CronJobCab(ComplexModel):
    class Meta:
        db_table = 'admin_cron_jobs_cab'
        managed = True
        verbose_name = 'CronJob Cab'
        verbose_name_plural = 'CronJob Cabs'
        ordering = ['createdat']
    VIEWSCODES = pstruct_full()
    viewcode = models.CharField('Codigo de View', max_length=50, null=False, blank=False, choices=VIEWSCODES)
    activo = models.BooleanField('Activo', default=True, null=False, blank=False)

    def __str__(self):
        return str(self.nombre)


class CronJob(ComplexModel):
    class Meta:
        db_table = 'admin_cron_jobs'
        managed = True
        verbose_name = 'CronJob'
        verbose_name_plural = 'CronJobs'
        ordering = ['activo', 'codigo']
    PJOBS_LIST = [(item, PJOBS[item]['title']) for item in PJOBS.keys()]
    cab = models.ForeignKey(CronJobCab, on_delete=models.PROTECT, null=False, blank=False, verbose_name='Cabecera')
    controllerpath = models.CharField('Codigo del Controlador', null=False, blank=False, max_length=450,
                                      choices=PJOBS_LIST)
    jsonvars = models.TextField('JSON Vars', null=True, blank=True)
    jobhash = models.CharField('Hash', null=True, blank=True, max_length=450)
    min = models.CharField('Minuto', null=False, blank=False, max_length=10, default='*')
    hora = models.CharField('Hora', null=False, blank=False, max_length=10, default='*')
    diames = models.CharField('Dia del mes', null=False, blank=False, max_length=10, default='*')
    mes = models.CharField('Mes', null=False, blank=False, max_length=10, default='*')
    diasemana = models.CharField('Dia de la semana', null=False, blank=False, max_length=10, default='*')
    maxminthread = models.IntegerField('Max. tiempo de ejecucion (minutos)', null=True, blank=True, default=10)
    activo = models.BooleanField('Activo', null=False, blank=False, default=True)

    def __str__(self):
        return str(self.nombre) + ', (' + self.min + ' ' + self.hora + ' ' + self.diames + ' ' + self.mes + ' ' +\
               self.diasemana + ')'


class CronJobLog(BaseModel):
    class Meta:
        db_table = 'admin_cron_logs'
        managed = True
        verbose_name = 'CronJob Log'
        verbose_name_plural = 'CronJob Logs'
        ordering = ['createdat']
    ESTADOS = [
        ('EE', 'En Ejecucion'),
        ('EC', 'Ejecutado Correctamente'),
        ('EI', 'Ejecutado Incorrectamente'),
        ('NE', 'No Ejecutado')
    ]
    job = models.ForeignKey(CronJob, on_delete=models.PROTECT, verbose_name='Job', null=False, blank=False, editable=False)
    estado = models.CharField('Estado', max_length=2, null=False, blank=False, editable=False)
    dtinicio = models.DateTimeField('Fecha/Hora inicio', null=True, blank=True, editable=False)
    dtfin = models.DateTimeField('Fecha/Hora fin', null=True, blank=True, editable=False)

    def __str__(self):
        return self.job.__str__() + ', state: ' + str(self.estado) + ', end: ' + str(self.dtfin)


class CronJobLogError(BaseModel):
    class Meta:
        db_table = 'admin_cron_logs_errors'
        managed = True
        verbose_name = 'CronJob Log Error'
        verbose_name_plural = 'CronJob Logs Errors'
        ordering = ['createdat']
    log = models.ForeignKey(CronJobLog, on_delete=models.PROTECT, verbose_name='Job Log', null=False, blank=False, editable=False)
    error = models.ForeignKey(ErrorLog, on_delete=models.PROTECT, verbose_name='Registro de error', null=True,
                              blank=True, editable=False)

    def __str__(self):
        return self.log.__str__() + ', error: ' + str(self.error.__str__())
