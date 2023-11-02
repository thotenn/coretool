from ..base import BaseModelAdmin, BaseLogModelAdmin, BaseLogTabModelAdmin
from ..models import ErrorEsperado, ErrorLog


class ErrorLogInline(BaseLogTabModelAdmin):
    model = ErrorLog
    fields = ['createdat', 'erroresperado', 'pathfunction', 'tipocaptura', 'catchstr']


class ErrorEsperadoAdmin(BaseModelAdmin):
    class Meta:
        model = ErrorEsperado
    inlines = [ErrorLogInline]
    list_per_page = 15
    list_display = ['tipoerror', 'viewcode', 'valor']
    fieldsets = (
        (None, {
            'classes': ('wide'),
            'fields': ('tipoerror', 'viewcode', 'valor', 'nombre', 'descripcion', 'solucion')
        }),
    )


class ErrorLogAdmin(BaseLogModelAdmin):
    class Meta:
        model = ErrorLog
    list_per_page = 15
    fields = ['viewcode', 'erroresperado', 'pathfunction', 'tipocaptura', 'catchstr']
    list_display = ['createdat', 'viewcode', 'erroresperado', 'pathfunction', 'tipocaptura', 'catchstr']
    ordering = ['-createdat']
