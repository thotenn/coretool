# from ..pstruct import PSTRUCT
# from kernel.set.pstruct import PSTRUCT


def pstruct_get_full_tuple(PSTRUCT) -> list or None:
    """
        Listado tipo [(codigo, titulo),...] de PStruct
    """
    res = list()
    for moduloitem in PSTRUCT.items():
        for appitem in moduloitem[1]['apps'].items():
            for modelitem in appitem[1]['models'].items():
                for viewitem in modelitem[1]['views'].items():
                    subres = (
                        ('{0}_{1}_{2}_{3}'.format(str(moduloitem[1]['code']).lower(), str(appitem[1]['code']).lower(),
                                                  str(modelitem[1]['code']).lower(), str(viewitem[1]['code']).lower())),
                        ('{0} - {1} - {2} - {3}'.format(
                            moduloitem[1].get('title', moduloitem[0]), appitem[1].get('title', appitem[0]),
                            modelitem[1].get('title', modelitem[0]), viewitem[1].get('title', viewitem[0])))
                    )
                    res.append(subres)
    return res


def pstruct_is_valid(code: str, PSTRUCT) -> bool:
    if code is None:
        return False
    code = code.lower()
    for moduloitem in PSTRUCT.items():
        for appitem in moduloitem[1]['apps'].items():
            for modelitem in appitem[1]['models'].items():
                for viewitem in modelitem[1]['views'].items():
                    pstruc_code = (
                        '{0}_{1}_{2}_{3}'.format(str(moduloitem[1]['code']).lower(), str(appitem[1]['code']).lower(),
                                                 str(modelitem[1]['code']).lower(), str(viewitem[1]['code']).lower())
                    )
                    if pstruc_code == code:
                        return True
    return False


def pstruct_get_code(view: str, model: str, PSTRUCT, app: str = 'fu', modulo: str = 'rrhh') -> str or None:
    try:
        return PSTRUCT[modulo]['apps'][app]['models'][model]['views'][view]['code']
    except:
        return None
