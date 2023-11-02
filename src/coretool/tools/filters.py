# -*- coding: utf-8 -*-
# Código fuente copiado de: https://github.com/silentsokolov/django-admin-rangefilter/blob/master/rangefilter/filter.py

"""
    Filtros customizados:
        - DateRangeFilter
        - DateTimeRangeFilter
        - DateTimeLessThanFilter
        - DateTimeMoreThanFilter
    
    Ejemplo de uso:
        class Permiso(BaseModel):
            fechahorainicio = models.DateTimeField("Fecha y hora de inicio")
            fechahorafin = models.DateTimeField("Fecha y hora de fin")
            fechaaprobacion = models.DateField("Fecha y hora de fin")

        class PermisoAdmin(admin.ModelAdmin):
            class Meta:
                model = Permiso

            list_filter = [
                ('fechahorafin', DateTimeLessThanFilter),
                ('fechahorainicio', DateTimeMoreThanFilter),
                ('fechaaprobacion', DateRangeFilter),
            ]
"""

from __future__ import unicode_literals

import datetime
from collections import OrderedDict

import django
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.admin.widgets import \
    AdminSplitDateTime as BaseAdminSplitDateTime
from django.template.defaultfilters import slugify
from django.templatetags.static import StaticNode
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.html import format_html
from PIL.EpsImagePlugin import field

try:
    import pytz
except ImportError:
    pytz = None

try:
    import csp
except ImportError:
    csp = None



if django.VERSION >= (2, 0, 0):
    from django.utils.translation import gettext_lazy as _
else:
    from django.utils.translation import ugettext_lazy as _


class AdminSplitDateTime(BaseAdminSplitDateTime):
    def format_output(self, rendered_widgets):
        return format_html('<p class="datetime">{}</p><p class="datetime">{}</p>',
                           rendered_widgets[0],
                           rendered_widgets[1])

class DateRangeFilter(admin.filters.FieldListFilter):
    template = 'templates/admin/filters/date_range_filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg_gte = '{0}__range__gte'.format(field_path)
        self.lookup_kwarg_lte = '{0}__range__lte'.format(field_path)

        super(DateRangeFilter, self).__init__(
            field, request, params, model, model_admin, field_path)

        self.request = request
        self.form = self.get_form(request)

    def get_timezone(self, request):
        return timezone.get_default_timezone()

    @staticmethod
    def make_dt_aware(value, timezone):
        if settings.USE_TZ and pytz is not None:
            default_tz = timezone
            if value.tzinfo is not None:
                value = default_tz.normalize(value)
            else:
                value = default_tz.localize(value)
        return value

    def choices(self, cl):
        yield {
            # slugify converts any non-unicode characters to empty characters
            # but system_name is required, if title converts to empty string use id
            # https://github.com/silentsokolov/django-admin-rangefilter/issues/18
            'system_name': force_str(slugify(self.title) if slugify(self.title) else id(self.title)),
            'query_string': cl.get_query_string(
                {}, remove=self._get_expected_fields()
            )
        }

    def expected_parameters(self):
        return self._get_expected_fields()

    def queryset(self, request, queryset):
        if self.form.is_valid():
            validated_data = dict(self.form.cleaned_data.items())
            if validated_data:
                return queryset.filter(
                    **self._make_query_filter(request, validated_data)
                )
        return queryset

    def _get_expected_fields(self):
        return [self.lookup_kwarg_gte, self.lookup_kwarg_lte]

    def _make_query_filter(self, request, validated_data):
        query_params = {}
        date_value_gte = validated_data.get(self.lookup_kwarg_gte, None)
        date_value_lte = validated_data.get(self.lookup_kwarg_lte, None)

        if date_value_gte:
            query_params['{0}__gte'.format(self.field_path)] = self.make_dt_aware(
                datetime.datetime.combine(date_value_gte, datetime.time.min),
                self.get_timezone(request),
            )
        if date_value_lte:
            query_params['{0}__lte'.format(self.field_path)] = self.make_dt_aware(
                datetime.datetime.combine(date_value_lte, datetime.time.max),
                self.get_timezone(request),
            )

        return query_params

    def get_form(self, request):
        form_class = self._get_form_class()
        return form_class(self.used_parameters)

    def _get_form_class(self):
        fields = self._get_form_fields()

        form_class = type(
            str('DateRangeForm'),
            (forms.BaseForm,),
            {'base_fields': fields}
        )
        form_class.media = self._get_media()
        # lines below ensure that the js static files are loaded just once
        # even if there is more than one DateRangeFilter in use
        request_key = 'DJANGO_RANGEFILTER_ADMIN_JS_SET'
        if (getattr(self.request, request_key, False)):
            form_class.js = []
        else:
            setattr(self.request, request_key, True)
            form_class.js = self.get_js()
        return form_class

    def _get_form_fields(self):
        return OrderedDict(
            (
                (self.lookup_kwarg_gte, forms.DateField(
                    label='',
                    widget=AdminDateWidget(attrs={'placeholder': _('Desde')}),
                    localize=True,
                    required=False
                )),
                (self.lookup_kwarg_lte, forms.DateField(
                    label='',
                    widget=AdminDateWidget(attrs={'placeholder': _('Hasta')}),
                    localize=True,
                    required=False
                )),
            )
        )

    @staticmethod
    def get_js():
        return [
            StaticNode.handle_simple('admin/js/calendar.js'),
            StaticNode.handle_simple('admin/js/admin/DateTimeShortcuts.js'),
        ]

    @staticmethod
    def _get_media():
        js = [
            'calendar.js',
            'admin/DateTimeShortcuts.js',
        ]
        css = [
            'widgets.css',
        ]
        return forms.Media(
            js=['admin/js/%s' % url for url in js],
            css={'all': ['admin/css/%s' % path for path in css]}
        )


