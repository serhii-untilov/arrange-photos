#!/usr/bin/env python
import os
import os.path
import re
from datetime import datetime, time

import exifread

EXTENSIONS = ('.jpg', '.jpeg')

# what tags use to redate file (use first found)
# DT_TAGS = ["Image DateTime", "EXIF DateTimeOriginal", "DateTime"]
DT_TAGS = ["EXIF DateTimeOriginal"]

PATH = '/media/combox/Фото'


def get_exif_date(path_file):
    dt_value = None
    f = open(path_file, 'rb')
    try:
        tags = exifread.process_file(f)
        for tag in DT_TAGS:
            try:
                ts = str(tags[tag]).strip().replace('-', ':')
                # dt_value = datetime.strptime(ts + 'UTC', "%Y:%m:%d %H:%M:%S%Z")
                dt_value = datetime.strptime(ts, '%Y:%m:%d %H:%M:%S')
                break
            except:
                continue
        if dt_value:
            return dt_value
    finally:
        f.close()
    return None


def make_path_file(root, path_file):
    dt_value = get_exif_date(path_file)
    new_path_file = path_file
    if dt_value:
        dir_year = '%4d' % dt_value.year
        dir_date = '%4d-%02d-%02d' % (dt_value.year, dt_value.month, dt_value.day)
        head, tail = os.path.split(path_file)
        new_path_file = os.path.join(root, dir_year, dir_date, tail)
    return new_path_file


def compare_path_file(new_path_file, old_path_file):
    return new_path_file == old_path_file


def move_file(root, path_file):
    new_path_file = make_path_file(root, path_file)
    if not compare_path_file(new_path_file, path_file) \
            and not os.path.isfile(new_path_file):
        try:
            new_dir = os.path.dirname(new_path_file)
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)
            if os.path.exists(new_dir):
                #os.rename(path_file, new_path_file)
                print('moved', path_file, new_path_file)
                return 1
        except:
            print('failed', path_file, new_path_file)
    return 0


def move_photos(path_name):
    start_time = datetime.now()
    count_all = 0
    count_moved = 0
    #p = re.compile('[a-zа-я]', flags=re.IGNORECASE | re.LOCALE)
    p = re.compile('[a-zA-Zа-яА-Я]')
    for root, dirs, files in os.walk(path_name):
        for name in files:
            count_all += 1
            head, ext = os.path.splitext(name)
            if ext.lower() in EXTENSIONS:
                if not p.search(root[len(path_name):]):
                    count_moved += move_file(path_name, os.path.join(root, name))
    finish_time = datetime.now()
    print("--------")
    print("start at ", start_time)
    print("finish at ", finish_time)
    print("overall time", finish_time - start_time)
    print(count_all, ' files in tree')
    print(count_moved, ' moved files')

def delete_empty_dirs(path_name):
    for root, dirs, files in os.walk(path_name):
        for name in dirs:
            if os.listdir(name) = "":
                print('directory is empty', name)


if __name__ == '__main__':
    #move_photos(PATH)
    delete_empty_dirs(PATH)
