from django.db import models
from ..base import BaseModel, ComplexModel
from ..controllers.pstruct import pstruct_get_full_tuple as pstruct_full


class ErrorEsperado(ComplexModel):
    class Meta:
        db_table = 'admin_errors'
        managed = True
        verbose_name = 'Error Esperado'
        verbose_name_plural = 'Errores Esperados'
        ordering = ['valor']
    TIPOERROR = [
        ('E', 'Error Esperado'),
        ('NE', 'Error no Esperado')
    ]
    VIEWSCODES = pstruct_full()
    tipoerror = models.CharField('Tipo de error', max_length=2, null=False, blank=False, choices=TIPOERROR)
    viewcode = models.CharField('Codigo de View', max_length=50, null=False, blank=False, choices=VIEWSCODES)
    solucion = models.TextField('Detalle de Solucion', null=True, blank=True)
    nombre = models.CharField('Nombre', null=True, blank=True, max_length=200, default='')
    valor = models.CharField('Valor', null=False, blank=False, max_length=250, default='')

    def __str__(self):
        return (self.nombre or 'Not named') + ', tipo: ' + (self.tipoerror or 'NE')


class ErrorLog(BaseModel):
    class Meta:
        db_table = 'admin_errors_logs'
        managed = True
        verbose_name = 'Error Log'
        verbose_name_plural = 'Error Logs'
        ordering = ['-createdat']
    VIEWSCODES = pstruct_full()
    TIPOSSTR = [
        ('json', 'JSON'),
        ('str', 'String'),
        ('file', 'Archivo'),
        ('other', 'Otro')
    ]
    viewcode = models.CharField('Codigo de View', max_length=50, null=False, blank=False, choices=VIEWSCODES)
    erroresperado = models.ForeignKey(ErrorEsperado, on_delete=models.PROTECT, null=True, blank=True,
                                      verbose_name='Error Esperado')
    pathfunction = models.CharField('Path', max_length=300, null=False, blank=False)
    tipocaptura = models.CharField('Tipo de captura', max_length=35, null=False, blank=False, choices=TIPOSSTR)
    catchstr = models.TextField('Catch', null=True, blank=True)

    def __str__(self):
        return str(self.createdat) + ', view: ' + self.viewcode + ', Error: ' + self.erroresperado.__str__()
