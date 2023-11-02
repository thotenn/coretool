def net_get_abs_url(request):
    '''
    Esta funcion retorna la url root o absoluta de la que se ha enviado el request
    ej.: https://127.0.0.1:8000
    '''
    urls = {
        'ABSOLUTE_ROOT': request.build_absolute_uri('/')[:-1].strip("/"),
        'ABSOLUTE_ROOT_URL': request.build_absolute_uri('/').strip("/"),
    }

    return urls