from django import template

from django.conf import settings

# EN EL ARCHIVO SETTINGS HACER ESTO:
# from .pstruct import PSTRUCT, SYSTEMINFO
# PSTRUCT = PSTRUCT
# SYSTEMINFO = SYSTEMINFO
# FIN

PSTRUCT = settings.PSTRUCT
SYSTEMINFO = settings.SYSTEMINFO

# from django.contrib.auth.models import Group
from ..controllers.users.users import UserController

register = template.Library()

@register.simple_tag
def admintag_get_project_name():
    return SYSTEMINFO['name']

@register.simple_tag
def admintag_get_project_name_short():
    return SYSTEMINFO['nameshort']

@register.simple_tag
def admintag_get_empresa_nombre():
    return SYSTEMINFO['empresanombre']

@register.simple_tag
def admintag_get_empresa_nombre_corto():
    return SYSTEMINFO['empresanombrecorto']

@register.simple_tag
def admintag_get_system_title():
    return admintag_get_project_name() + ' - ' + admintag_get_empresa_nombre()

@register.simple_tag
def admintag_get_system_title_short():
    return admintag_get_project_name_short() + ' - ' + admintag_get_empresa_nombre_corto()

@register.simple_tag
def admintag_get_favicon():
    return SYSTEMINFO['favicon']

@register.simple_tag
def admintag_get_logo():
    return SYSTEMINFO['logo']

@register.simple_tag
def admintag_get_logo_alternative():
    return SYSTEMINFO['logo_alternative']

@register.simple_tag
def admintag_get_logo_alt():
    return SYSTEMINFO['logoalt']

@register.filter(name='has_group')
def has_group(user, group_name):
    pass
    # if not user.is_superuser:
    #     group = Group.objects.get(name=group_name)
    #     return True if group in user.groups.all() else False
    # return True

@register.filter(name='admin_group')
def is_in_admins_groups(user):
    userc = UserController(user)
    return userc.in_admin_group()
