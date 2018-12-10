#!/usr/bin/env python3
import argparse
from multiprocessing import Pool
import os
import re
import sys
from datetime import datetime
from functools import partial
import exifread


DESCRIPTION = 'Arrange photos in folder and sub-folders by EXIF DateTimeOriginal from jpeg files.'
VERSION = '2.0 (9 dec 2018)' # '1.0 (2 may 2016)'
AUTHOR = 'USV'
EXTENSIONS = ('.jpg', '.jpeg')
EXIF_TAG_DATE = 'EXIF DateTimeOriginal'


def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


@singleton
class FolderChecker:
    def __init__(self):
        self.re_exclude = re.compile('[a-zA-Zа-яА-Я]')

    def can_process(self, folder):
        if self.re_exclude.search(folder):
            return False
        return True


class FileList:
    def __init__(self):
        self.file_list = []

    def __make_file_list__(self, path, photo_path):
        for root, dirs, files in os.walk(path):
            folder = os.path.basename(os.path.normpath(root))
            if (root == photo_path or FolderChecker().can_process(folder) == True):
                for dir in dirs:
                    self.__make_file_list__(dir, photo_path)
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in EXTENSIONS:
                        self.file_list.append(os.path.join(root, file))

    def make(self, path):
        self.file_list.clear()
        self.__make_file_list__(path, path)
        return self.file_list


def get_picture_date(file):
    dt_value = None
    try:
        f = open(file, 'rb')
        tags = exifread.process_file(f)
        ts = str(tags[EXIF_TAG_DATE]).strip().replace('-', ':')
        dt_value = datetime.strptime(ts, '%Y:%m:%d %H:%M:%S')
    except KeyError as e:
        raise e
    except IOError as e:
        raise e
    except:
        raise
    finally:
        f.close()
    return dt_value


def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def move_file(file, root, test):
    try:
        date = get_picture_date(file)
        folder_year = '%4d' % date.year
        folder_date = '%4d-%02d-%02d' % (date.year, date.month, date.day)
        file_name = os.path.basename(os.path.normpath(file))
        new_file = os.path.join(root, folder_year, folder_date, file_name)
        if (new_file != file):
            print(new_file)
            if (test == False):
                make_dir(os.path.join(root, folder_year))
                make_dir(os.path.join(root, folder_year, folder_date))
                os.rename(file, new_file)
    except KeyError:
        print('EXIF data not found in file', file)
    except IOError as e:
        print('I/O error({0}): {1}'.format(e.errno, e.strerror), file)
    except:
        print('Unexpected error ({}) while processing file {}'.format(sys.exc_info()[0], file))


def remove_empty_folders(path, test):
    for root, dirs, files in os.walk(path):
        for name in dirs:
            if os.listdir(os.path.join(root, name)):
                continue
            try:
                dir_to_remove = os.path.join(root, name)
                print("Remove an empty dir " + dir_to_remove)
                if (test == False):
                    os.removedirs(dir_to_remove)
            except:
                continue


def create_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION, epilog=AUTHOR, add_help=False)
    parser.add_argument('--path', '-p', action='store', help='Set path to photo\'s folder, by default using current path.')
    parser.add_argument('--test', '-t', action='store_true', help='Switch to test mode, without moving files and removing empty folders.')
    parser.add_argument('--version', action='version', version='%(prog)s {}'.format(VERSION), help='Get programm\'s version.')
    parser.add_argument('--help', action='help', help='Help.')
    return parser


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args()
    print(parser.description)
    print(namespace)

    start_time = datetime.now()

    path = os.path.abspath(namespace.path or '.')
    file_list = FileList().make(path)
    pool = Pool()
    pool.map(partial(move_file, root = path, test = namespace.test), file_list)
    remove_empty_folders(path, namespace.test)

    finish_time = datetime.now()
    print('overall time', finish_time - start_time)
