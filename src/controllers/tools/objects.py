import inspect


def tools_objects_getmembers(obj):
    return [name for name, thing in inspect.getmembers(obj)]


def tools_objects_getattributes_values(obj):
    res = list
    # print('here ///////////////////////////////////////////////////////')
    for item in tools_objects_getmembers(obj):
        msg = str(item) + ': '
        try:
            msg = msg + str(getattr(obj, item))
            print(msg)
            res[item] = getattr(obj, item)
        except:
            msg = str(item) + ': '
            print(msg)
            pass
    return res
