import os
import sys
from PIL import Image

def get_size_mb(filepath):
    file_stats = os.stat(filepath)
    return file_stats.st_size / (1024 * 1024)


def compressMe(filepath, MAX_SIZE_MB = 0.3, BASE_QUALITY=60):
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
    # return
    
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
                        optimize = True, 
                        quality = quality)
        file_size = get_size_mb(filepath)
        if file_size > MAX_SIZE_MB:
            if quality <= 10:
                quality = quality - 2
            else:
                quality = quality - 10
            if quality <=2:
                os.remove(original_filepath_renamed)
                return
            os.remove(filepath)
        print('{}, el nuevo tam es: {}, quality: {}'.format(format_img, file_size, quality))
    os.remove(original_filepath_renamed)
    return
  
# Define a main function
def main():
    
    verbose = False
      
    # checks for verbose flag
    if (len(sys.argv)>1):
        
        if (sys.argv[1].lower()=="-v"):
            verbose = True
                      
    # finds current working dir
    cwd = os.getcwd()
  
    formats = ('jpg', 'jpeg', 'png')
      
    # looping through all the files
    # in a current directory
    for file in os.listdir(cwd):
        file_type = os.path.splitext(file)[1].lower()[1:]

        # If the file format is JPG or JPEG
        if file_type in formats:
            print('compressing', file)
            filepath = os.path.join(os.getcwd(), file)

            compressMe(filepath)
  
    print("Done")
  
# Driver code
if __name__ == "__main__":
    main()
