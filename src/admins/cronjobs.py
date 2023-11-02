from ..base import BaseModelAdmin, BaseLogModelAdmin
from ..models.cronjobs import CronJobCab, CronJob, CronJobLog, CronJobLogError




class CronJobCabAdmin(BaseModelAdmin):
    class Meta:
        model = CronJobCab
    list_per_page = 15
    list_display = ['nombre', 'viewcode', 'activo', 'descripcion']


class CronJobAdmin(BaseModelAdmin):
    class Meta:
        model = CronJob
    list_per_page = 15
    list_display = ['cab', 'controllerpath', 'get_timecron', 'activo']
    fieldsets = (
        (None, {
            'classes': ('wide'),
            'fields': ('cab', 'nombre', 'controllerpath', 'activo', 'jobhash', 'min', 'hora', 'diames', 'mes', 'diasemana')
        }),
        ('Propiedades', {
            'classes': ('wide'),
            'fields': ('codigo', 'maxminthread', 'modificable', 'jsonvars', 'descripcion')
        }),
    )

    def get_timecron(self, obj: CronJob) -> str:
        return ('(' + obj.min + ' ' + obj.hora + ' ' + obj.diames + ' ' + obj.mes + ' ' +
                obj.diasemana + ')')


class CronJobLogAdmin(BaseLogModelAdmin):
    class Meta:
        model = CronJobLog
    list_display = ['job', 'estado', 'dtinicio', 'dtfin', 'createdby']
    fields = list_display


class CronJobLogErrorAdmin(BaseLogModelAdmin):
    class Meta:
        model = CronJobLogError
    list_display = ['log', 'error', 'createdat']
    fields = list_display
