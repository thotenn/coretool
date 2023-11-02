
# from django.db.models.deletion import Collector
# from .controllers.addedbyuser.request import get_current_user

from django import forms
from django.contrib.admin.views.main import ChangeList
from django.db import IntegrityError, models
from django.conf import settings

from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE
from safedelete.managers import SafeDeleteManager
from safedelete.queryset import SafeDeleteQueryset

###

from django.contrib import admin, messages
from django.http import HttpResponseRedirect

from .controllers.addedbyuser.fields import UserForeignKey

# libs para ComplexModel
from .checks.complexmodelcheck import check_database_table, check_fixture
from .fields import ReservableAutoField

###
# Models
###

"""
    PARA LOS MODELOS CON API, DEBERAN TENER LA VARIABLE apiname: str
    CON EL NOMBRE DE LA BASE PARA LA COMPOSICION DE SU URL 
"""

class THBQuerySet(SafeDeleteQueryset): # models.Model (safedelete)
    pass
    # def delete(self):
    #     for o in self:
    #         collector = Collector(using='default')
    #         collector.collect([o])
    #         if collector.dependencies:
    #             raise Exception('No se puede eliminar el registro. Existen asociaciones dependientes')
    #         o.eliminado = True
    #         o.save()


class THBModelManager(SafeDeleteManager):  # models.Manager (safedelete)
    _queryset_class = THBQuerySet # safedelete
    def get_queryset(self):
        queryset = super().get_queryset() # savedelete
        return queryset  # savedelete
        # # print(user._wrapped.__dict__)
        # try:
        #     val = settings.SHOW_DELETE_COL
        # except:
        #     val = False
        # if val:
        #     if get_current_user().is_superuser:
        #         return THBQuerySet(self.model, using=self._db)
        # return THBQuerySet(self.model, using=self._db).filter(eliminado=False)


class BasicModelManager(THBModelManager):
    _queryset_class = THBQuerySet

    def get_queryset(self):
        return super().get_queryset().order_by('nombre')


class ComplexModelManager(BasicModelManager):
    pass


class AdminManager(models.Manager):
    pass


class BaseModel(SafeDeleteModel):  # class BaseModel(models.Model)  (safedelete)
    class Meta:
        abstract = True

    id = models.AutoField(primary_key=True)
    createdby = UserForeignKey(auto_user_add=True, verbose_name="CreatedBy", null=False, editable=False)
    updatedby = UserForeignKey(auto_user=True, verbose_name="UpdatedBy", null=False, editable=False, related_name="%(app_label)s_%(class)s_updatedby")
    createdat = models.DateTimeField('Creado', auto_now_add=True, editable=False, null=True)
    updatedat = models.DateTimeField('Actualizado', auto_now=True, editable=False, null=True)
    lock = models.DateTimeField('Lock', editable=False, null=True, blank=True)
    #eliminado = models.BooleanField('Eliminado', editable=False, null=False, blank=False, default=False, db_index=True)
    objects = THBModelManager()
    admin_objects = AdminManager()
    _safedelete_policy = SOFT_DELETE_CASCADE  # (safedelete)

    # API SECTION
    api_url_name = ''
    api_fields = '__all__'
    # /API SECTION

    """
    def save(self, *args, **kwargs):
       try:
           if self.lock is not None:
               super().save(args, kwargs)
           else:
               raise forms.ValidationError('El formulario ha sido bloqueado para su edicion')
       except Exception as e:
           print('Error al guardar')
           print(e)
           print('...___...')
           raise forms.ValidationError('El registro ya existe')
    """
    # def delete(self, *args, **kwargs):
    #     collector = Collector(using='default')
    #     collector.collect([self])
    #     # dependencies should be an empty dict if the item is not related to anything
    #     if not collector.dependencies:
    #         self.eliminado = True
    #         self.save()
    #     else:
    #         raise forms.ValidationError('No se puede eliminar el registro. Existen asociaciones dependientes')


class BasicModel(BaseModel):
    class Meta:
        abstract = True

    nombre = models.CharField('Nombre', null=False, blank=False, max_length=200, default='')
    descripcion = models.TextField('Descripcion', null=True, blank=True)


