def set_attribute(attr, val):
    def decorated_function(func):
        setattr(func, attr, val)
        return func
    return decorated_function


def admin_descripcion(desc):
    """Decorador sobre un método personalizado
        para modificar la descripción de una
        columna/campo de la lista de ModelAdmin,
        creado por un método personalizado.

    Example:
        from django.contrib import admin
        class ClaseModelAdmin(admin.ModelAdmin):
            list_display = ['metodo_personalizado']

            @admin_descripcion("Descripcion en la cabecera")
            def metodo_personalizado(self, obj):
                ...

    Arguments:
        desc {string} -- Texto de descripción para la
            cabecera.
    """
    def inner_function(func):
        func.short_description = desc
        return func
    return inner_function


def admin_ordenarpor(clave):
    """Decorador sobre un método personalizado
        para definir el parámetro arbitrario kwarg
        de una columna/campo de la lista de ModelAdmin.

    Example:
        from django.contrib import admin
        class ClaseModelAdmin(admin.ModelAdmin):
            list_display = ['metodo_personalizado']

            def get_queryset(self, request):
                qs = super(ClaseModelAdmin, self).get_queryset(request)
                qs = qs.annotate(parametro_kwarg=F('atributos'))
                return qs

            @admin_descripcion("parametro_kwarg")
            def metodo_personalizado(self, obj):
                ...

    Arguments:
        clave {string} -- Nombre del parámetro arbitrario
    """
    def inner_function(func):
        func.admin_order_field = clave
        return func
    return inner_function
