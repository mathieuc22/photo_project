#!/usr/bin/env python3

from PIL import Image, ImageChops, ImageFile
from PIL.ExifTags import TAGS
from pathlib import Path
import shutil
import logging
import secrets

ImageFile.LOAD_TRUNCATED_IMAGES = True

# create logger with 'photo'
logger = logging.getLogger('photo')
logger.setLevel(logging.INFO)
# create file handler which logs even debug messages
fh = logging.FileHandler('photo.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

# set the path containing the images
source_path = Path('/srv/dev-disk-by-path-pci-0000-00-0c.0-part1/perso/Photos')
destination_path = Path('/srv/dev-disk-by-path-pci-0000-00-0c.0-part1/pictures')
dest_crap_path = destination_path.joinpath('processed','crap')
dest_other_path = destination_path.joinpath('processed','other')
dest_sort_path = destination_path.joinpath('processed','sort')
dest_crap_path.mkdir(parents=True, exist_ok=True)
dest_other_path.mkdir(parents=True, exist_ok=True)

# test if the file is an image
def is_image(imagename):
    try:
        i=Image.open(imagename)
        return True
    except IOError:
        return False

# test if duplicate image
def same_images(image_one,image_two):
    iOne = Image.open(image_one)
    iTwo = Image.open(image_two)
    diff = ImageChops.difference(iOne, iTwo)
    if diff.getbbox():
        return False
    else:
        return True

# set a unique filename
def get_filename(imagename):
    suffix = imagename.suffix
    path = imagename.parent
    size = imagename.stat().st_size
    name = imagename.name
    try:
        # read the image data using PIL
        with Image.open(imagename) as image:
            logger.info(f'file {imagename} is indeed an image, process the file')
            # extract EXIF data
            exifdata = image.getexif()
            # 306 - DateTime
            dt = exifdata.get(306)
            # 272 - Model
            md = exifdata.get(272)
            # get the filename
            # if no metadata keep the filename and send it to crap folder
            if dt == None or md == None:
                logger.warning(f'no metadata found in image {name}')
                # keep the original name plus the size of the file
                filename = name.replace(suffix,f'_{size}{suffix}')
                logger.debug(f'set the filename as {name}')
                # copy to crap folder
                shutil.copy(imagename, dest_crap_path.joinpath(filename))
                logger.debug(f'send {filename} to {dest_crap_path}')
            # else change the filename with metadata
            else:
                # add time and model to the a new name
                filename = f'{dt.replace(" ","").replace(":","")}_{md.replace(" ","")}_{size}{suffix}'
                # check path exist, path with year
                complete_path = dest_sort_path.joinpath(dt[0:4])
                complete_path.mkdir(parents=True, exist_ok=True)
                # test if file with new name already exists
                if complete_path.joinpath(filename).exists():
                    logger.warning(f'image with name {filename} already exists')
                    # test if it's a duplicate
                    if same_images(imagename,complete_path.joinpath(filename)):
                        # if duplicate do nothing
                        logger.warning(f'image {name} is a duplicate')
                        # set filename to none in order to exit loop later
                        filename=None
                        logger.warning(f'skip {name}')
                    else:
                        # if not real duplicate continue
                        logger.debug(f'image {name} is a not a duplicate')
                        filename = filename.replace(suffix,f'_{secrets.token_hex(2)}{suffix}')
                        logger.debug(f'change name from {name} to {filename}')
                if filename:
                    # copy the renamed image
                    shutil.copy(imagename, complete_path.joinpath(filename))
                    logger.debug(f'change name from {name} to {filename}')
                    logger.debug(f'send {filename} to {complete_path}')
            return True
    except IOError:
        logger.warning(f'file {imagename} is not an image')
        # if not an image try to copy the file to garbage directory with a new name
        filename = name.replace(suffix,f'_{size}{suffix}')
        try:
            # if not an image try to copy the file to garbage directory
            shutil.copy(imagename, dest_other_path.joinpath(filename))
            logger.debug(f'send {filename} to {dest_other_path}')
            logger.warning(f'file {imagename} processed')
        except IOError:
            logger.debug(f'skip {imagename}')
            logger.warning(f'file {imagename} not processed')
        return False

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

def main():
    # set a counter
    i = 0
    j = 0
    logger.info('- - - -')
    logger.info(f'start processing files in directory {source_path}')
    logger.info('- - - -')

    # loop through the directory (rglob for subsir)
    for file in source_path.rglob('*.*'):
        logger.info(f'start processing file {file}')
        logger.info(f'file number {i}')
        if get_filename(file):
            logger.info(f'file {file} processed')
            logger.info('- - - -')
            i = i + 1
        else:
            logger.info('- - - -')
            j = j + 1

    logger.info(f'{i} images processed, {j} other files skipped')

if __name__ == '__main__':
    main()