class ComplexModel(BasicModel):
    """
        Modelo abstracto referenciable por código que mantiene
        los constantes del sistema en la base de datos.

        Reserva un bloque de 'id' que incia desde 0 hasta
        'initial_value', especificado en el ReservableAutoField
        (por defecto, el valor es SEQUENCE_DEFAULT_INITIAL_VALUE).
        Véase la documentación del 'ReservableAutoField' para más
        detalle.

        Los constantes del sistema son especificados a través de
        los fixtures. El fixture relacionado se especifica a
        través del atributo 'fixture' y contiene la ruta relativa
        al fixture (generalmente a un archivo JSON). Estos fixtures
        deben especificar la clave primaria 'pk' por cada objeto.

        Los constantes del sistema pueden ser cargados a través
        del comando 'updatecomplex' de la siguiente manera:

            python manage.py updatecomplex --settings=cbarh.settings.tu_settings


        Las verificaciones de la consistencia de los valores entre
        el fixture y la base de datos son comparados durante el
        arranque de django. En caso de encontrar un discrepancias,
        lanza un WARNING en la consola.
        """
    class Meta:
        abstract = True

    id = ReservableAutoField(primary_key=True)
    codigo = models.CharField('Código', null=True, blank=True, max_length=250)
    modificable = models.BooleanField('Modificable', null=False, blank=False, default=True)

    objects = ComplexModelManager()

    fixture = ''

    def save(self, *args, **kwargs):
        # Si en la base de datos existe el registro y está
        # como no modificable, lanzar una excepción.
        try:
            obj = self._meta.model.objects.get(id=self.id)
            if not obj.modificable:
                raise ComplexModel.InstanciaNoModificableException()
        except self._meta.model.DoesNotExist:
            pass

        super().save(*args, **kwargs)

    def delete(self, force_policy=None, **kwargs):
    # def delete(self, *args, **kwargs):
        try:
            obj = self._meta.model.objects.get(id=self.id)
            if not obj.modificable:
                raise ComplexModel.InstanciaNoModificableException()
            # obj.delete()
            super(ComplexModel, self).delete(force_policy, **kwargs)
        except self._meta.model.DoesNotExist:
            pass

    # SOLUCIONAR ESTO DE AQUI
    # @classmethod
    # def check(cls, **kwargs):
    #     # Reinicializa la secuencia de la columna 'id' de la tabla
    #     # si el valor de la secuencia se encuentra por debajo del
    #     # valor 'initial_value' especificado en el ReservableAutoField.
    #     # (Nota: Esto no es una verificación sino es una corrección)
    #     cls._meta.pk.corregir_secuencia()
    #
    #     errors = super().check(**kwargs)
    #
    #     # Si el atributo _fixture está cargado y no es un modelo proxy
    #     if cls.fixture and not cls._meta.proxy:
    #         # Verificar si la base de datos es consistente con el modelo
    #         # antes de comparar con los datos del fixture.
    #         db_table_errors = check_database_table(cls, **kwargs)
    #         if len(db_table_errors) == 0:
    #             # Ejecutar la comprobación entre el fixture y la base de datos
    #             errors += check_fixture(cls, **kwargs)
    #         else:
    #             errors += db_table_errors
    #
    #     return errors

    class InstanciaNoModificableException(Exception):
        def __init__(self):
            super().__init__('El registro no puede modificarse ni eliminarse.')

    class ComplexConstant(object):
        """
        Encapsula y retorna una instancia del modelo
        cuando es accedido. La instancia del modelo
        retornado es la instancia que posee el mismo
        valor en el campo 'codigo'.

        Modo de uso:

            # Las constantes de definen de la siguiente manera:
            class ModeloXManager(ComplexManager):
                CONSTANTE_A = ComplexModel.ComplexConstant('codigo_a')
                CONSTANTE_B = ComplexModel.ComplexConstant('codigo_b')

            class ModeloX(ComplexModel):
                objects = ModeloXManager()

            # Las constantes se acceden de la siguiente manera:
            # (la variable 'instancia' es una instancia del 'ModeloX')
            instancia = ModeloX.objects.INSTANCIA_A
        """

        def __init__(self, codigo):
            self._codigo = codigo
            self._model_instance = None

        def __get__(self, instance, owner):
            if self._model_instance is None:
                self._model_instance = instance.get(codigo=self._codigo)
            return self._model_instance

###
# Admin
###


