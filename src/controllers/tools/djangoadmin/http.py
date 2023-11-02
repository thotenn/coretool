def tools_http_print_wsgirequest(request):
    strres = ""
    for key in request.__dict__.keys():
        strres = strres + str(key) + ': ' + str(request.__dict__[key]) + '\n'
    return strres