def tools_json_dict_merge(principal: dict, json_for_merge: dict, replace: bool = False) -> dict:
    for key in principal.keys():
        if key in json_for_merge:
            if replace:
                principal[key] =json_for_merge[key]
    for key, value in json_for_merge.items():
        if not key in principal:
            principal[key] = value
    return principal


def tools_json_dict_all_to_str(jsonvar: dict):
    for key, value in jsonvar.items():
        try:
            jsonvar[key] = str(value)
        except:
            jsonvar[key] = value.__str__()
    return jsonvar