class BaseModelAdmin(admin.ModelAdmin):
    # def save_model(self, request, obj, form, change):
    #     try:
    #         if self.lock is not None:
    #             obj.save()
    #         else:
    #             raise forms.ValidationError('El formulario ha sido bloqueado para su edicion')
    #     except Exception as e:
    #         raise forms.ValidationError(e)

    def get_queryset(self, request):
        qs = super(BaseModelAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(deleted__isnull=True)

    #Vista para confirmación de borrado. Se verifica si existen relaciones
    def delete_view(self, request, object_id, extra_context=None):
        try:
            return super().delete_view(request, object_id)
        except Exception as exc:
            messages.add_message(request, messages.ERROR, exc)
            return HttpResponseRedirect(request.path)

    def changelist_view(self, request, extra_context=None):
        try:
            return super().changelist_view(request)
        except Exception as exc:
            messages.add_message(request, messages.ERROR, exc)
            return HttpResponseRedirect(request.path)

    def add_view(self, request, form_url='', extra_context=None):
        try:
            return super().add_view(request)
        except Exception as exc:
            messages.add_message(request, messages.ERROR, exc)
            return HttpResponseRedirect(request.path)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        try:
            return super().change_view(request, object_id, form_url='', extra_context=None)
        except Exception as exc:
            messages.add_message(request, messages.ERROR, exc)
            return HttpResponseRedirect(request.path)

    def get_readonly_fields(self, request, obj=None):
        # Lo siguiente comentado es para que el superusuario si pueda editar los campos
        #  normalmente accesibles, los readonly se mantienen
        # if request.user.is_superuser:
        #     return self.readonly_fields
        if obj is not None:
            if obj.lock:
                return list(set(
                    [field.name for field in self.opts.local_fields] +
                    [field.name for field in self.opts.local_many_to_many]
                ))
                # return 'alumno', 'fechapago', 'montopagado', 'descuento', 'montototal', 'pendiente', 'justificado'
            else:
                return super(BaseModelAdmin, self).get_readonly_fields(request, obj)
        else:
            return super(BaseModelAdmin, self).get_readonly_fields(request, obj)

    def get_changelist_instance(self, request):
        """
        Return a `ChangeList` instance based on `request`. May raise
        `IncorrectLookupParameters`.
        """
        list_display = self.get_list_display(request)
        try:
            ADMIN_SHOW_COLS = settings.ADMIN_SHOW_COLS
        except:
            ADMIN_SHOW_COLS = None
        if request.user.is_superuser:
            if ADMIN_SHOW_COLS is not None:
                res = list()
                trespuntos = False
                for item in ADMIN_SHOW_COLS:
                    if item == '...':
                        trespuntos = True
                        res.extend(list_display)
                    else:
                        res.append(item)
                if trespuntos is False:
                    res.extend(list_display)
                list_display = res
        else:
            if ADMIN_SHOW_COLS is not None:
                if '...' in ADMIN_SHOW_COLS:
                    ADMIN_SHOW_COLS.remove('...')
                for item in ADMIN_SHOW_COLS:
                    if item in list_display:
                        list_display.remove(item)
        list_display_links = self.get_list_display_links(request, list_display)
        if self.get_actions(request):
            list_display = ['action_checkbox', *list_display]
        sortable_by = self.get_sortable_by(request)
        change_list = self.get_changelist(request)
        return ChangeList(
            request,
            self.model,
            list_display,
            list_display_links,
            self.get_list_filter(request),
            self.date_hierarchy,
            self.get_search_fields(request),
            self.get_list_select_related(request),
            self.list_per_page,
            self.list_max_show_all,
            self.list_editable,
            self,
            sortable_by,
            change_list
        )

    def delete_model(self, request, obj):
        if obj.lock:
            raise forms.ValidationError('No se puede eliminar el registro, ya que esta bloqueado por otra entidad.')
        super(BaseModelAdmin, self).delete_model(request, obj)


class BaseLogModelAdmin(BaseModelAdmin):
    actions = None

    # def get_model_perms(self, request):
    #     return {}

    def has_add_permission(self, request, obj=None):
        return False

    def has_edit_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def has_delete_permission(self, request, obj=None):
        return False

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        try:
            extra_context = extra_context or {}
            extra_context['show_save_and_continue'] = False
            extra_context['show_save'] = False
            return super(BaseLogModelAdmin, self).changeform_view(request, object_id, form_url='', extra_context=extra_context)
            # return super().change_view(request, object_id, form_url='', extra_context=None)
        except Exception as exc:
            messages.add_message(request, messages.ERROR, exc)
            return HttpResponseRedirect(request.path)


class BaseLogTabModelAdmin(admin.TabularInline):
    extra = 0

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_edit_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]
