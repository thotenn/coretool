from rest_framework.parsers import JSONParser

from .crudbasic import CrudBasic


class ApiBasicController:
    @staticmethod
    def post(request):
        data = None
        try:
            if type(request) is not dict:  # Puede que el request ya se haya parseado de una forma distinta
                data = JSONParser().parse(request)
            else:  # Entonces directamente igualamos a la data
                data = request
        except Exception as err:
            print(err)
        api_type = data['type']
        types = api_type.split('_')
        content = None
        try:
            if len(types) == 3:
                content = CrudBasic.crud_basic_get_content(
                    types,
                    data_set=data
                )
        except Exception as err:
            print(err)
            raise err
        return content