class DateTimeRangeFilter(DateRangeFilter):
    template = 'templates/admin/filters/date_time_range_filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg_gte = '{0}__range__gte'.format(field_path)
        self.lookup_kwarg_lte = '{0}__range__lte'.format(field_path)

        lookup_kwarg_gte_date = self.lookup_kwarg_gte + "_0"
        lookup_kwarg_gte_time = self.lookup_kwarg_gte + "_1"
        if lookup_kwarg_gte_time in params and lookup_kwarg_gte_date in params:
            date = params[lookup_kwarg_gte_date].strip()
            time = params[lookup_kwarg_gte_time].strip()
            if not date == "" and time == "":
                params[lookup_kwarg_gte_time] = "0:00"

        lookup_kwarg_lte_date = self.lookup_kwarg_lte + "_0"
        lookup_kwarg_lte_time = self.lookup_kwarg_lte + "_1"
        if lookup_kwarg_lte_time in params and lookup_kwarg_lte_date in params:
            date = params[lookup_kwarg_lte_date].strip()
            time = params[lookup_kwarg_lte_time].strip()
            if not date == "" and time == "":
                params[lookup_kwarg_lte_time] = "23:59"

        super(DateTimeRangeFilter, self).__init__(
            field, request, params, model, model_admin, field_path)

    def _get_expected_fields(self):
        expected_fields = []
        for field in [self.lookup_kwarg_gte, self.lookup_kwarg_lte]:
            for i in range(2):
                expected_fields.append('{}_{}'.format(field, i))
        return expected_fields

    def _get_form_fields(self):
        return OrderedDict(
            (
                (self.lookup_kwarg_gte, forms.SplitDateTimeField(
                    label='',
                    widget=AdminSplitDateTime(
                        attrs={'placeholder': _('Desde')}),
                    localize=True,
                    required=False
                )),
                (self.lookup_kwarg_lte, forms.SplitDateTimeField(
                    label='',
                    widget=AdminSplitDateTime(
                        attrs={'placeholder': _('Hasta')}),
                    localize=True,
                    required=False
                )),
            )
        )

    def _make_query_filter(self, request, validated_data):
        query_params = {}
        date_value_gte = validated_data.get(self.lookup_kwarg_gte, None)
        date_value_lte = validated_data.get(self.lookup_kwarg_lte, None)

        if date_value_gte:
            query_params['{0}__gte'.format(self.field_path)] = self.make_dt_aware(
                date_value_gte, self.get_timezone(request)
            )
        if date_value_lte:
            query_params['{0}__lte'.format(self.field_path)] = self.make_dt_aware(
                date_value_lte, self.get_timezone(request)
            )

        return query_params


