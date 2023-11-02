from django.template.loader import render_to_string
from django.utils.html import format_html #, escape
from django.utils.safestring import mark_safe
import datetime
import re

from ...tools.strings import strings_just_numbers

class ToolsTemplates:
    @staticmethod
    def get_modal_image(imagen, identificador, titulo,
                        titulomodal="Falta imágen",
                        descripmodal="Debe ingresar a este registro y cargar la imágen"):
        #return format_html("<a href='%s' target='_blank'><img src='%s' height='42' width='42' /></a>" % (escape(imagen.url), escape(imagen.url)) )
        #return format_html('<a href="{}" target="_blank"><img src="{}" height="42" width="42" /></a>'.format(imagen.url, imagen.url))
        posee_imagen = True if not (imagen == None or imagen == '') else False
        imagen_url = None
        if posee_imagen:
            imagen_url = imagen.url
        return render_to_string('admin/modals/images.html', {'id_image': 'image_' + str(identificador).replace(' ', '_'),
                                                                        'title': str(titulo),
                                                                        'url_image': imagen_url,
                                                                        'url_image_have': posee_imagen,
                                                                        'titulomodal': titulomodal,
                                                                        'descripmodal' : descripmodal
                                                                        })
    @staticmethod
    def get_href_telefono(telefono, nombre, idforcopy=''):
        telefono_have = True
        if telefono == None or telefono == '':
            telefono_have = False
        idcopy = idforcopy
        if idforcopy == '':
            idforcopy = strings_just_numbers(str(datetime.datetime.now()))
        return render_to_string('admin/boxes/telefono.html',
                                {'telefono': str(telefono).replace(' ', ''),
                                'telefono_have': telefono_have,
                                'telefono_justnums': re.sub("\D", "", str(telefono)),
                                 'title': str(nombre),
                                 'idforcopy': idforcopy
                                })
    @staticmethod
    def get_button_change_list(objid, title, posturl='/change', preurl='', style='primary'):
        '''
        Provee el formato boton linkeado a la url de modificacion de registro por medio de su id
        Aunque tambien se puede utilizar para definir otras urls por medio de posturl y preurl

        objid: El id del registro
        '''
        return mark_safe('<a class="btn btn-'+ style + '" href="' + preurl + str(objid) + posturl + '">' + title +'</a>')

