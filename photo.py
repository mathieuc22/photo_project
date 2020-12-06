from PIL import Image, ImageChops
from PIL.ExifTags import TAGS
from pathlib import Path
import shutil

source_path = Path('/Users/mathieu/Pictures/')

def is_image(imagename):
    try:
        i=Image.open(imagename)
        return True
    except IOError:
        return False

def get_filename(imagename):
    p = Path(imagename)
    suffix = p.suffix
    path = p.parent
    # read the image data using PIL
    with Image.open(imagename) as image:
        # extract EXIF data
        exifdata = image.getexif()
        # 306 - DateTime
        dt = exifdata.get(306)
        # 272 - Model
        md = exifdata.get(272)
        # get the filename
        if dt == None or md == None:
            filename = imagename.name
            shutil.copy(imagename, source_path.joinpath('processed','crap', filename))
        else:
            filename = f'{dt.replace(" ","").replace(":","")}{md.replace(" ","")}{Path(imagename).stat().st_size}{suffix}'
            if is_image(path.joinpath(filename)):
                if same_images(imagename,path.joinpath(filename)):
                    filename = f'{imagename.name}.dupli' 
                else:
                    filename = f'{filename}.other'
            # check path exist, path with year
            shutil.copy(imagename, source_path.joinpath('processed','sort', filename))
        print(filename)

def get_all_exif():
    # iterating over all EXIF data fields
    for tag_id in exifdata:
        # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        data = exifdata.get(tag_id)
        # decode bytes 
        if isinstance(data, bytes):
            if len(data)<100:
                data = data.decode()
            else:
                data =""
        print(f"{tag:25}: {data}")

def same_images(image_one,image_two):
    iOne = Image.open(image_one)
    iTwo = Image.open(image_two)
    diff = ImageChops.difference(iOne, iTwo)
    if diff.getbbox():
        return False
    else:
        return True

i = 0
for file in source_path.glob('*.*'):
    if is_image(file):
        i = i + 1
        get_filename(file)
print(f'{i} images processed')