class DateTimeMoreThanFilter(DateRangeFilter):
    template = 'templates/admin/filters/date_time_simple_filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = '{0}__range'.format(field_path)

        lookup_kwarg_date = self.lookup_kwarg + "_0"
        lookup_kwarg_time = self.lookup_kwarg + "_1"
        if lookup_kwarg_time in params and lookup_kwarg_date in params:
            date = params[lookup_kwarg_date].strip()
            time = params[lookup_kwarg_time].strip()
            if not date == "" and time == "":
                params[lookup_kwarg_time] = "0:00"

        super(DateTimeMoreThanFilter, self).__init__(
            field, request, params, model, model_admin, field_path)

    def _get_expected_fields(self):
        expected_fields = []
        for field in [self.lookup_kwarg]:
            for i in range(2):
                expected_fields.append('{}_{}'.format(field, i))
        return expected_fields

    def _get_form_fields(self):
        return OrderedDict(
            (
                (self.lookup_kwarg, forms.SplitDateTimeField(
                    label='',
                    widget=AdminSplitDateTime(
                        attrs={'placeholder': _('Desde')}),
                    localize=True,
                    required=False
                )),
            )
        )

    def _make_query_filter(self, request, validated_data):
        query_params = {}
        date_value = validated_data.get(self.lookup_kwarg, None)

        if date_value:
            query_params['{0}__gte'.format(self.field_path)] = self.make_dt_aware(
                date_value, self.get_timezone(request)
            )

        return query_params


class DateTimeLessThanFilter(DateRangeFilter):
    template = 'templates/admin/filters/date_time_simple_filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = '{0}__range'.format(field_path)

        lookup_kwarg_date = self.lookup_kwarg + "_0"
        lookup_kwarg_time = self.lookup_kwarg + "_1"
        if lookup_kwarg_time in params and lookup_kwarg_date in params:
            date = params[lookup_kwarg_date].strip()
            time = params[lookup_kwarg_time].strip()
            if not date == "" and time == "":
                params[lookup_kwarg_time] = "23:59"

        super(DateTimeLessThanFilter, self).__init__(
            field, request, params, model, model_admin, field_path)

    def _get_expected_fields(self):
        expected_fields = []
        for field in [self.lookup_kwarg]:
            for i in range(2):
                expected_fields.append('{}_{}'.format(field, i))
        return expected_fields

    def _get_form_fields(self):
        return OrderedDict(
            (
                (self.lookup_kwarg, forms.SplitDateTimeField(
                    label='',
                    widget=AdminSplitDateTime(
                        attrs={'placeholder': _('Hasta')}),
                    localize=True,
                    required=False
                )),
            )
        )

    def _make_query_filter(self, request, validated_data):
        query_params = {}
        date_value = validated_data.get(self.lookup_kwarg, None)

        if date_value:
            query_params['{0}__lte'.format(self.field_path)] = self.make_dt_aware(
                date_value, self.get_timezone(request)
            )

        return query_params


class DateMoreThanFilter(DateRangeFilter):
    template = 'templates/admin/filters/date_simple_filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = '{0}__gte'.format(field_path)

        lookup_kwarg_date = self.lookup_kwarg
        if lookup_kwarg_date in params:
            date = params[lookup_kwarg_date].strip()

        super(DateMoreThanFilter, self).__init__(
            field, request, params, model, model_admin, field_path)

    def _get_expected_fields(self):
        expected_fields = []
        for field in [self.lookup_kwarg]:
            expected_fields.append('{}'.format(field))
        return expected_fields

    def _get_form_fields(self):
        return OrderedDict(
            (
                (self.lookup_kwarg, forms.DateTimeField(
                    label='',
                    widget=AdminDateWidget(
                        attrs={'placeholder': _('Desde')}),
                    localize=True,
                    required=False
                )),
            )
        )

    def _make_query_filter(self, request, validated_data):
        query_params = {}
        date_value = validated_data.get(self.lookup_kwarg, None)

        if date_value:
            query_params['{0}__gte'.format(self.field_path)] = self.make_dt_aware(
                date_value, self.get_timezone(request)
            )

        return query_params

class DateLessThanFilter(DateRangeFilter):
    template = 'templates/admin/filters/date_simple_filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = '{0}__lte'.format(field_path)

        lookup_kwarg_date = self.lookup_kwarg
        if lookup_kwarg_date in params:
            date = params[lookup_kwarg_date].strip()

        super(DateLessThanFilter, self).__init__(
            field, request, params, model, model_admin, field_path)

    def _get_expected_fields(self):
        expected_fields = []
        for field in [self.lookup_kwarg]:
            expected_fields.append('{}'.format(field))
        return expected_fields

    def _get_form_fields(self):
        return OrderedDict(
            (
                (self.lookup_kwarg, forms.DateTimeField(
                    label='',
                    widget=AdminDateWidget(
                        attrs={'placeholder': _('Hasta')}),
                    localize=True,
                    required=False
                )),
            )
        )

    def _make_query_filter(self, request, validated_data):
        query_params = {}
        date_value = validated_data.get(self.lookup_kwarg, None)

        if date_value:
            query_params['{0}__gte'.format(self.field_path)] = self.make_dt_aware(
                date_value, self.get_timezone(request)
            )

        return query_params
