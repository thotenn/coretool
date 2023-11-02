# import random
from typing import List  # , Union
from django.urls import path
# from django.db.models.base import ModelBase
# from django.http import HttpRequest

from rest_framework import serializers, status  # , viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


class GenView(APIView):
    def __init__(self, **kwargs):
        super(GenView, self).__init__(**kwargs)

    permission_classes = [IsAuthenticated]
    model_class = None
    serializer = None

    """
    Obtiene un objeto
    """
    def get_object(self, pk):
        try:
            return self.model_class.objects.get(pk=pk)
        except self.model_class.DoesNotExist as err:
            return Response({'ERROR': err.__str__()}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, format=None):
        """
        Obtiene todos los objetos
        """
        content = self.model_class.objects.all()
        serializer = self.serializer(content, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """
        Crea un objeto
        """
        # TODO: Rellenar el campo createdby por algun usuario que haga referencia a los de afuera
        if request.method == 'POST':
            try:
                serializer = self.serializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as err:
                return Response(err.__str__(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response('Error Request', status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def put(self, request, pk, format=None):
        """
        Actualiza un objeto
        """
        if request.method == 'PUT':
            try:
                obj = self.get_object(pk)
            except Exception as err:
                return Response(err.__str__(), status=status.HTTP_404_NOT_FOUND)
            try:
                serializer = self.serializer(instance=obj, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as err:
                return Response(err.__str__(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response('Error Request', status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, request, pk, format=None):
        """
        Borra un objeto
        """
        try:
            obj = self.get_object(pk)
            obj.delete()
            return Response('Eliminado', status=status.HTTP_200_OK)
        except Exception as err:
            return Response(err.__str__(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def api_generate_serializer_class(
        model_class: type.__class__
) -> type.__class__:
    class BaseSerializer(serializers.ModelSerializer):
        class Meta:
            model = model_class
            fields = model_class.api_fields
    return BaseSerializer


def generate_gen_view(model_class_g):
    class ModelGenView(GenView):
        model_class = model_class_g
        serializer = api_generate_serializer_class(
            model_class=model_class_g
        )
    return ModelGenView


def generate_urlpatterns_gens_view(tuplas_models_name_fields: List) -> list:
    urlpatterns = list()
    for item in tuplas_models_name_fields:
        api_url_name = ""
        if type(item) == tuple:
            if type(item[0]) == str:
                api_url_name = item[0]
            else:
                api_url_name = item[0].api_url_name
            api_view = item[1]
        else:
            model_class = item
            api_view = generate_gen_view(model_class_g=model_class)
        urlpatterns.append(
            path(
                api_url_name + '/',
                api_view.as_view(),
                name=api_url_name
            )
        )
        urlpatterns.append(
            path(
                api_url_name + '<int:pk>/',
                api_view.as_view(),
                name=api_url_name
            )
        )
    return urlpatterns
