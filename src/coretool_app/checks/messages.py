# pylint: disable=redefined-builtin

from django.core.checks.messages import Warning

CURRENT_APP = 'core'


class NoExisteTablaWarning(Warning):
    def __init__(self, cls):
        super().__init__(
            'No existe la tabla {tabla}.'.format(
                tabla=cls._meta.db_table.upper()),
            obj=cls,
            id='{app}.W100'.format(app=CURRENT_APP))


class NoExisteFixtureWarning(Warning):
    def __init__(self, cls):
        super().__init__(
            'No existe el fixture \'{fixture_path}\'.'.format(
                fixture_path=cls.fixture),
            hint="Revise si la ruta es correcta o si el archivo json existe.",
            obj=cls,
            id='{app}.W101'.format(app=CURRENT_APP))


class FixtureNoUniformeWarning(Warning):
    def __init__(self, cls, model_label_encontrado):
        super().__init__(
            'El fixture contiene datos de un modelo distinto al \'{model_label_esperado}\'. Modelo encontrado: \'{model_label_encontrado}\'.'.format(
                model_label_esperado=cls._meta.label_lower,
                model_label_encontrado=model_label_encontrado),
            hint="Se espera que el fixture contenga solamente los datos de los modelos \'{model_label_esperado}\'.".format(
                model_label_esperado=cls._meta.label_lower),
            obj=cls,
            id='{app}.W102'.format(app=CURRENT_APP))


class FixtureNoValidoWarning(Warning):
    def __init__(self, cls, exc):
        super().__init__(
            'El fixture \'{fixture_path}\' no es válido ({exception_message}).'.format(
                fixture_path=cls.fixture,
                exception_message=str(exc)),
            hint="El fixture debe ser un archivo JSON válido.",
            obj=cls,
            id='{app}.W103'.format(app=CURRENT_APP))


class NoExisteComplexCodigoWarning(Warning):
    def __init__(self, cls, codigo):
        super().__init__(
            'No existe el codigo \'{codigo}\' en la tabla {tabla}.'.format(
                codigo=codigo,
                tabla=cls._meta.db_table.upper()),
            hint="Cargue una fila en la tabla {tabla} con los datos especificados en el fixture.".format(
                tabla=cls._meta.db_table.upper()),
            obj=cls,
            id='{app}.W104'.format(app=CURRENT_APP))


class ExisteMultiplesComplexCodigoWarning(Warning):
    def __init__(self, cls, codigo):
        super().__init__(
            'Existe más de una fila con el código \'{codigo}\' en la tabla {tabla}.'.format(
                codigo=codigo,
                tabla=cls._meta.db_table.upper()),
            hint="El codigo \'{codigo}\' debe ser único en la tabla {tabla}.".format(
                codigo=codigo,
                tabla=cls._meta.db_table.upper()),
            obj=cls,
            id='{app}.W105'.format(app=CURRENT_APP))


class DiferenciaComplexCodigoWarning(Warning):
    def __init__(self, cls, field, database_instance, json_instance):
        super().__init__(
            'El campo \'{field}\' del código \'{codigo}\' difiere entre la base de datos y el fixture. Dato esperado: \'{field_codigo_esperado}\', dato encontrado: \'{field_codigo_encontrado}\''.format(
                codigo=json_instance['codigo'],
                field=field,
                field_codigo_encontrado=database_instance[field],
                field_codigo_esperado=json_instance[field]),
            hint="Verifique el código \'{codigo}\' de la tabla {tabla} o del fixture.".format(
                codigo=json_instance['codigo'],
                tabla=cls._meta.db_table.upper()),
            obj=cls,
            id='{app}.W106'.format(app=CURRENT_APP))


class NoCoincidenColumnasModeloTablaWarning(Warning):
    def __init__(self, cls):
        super().__init__(
            'No coinciden las columnas de la tabla {tabla} con los campos del modelo {modelo}.'.format(
                tabla=cls._meta.db_table.upper(),
                modelo=cls.__name__),
            hint="Revise si las migraciones se crearon y se aplicaron correctamente.",
            obj=cls,
            id='{app}.W107'.format(app=CURRENT_APP))
