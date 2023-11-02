from django.contrib import admin

# ERRORES
from .models.errors import ErrorEsperado, ErrorLog
from .admins.errors import ErrorEsperadoAdmin, ErrorLogAdmin

# CRONJOBS
from .models.cronjobs import CronJobCab, CronJob, CronJobLog, CronJobLogError
from .admins.cronjobs import CronJobCabAdmin, CronJobAdmin, CronJobLogAdmin, CronJobLogErrorAdmin


###


# ERRORES
admin.site.register(ErrorEsperado, ErrorEsperadoAdmin)
admin.site.register(ErrorLog, ErrorLogAdmin)

# CRONJOBS
admin.site.register(CronJobCab, CronJobCabAdmin)
admin.site.register(CronJob, CronJobAdmin)
admin.site.register(CronJobLog, CronJobLogAdmin)
admin.site.register(CronJobLogError, CronJobLogErrorAdmin)