import base64
import io
import os
import pathlib

from PIL import Image

from .strings import strings_just_letters


def get_size_mb(filepath):
    file_stats = os.stat(filepath)
    return file_stats.st_size / (1024 * 1024)


def image_compress(filepath, MAX_SIZE_MB = 0.3, BASE_QUALITY=60):
    formats = ('jpg', 'jpeg', 'png')
    file_base_name = os.path.basename(filepath)
    file_type = os.path.splitext(file_base_name)[1].lower()[1:]
    if file_type not in formats:
        return

    file_size = get_size_mb(filepath)

    if file_size <= MAX_SIZE_MB:
        return

    img_formats = {
        'JPEG': ['jpg', 'jpeg'],
        'PNG': ['png']
    }

    file_dir = os.path.dirname(filepath)
    name = '.'.join(file_base_name.split('.')[:-1])
    original_filepath_renamed = '{}/0_{}.{}'.format(file_dir, name, file_type)
    os.rename(filepath, original_filepath_renamed)
    quality = BASE_QUALITY

    while file_size > MAX_SIZE_MB:
        # open the image
        picture = Image.open(original_filepath_renamed)

        # select format
        format_img = 'JPEG'
        for item in img_formats:
            if file_type in img_formats[item]:
                format_img = item
                break
        if format_img == 'PNG':
            picture = picture.convert("P", palette=Image.ADAPTIVE, colors=256)
        picture.save(filepath,
                     format_img,
                     optimize=True,
                     quality=quality)
        file_size = get_size_mb(filepath)
        if file_size > MAX_SIZE_MB:
            if quality <= 10:
                quality = quality - 2
            else:
                quality = quality - 10
            if quality <= 2:
                os.remove(original_filepath_renamed)
                return
            os.remove(filepath)
        # print('{}, el nuevo tam es: {}, quality: {}'.format(format_img, file_size, quality))
    os.remove(original_filepath_renamed)
    return


def image_rename_for_upload(prefix, name, filename, UPLOAD_DIR, PATH_DIR, FOLDER_NAME, IN_OWN_FOLDER = True) -> str:
    """
    Cambia el nombre de la imagen a guardar por un formato estandar

    :param prefix Name Prefix
    :param name File central name
    :param filename Current filename
    :param UPLOAD_DIR Initial path for uploads
    :param PATH_DIR File path
    :param FOLDER_NAME Folder name
    :param IN_OWN_FOLDER Whether the file will have its own folder
    :type prefix: str
    :type name: str
    :type filename: str
    :type UPLOAD_DIR: str
    :type PATH_DIR: str
    :type FOLDER_NAME: str
    :type IN_OWN_FOLDER: bool
    :returns Standard name
    :rtype: str
    """
    case_name = name.lower().replace(" ", "-")
    new_folder_name = FOLDER_NAME.lower().replace(" ", "-")
    ftype = filename.split('.')
    ftype = ftype[len(ftype) - 1]
    file_name = '{}{}.{}'.format(prefix, case_name, ftype)
    if IN_OWN_FOLDER:
        return UPLOAD_DIR + PATH_DIR.format(new_folder_name, file_name)
    return UPLOAD_DIR + PATH_DIR.format(file_name)


def image_name_for_save(filename, nombre, UPLOAD_DIR, PATH_DIR, categoria_nombre=None):
    try:
        categoria_nombre = categoria_nombre
    except Exception as err:
        categoria_nombre = 'NoCategory'
    return image_rename_for_upload(
        prefix="prod_",
        name=strings_just_letters(nombre).lower(),
        filename=filename,
        UPLOAD_DIR=UPLOAD_DIR,
        PATH_DIR=PATH_DIR,
        FOLDER_NAME=strings_just_letters(categoria_nombre),
        IN_OWN_FOLDER=True
    )


