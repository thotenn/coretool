from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..api import GenView
from .apibasiccontroller import ApiBasicController


class ApiRestBaseController(GenView):
    permission_classes = (IsAuthenticated,)
    api_url_name = 'apirestbase'

    def get(self, request, format=None):
        return Response('Error Request', status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request, format=None):
        try:
            content = ApiBasicController.post(request)
        except Exception as err:
            print(err)
            return Response('Error Request', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if content is None:
            return Response('Error Request', status=status.HTTP_404_NOT_FOUND)
        return Response(content)

    def put(self, request, pk, format=None):
        return Response('Error Request', status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, request, pk, format=None):
        return Response('Error Request', status=status.HTTP_405_METHOD_NOT_ALLOWED)
