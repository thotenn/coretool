from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

# https://docs.djangoproject.com/en/3.1/topics/db/multi-db/
# https://stackoverflow.com/questions/43331376/multiple-arguments-with-values-to-custom-management-command


class Command(BaseCommand):
    help = 'Copiar los datos de una base de datos base a otra secundaria. Ejemplo de uso: ' \
           'python manage.py initialsync --bdbase base --bdsecondary default --settings=kernel.set.local2'

    def add_arguments(self, parser):
        parser.add_argument('--bdbase', type=str, nargs='+',
                            help='El nombre de la bd de la cual vamos a copiar los datos')
        parser.add_argument('--bdsecondary', type=str, nargs='+',
                            help='El nombre de la bd en la cual vamos a depositar los datos, es decir la secundaria.')

    def handle(self, *args, **kwargs):
        bdbase = kwargs['bdbase'][0]
        bdsecondary = kwargs['bdsecondary'][0]
        print('Esta apunto de copiar los datos de la bd {} a la bd {}.'.format(bdbase, bdsecondary))
        """
        administrador
        base
        inventario
        ventas
        gastos
        """
        app_models = {
            'auth': [
                'User'
            ],
            'administrador': ['Moneda', 'Config', 'Aplicacion'],
            'base': [
                'LocPais',
                'LocEstado',
                'LocCiudad',
                'LocBarrio',
                'Localidad',
                'PersonaTipoDoc',
                'PersonaEstadoCivil',
                'PersonaGrupoSangre',
                'Persona',
                'PersonaContacto',
                'PersonaContactoEmergencia',
                'PersonaHijo',
                'CategoriaSucursal',
                'Sucursal',
                'CategoriaDeposito',
                'Deposito',
                'ContactoTipo',
                'TipoRelacion',
                'Rol',
                'Permiso',
                'RolPermiso',
                'UserRol',
                'UserPermiso',
                'UsersData'
            ],
            'inventario': [
                'ProductoCategoria',
                'ProductoEstado',
                'Marca',
                'Proveedor',
                'Producto',
                'CompraEstado',
                'CompraCab',
                'Compra',
                'Transferencia',
                'TransferenciaItem',
                'DepositoStock',
                'Barcode'
            ],
            'ventas': [
                'EmpresaEnvio',
                'Empresa',
                'Cliente',
                'TipoDescuento',
                'TipoPago',
                'Factura',
                'Pedido',
                'PedidoItem',
                'Envio',
                'Venta'
            ]
        }
        models = list()
        for app in app_models:
            for m in app_models[app]:
                am = (app, m)
                models.append(am)
        print('LAS APP CON SUS MODELOS SON:')
        print(models)
        for model in models:
            print('Procesando ({}, {})'.format(model[0], model[1]))
            try:
                mod = apps.get_model(app_label=model[0], model_name=model[1])
                mod.objects.using(bdsecondary).bulk_create(mod.objects.using(bdbase).all())
            except Exception as err:
                print('Error: ', err)
        print('EJECUTADO CORRECTAMENTE')