def images_compress_save(filepath, max_width=None, max_height=None):
    '''
    Esta funcion guarda una imagen y la redimensiona segun el ancho y alto enviado
    si se envia solo el ancho o solo el alto, se redimensiona de modo escalado
    filepath    :   La direccion de la imagen
    '''
    filetype = filepath.split('/')
    """
    filedir = '/'
    for k, s in enumerate(filetype):
        if k < (len(filetype)-1):
            filedir = filedir + s
            if k != 0:
                filedir = filedir + '/'
    filename = 'untitled'
    """
    filetype = filetype[len(filetype)-1].split('.')
    if len(filetype) > 1:
        # filename = filetype[0]
        filetype = filetype[1]
    else:
        filetype = 'JPEG'
    if filetype in ['jpeg', 'jpg']:
        filetype = 'JPEG'
    else:
        filetype = filetype.upper()
    im = Image.open(filepath)
    w = im.size[1]
    h = im.size[0]
    if max_width != None or max_height != None:
        whk = im.size[1]/im.size[0]
        if max_width != None and max_height != None:
            w = max_width
            h = max_height
        elif max_width != None:
            if max_width > im.size[1]:
                w = im.size[1]
            else:
                w = max_width
            h = w/whk
        else:
            if max_height > im.size[0]:
                h = im.size[0]
            else:
                h = max_height
            w = h * whk
    size = w, h
    im.thumbnail(size, Image.ANTIALIAS)
    im.save(filepath, filetype)


def img_app_resize_save(filepath):
    pass


def image_bytearray_to_img(bytearr):
    '''
    Transforma un array de bytes en una imagen
    '''
    # b = base64.b64decode(bytearr)
    img = Image.open(io.BytesIO(bytearr))
    outputIO = io.BytesIO()
    print('formato de img: ')
    print(img.format)
    # img.show()
    # img.save('holi123.png')

    img.save(outputIO, format=img.format, quality=100)

    return outputIO, img


def b64_to_img(imgb64,final_path, name=None, extension=None):
    # Decodifica la imagen base64
    image_data = base64.b64decode(imgb64.split(',')[1])

    file_path = ''
    if name is None or name == '':
        file_path = final_path
    else:
        file_path = '{}{}.{}'.format(final_path, name, extension)

    # Guarda la imagen en el servidor
    with open(file_path, 'wb') as f:
        f.write(image_data)


def image_get_content_file_from_bytearray(bytearr, file_path):
    # print('formato de img2: ')
    # print(img.getvalue())
    # print(img.format)
    img = Image.open(io.BytesIO(bytearr), mode='r')
    output_io = io.BytesIO()
    img.save(output_io, format=img.format, quality=100)
    file_path = '{}.{}'.format(file_path, img.format.lower())
    pathlib.Path(file_path).write_bytes(output_io.getbuffer().tobytes())
    return file_path

"""
verificar
def images_download(url, path):
    r = request.get(url, stream=True)

    if r.status_code == 200:
        with open(path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)

        im = Image.open(path)
        im.thumbnail(size, Image.ANTIALIAS)
        # im.save(thumbnail_path, "JPEG")
        im.save(path, "JPEG")
"""


"""
import sys
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
def compressImage(uploadedImage):
    imgdir = (settings.BASE_DIR + uploadedImage).replace(str(settings.MEDIA_URL), '\\').replace('/', '\\')
    print('img dir = ')
    print(imgdir)
    imageTemproary = Image.open(imgdir).replace('\\', '/')
    outputIoStream = BytesIO()
    imageTemproaryResized = imageTemproary.resize( (420,420) ) 
    imageTemproary.save(outputIoStream , format='JPEG', quality=60)
    outputIoStream.seek(0)
    uploadedImage = InMemoryUploadedFile(outputIoStream,'ImageField', "%s.jpg" % uploadedImage.name.split('.')[0], 'image/jpeg', sys.getsizeof(outputIoStream), None)
    return uploadedImage

"""
