"""
PSTRUCT: Estructura del proyecto, componentes y subcomponentes

# PSTRUCT > MODULES > APPS > MODELS > VIEWS

PSTRUCT: dict = {
    'modulo_name': {
        'code': 'rh',
        'title': 'RRHH',
        'apps': {
            'aplicacion_name': {
                'code': 'fu',
                'title': 'Funcionarios',
                'appname': 'funcionarios',
                'models': {
                    'model_name': {
                        'code': 'lf',
                        'title': 'Archivos de Marcacion',
                        'views': {
                            'view_name': {
                                'code': 'ac',
                                'title': 'Controlador de Asistencias de Funcionarios'
                            }
                        }
                    }
                }
            }
        }
    }
}
"""

PSTRUCT: dict = {
    'rrhh': {
        'code': 'rh',
        'title': 'RRHH',
        'apps': {
            'asistencia': {
                'code': 'as',
                'title': 'Asistencia',
                'appname': 'asistencia',
                'models': {
                    'Reloj': {
                        'code': 'rj',
                        'title': 'Reloj',
                        'views': {
                            'ImportacionCronJobAdmin': {
                                'code': 'cj',
                                'title': 'Controlador de Importacion automatica'
                            }
                        }
                    }
                }
            },
            'funcionarios': {
                'code': 'fu',
                'title': 'Funcionarios',
                'appname': 'funcionarios',
                'models': {
                    'logsfiles': {
                        'code': 'lf',
                        'title': 'Archivos de Marcacion',
                        'views': {
                            'FAsistenciaController': {
                                'code': 'ac',
                                'title': 'Controlador de Asistencias de Funcionarios'
                            }
                        }
                    },
                    'importacionautocab': {
                        'code': 'ia',
                        'title': 'Importacion automatica de registros de marcacion',
                        'views': {
                            'ZkController': {
                                'code': 'zk',
                                'title': 'Controlador de importacion automatica de asistencias de Funcionarios'
                            }
                        }
                    }
                }
            },
            'system': {
                'code': 'sy',
                'title': 'System',
                'appname': 'system',
                'models': {
                    'CronJob': {
                        'code': 'cj',
                        'title': 'Tareas Programadas (Det)',
                        'views': {
                            'CronJobsController': {'code': 'cj', 'title': 'Controlador de Tareas Programadas'}
                        }
                    }
                }
            }
        }
    }
}

SYSTEMINFO = {
    'name': 'DaleCompra PY',
    'nameshort': 'DCP',
    'empresanombre': 'MG SERVICES',
    'empresanombrecorto': 'MG',
    'favicon': 'admin/assets/images/logos/mg/favicon.png',
    'logo': 'admin/assets/images/logos/mg/logo_small.png',
    'logo_alternative': 'admin/assets/images/logos/mg/logo_small.png',
    'logoalt': 'DCP'
}
