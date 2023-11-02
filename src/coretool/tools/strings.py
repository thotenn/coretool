import random
import re
import string
import unicodedata
import secrets


def strings_just_numbers(valor):
    return re.sub(r"[^0-9]+", '', valor)


def strings_just_letters(valor):
    return re.sub(r"[^A-Za-z]+", '', valor)


def strings_currency_format(valor: float, none_val='0'):
    if valor is None:
        return none_val
    return '{:0,.0f}'.format(valor).replace(',', '.')


def strings_currency_gs(valor):
    if valor is None:
        return ''
    return 'Gs. {:0,.0f}'.format(valor).replace(',', '.')


def strings_get_fcurrency_value(valor: float, currency: str = 'gs', none_val=''):
    if valor is None:
        return none_val
    if currency == '':
        return '{:0,.0f}'.format(valor).replace(',', '.')
    elif currency == 'gs':
        return 'Gs. {:0,.0f}'.format(valor).replace(',', '.')
    return valor.__str__()


def strings_get_s_numer(number: int or float) -> str:
    return 's' if number > 0 or number == 0 else ''


def strings_array_values_to_str(arrayval: list or tuple, float_to_currency_cast=True):
    newarray = list()
    for i, item in enumerate(arrayval):
        if type(item) not in [list, tuple]:
            typeitem = type(item)
            if typeitem == 'datetime.date':
                item = item.isoformat()
            elif typeitem == 'datetime':
                item = item.strftime("%Y/%m/%d %H:%M:%S"),
            elif typeitem == float and float_to_currency_cast:
                item = strings_get_fcurrency_value(item)
            else:
                item = item.__str__()
        else:
            item = strings_array_values_to_str(item)
        newarray.append(item)
    return newarray


def strings_generate_code(length=6):
    """
    Genera codigos random de tipo string, ej: 'YHFJDL'
    """
    return ''.join(random.choices(string.ascii_uppercase, k=length))


def strings_generate_token_urlsafe():
    """
    Genera un token seguro al azar
    """
    return secrets.token_urlsafe()


def strings_generate_random_password(length=9):
    """
    Genera un codigo random seguro, util para crear passwords
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))


def strings_normalize_str(value):
    """
    Elimina todas las ñ, vocales con acentos, etc
    """
    return unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode("utf-8")

def strings_normalize_slower_str(value):
    """
    Elimina todas las ñ, vocales con acentos, etc
    """
    return strings_normalize_str(re.sub(' +', ' ', value).strip().lower())


def strings_delete_duplicates(value):
    """
    Elimina palabras repetidas dentro de un string
    Args:
        value: String

    Returns: String

    """
    keys = value.split()
    unique_keys = set(keys)
    return ' '.join(unique_keys)


def strings_seeker_iregex_and(search):
    """
    Seria un buscador en el cual quita todos los espacios extra, normaliza, splitea y luego forma el regex
    correspondiente para agregar al filtro NOMBRECOLUMNA__iregex=lo que retorna esta funcion
    Por ejemplo:
    search = ' ga   jo  '
    y me filtra todas las filas que contengan en la columna NOMBRECOLUMNA los valores 'ga' y 'jo' al simultaneamente

    Ejemplo practico:
    regex_filter = strings_seeker_iregex_and(search)

    res = Cliente.objects.filter(
        Q(razon__iregex=regex_filter) |
        Q(identificador__iregex=regex_filter)
    )
    """
    new_search = strings_normalize_str(re.sub(' +', ' ', search.strip()))
    search_split = new_search.split(' ')
    return '^(?=.*' + ')(?=.*'.join(search_split) + ').*$'


def strings_seeker_iregex_or(search):
    """
    Seria un buscador en el cual quita todos los espacios extra, normaliza, splitea y luego forma el regex
    correspondiente para agregar al filtro NOMBRECOLUMNA__iregex=lo que retorna esta funcion
    Por ejemplo:
    search = ' ga   jo  '
    y me filtra todas las filas que contengan en la columna NOMBRECOLUMNA los valores 'ga' o 'jo' indistintamente
    """
    new_search = strings_normalize_str(re.sub(' +', ' ', search.strip()))
    search_split = new_search.split(' ')
    return '^.*(%s).*$' % '|'.join(search_split)
