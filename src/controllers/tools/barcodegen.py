import barcode
from enum import Enum


def generate_ean13(basenum: int):
    # Contamos los digitos
    k = 0
    suma_par = 0
    suma_impar = 0
    basenum_copy = basenum
    while basenum_copy > 0:
        basenum_copy = int(basenum_copy / 10)
        k = k + 1
    if k > 12:
        raise Exception('Error, los digitos no pueden ser mayores a 12')
    ik = 1
    basenum_copy: int = basenum
    while basenum_copy > 0:
        if ik % 2 == 0:
            suma_par = suma_par + int(basenum_copy % 10)
        else:
            suma_impar = suma_impar + int(basenum_copy % 10)
        ik = ik + 1
        basenum_copy = int(basenum_copy / 10)
    final_sum = suma_par + (suma_impar * 3)

    # Redondeamos al entero mas cercano
    final_sum_ceil = final_sum
    while int(final_sum_ceil % 10) > 0:
        final_sum_ceil = final_sum_ceil + 1
    res = (basenum * 10) + (final_sum_ceil - final_sum)
    return res


class BarcodeTypes(Enum):
    CODE39 = 'code39'
    CODE128 = 'code128'
    PZN7 = 'pzn'
    EAN13 = 'ean13'
    EAN8 = 'ean8'
    JAN = 'jan'
    ISBN13 = 'isbn13'
    ISBN10 = 'isbn10'
    ISSN = 'issn'
    UPCA = 'upca'
    EAN14 = 'ean14'
    GS1128 = 'gs1_128'


def barcode_generate_fullcode(code, type_barcode=BarcodeTypes.EAN13):
    """
    Genera el codigo completo del semicodigo enviado, por ejemplo, en el formato ean13 la data seria: 123456789012
    y el resultado seria: 1234567890128

    References:
        https://python-barcode.readthedocs.io/en/stable/
    Args:
        code (str): El codigo con el digito verificador faltante.
        type_barcode (str): El formato del codigo. los posibles son: []

    Returns:
        str: El codigo completo incluido el digito verificador.
    """
    try:
        res = barcode.get(type_barcode, code).get_fullcode()
    except Exception as err:
        raise err
    return res


def barcode_generate_file(code, path, options, type_barcode=BarcodeTypes.EAN13.value):
    """
    Genera una imagen de codigo de barras
    Ejemplo:
    barcode_generate_file('1234567890128', 'hello', {'compress': True, 'font_size': 30})

    Args:
        code (str): El codigo de barras
        path (str): El path donde se creara y almacenara el archivo, por supuesto que con su nombre,
                    Ej: /tmp/archivo.svg
        options (dict): Opciones para la imagen, ver en all_options
        type_barcode (str): El tipo de codigo de barras fijado en la clase BarcodeTypes

    Returns (bool): True si se creo con exito, y false si no.

    """
    all_options = dict(
        compress=False,
        module_width=0.2,
        module_height=15.0,
        quiet_zone=6.5,
        font_size=10,
        text_distance=5.0,
        background='white',
        foreground='black',
        center_text=True
    )
    opts = all_options | options
    try:
        bc = barcode.get(type_barcode, code)
        bc.save(path, opts)
    except:
        return False
    return True
