from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..api import GenView
from ..tools.classes import tools_classes_import_from_str as t_import


def get_response(is_success, payload=None, code=status.HTTP_400_BAD_REQUEST, message=''):
    """
    Retorna el formato estandar del Response que seria asi:
    {
        success: bool,
        payload: any,
        error: {
            code: int,
            message: str
        }
    }
    Args:
        is_success (bool): Si no retorna ni un error
        payload (Any): La respuesta al request
        code (int): El codigo del error si lo tuviese
        message (str): El mensaje del error si lo tuviese

    Returns (Response): Retorna el response que va directo al cliente

    """
    response = {}
    if not is_success:
        response['error'] = {
            code: code,
            message: message
        }
    response['success'] = is_success
    if payload is not None:
        response['payload'] = payload
    return Response(response)


class ApiRestStandard(GenView):

    permission_classes = (IsAuthenticated, )
    api_url_name = 'response'
    controllers_list = {}

    def get(self, request, format=None):
        return get_response(
            is_success=False,
            message='No permitido'
        )

    def post(self, request, format=None):
        try:
            data = JSONParser().parse(request)
            api_type = data['type']
            payload = data['payload']
            s_type = None
            if 'stype' in data:
                s_type = data['stype']
            class_src = self.controllers_list[api_type]
            base_controller = t_import(class_src, '_')()
            content = base_controller.get_data(payload, s_type=s_type)
        except Exception as err:
            print(err)
            return get_response(
                is_success=False,
                message='Error interno.'
            )
        if content is None:
            return get_response(
                is_success=False,
                message='No response.'
            )
        return get_response(
            is_success=True,
            payload=content
        )

    def put(self, request, pk, format=None):
        return get_response(
            is_success=False,
            message='No permitido'
        )

    def delete(self, request, pk, format=None):
        return get_response(
            is_success=False,
            message='No permitido'
        )
