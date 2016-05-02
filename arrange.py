#!/usr/bin/env python3
import sys
import argparse
import os
import os.path
import re
from datetime import datetime

import exifread


DESCRIPTION = 'Arrange photo\'s folder by EXIF DateTimeOriginal from jpeg files.'
VERSION = '1.0 (2 may 2016)'
AUTHOR = 'USV'
EXTENSIONS = ('.jpg', '.jpeg')
DT_TAGS = ['EXIF DateTimeOriginal']


class PhotoFolder:

    def __init__(self, path):
        self.path = path
        self.is_test = True
        self.is_verbose = True
        self.skip_folder_template = None
        self.count_folders = 0
        self.count_files = 0
        self.count_removed_folders = 0
        self.count_moved_files = 0

    def get_exif_date(self, path_file):
        dt_value = None
        try:
            f = open(path_file, 'rb')
            try:
                tags = exifread.process_file(f)
                for tag in DT_TAGS:
                    try:
                        ts = str(tags[tag]).strip().replace('-', ':')
                        dt_value = datetime.strptime(ts, '%Y:%m:%d %H:%M:%S')
                        break
                    except:
                        continue
                if dt_value:
                    return dt_value
                if self.is_verbose:
                    print('tag not found', path_file)
            finally:
                f.close()
        except IOError as e:
            if self.is_verbose:
                print('I/O error({0}): {1}'.format(e.errno, e.strerror), path_file)
        except:
            if self.is_verbose:
                print('failed to open', path_file, 'Unexpected error:', sys.exc_info()[0])
            raise
        return None

    def make_path_file(self, path_file):
        dt_value = self.get_exif_date(path_file)
        new_path_file = path_file
        if dt_value:
            dir_year = '%4d' % dt_value.year
            dir_date = '%4d-%02d-%02d' % (dt_value.year, dt_value.month, dt_value.day)
            head, tail = os.path.split(path_file)
            new_path_file = os.path.join(self.path, dir_year, dir_date, tail)
        return new_path_file

    def move_file(self, path_file):
        new_path_file = self.make_path_file(path_file)
        if new_path_file != path_file and not os.path.isfile(new_path_file):
            try:
                new_dir = os.path.dirname(new_path_file)
                if not os.path.exists(new_dir):
                    os.makedirs(new_dir)
                if not self.is_test:
                    os.rename(path_file, new_path_file)
                if self.is_verbose:
                    print('moved', path_file, new_path_file)
                return 1
            except:
                if self.is_verbose:
                    print('failed', path_file, new_path_file)
        return 0

    def move_photos(self):
        for root, dirs, files in os.walk(self.path):
            for name in files:
                self.count_files += 1
                head, ext = os.path.splitext(name)
                if ext.lower() in EXTENSIONS:
                    if not self.skip_folder_template.search(root[len(self.path):]):
                        self.count_moved_files += self.move_file(os.path.join(root, name))

    def remove_empty_folders(self):
        for root, dirs, files in os.walk(self.path):
            for name in dirs:
                self.count_folders += 1
                if os.listdir(os.path.join(root, name)):
                    continue
                try:
                    if not self.is_test:
                        os.removedirs(os.path.join(root, name))
                    self.count_removed_folders += 1
                    if self.is_verbose:
                        print('folder removed', os.path.join(root, name))
                except:
                    continue


def create_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION, epilog=AUTHOR, add_help=False)
    parser.add_argument('--path', '-p', action='store')
    parser.add_argument('--test', '-t', action='store_true', help='switch to test mode')
    parser.add_argument('--verbose', '-v', action="store_true", help='increase output verbosity')
    parser.add_argument('--version', action='version', version='%(prog)s {}'.format(VERSION))
    return parser


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args()
    print(parser.description)
    print(namespace)

    start_time = datetime.now()
    photo_folder = PhotoFolder(os.path.abspath(namespace.path or '.'))
    print('path', photo_folder.path)
    photo_folder.is_test = namespace.test
    photo_folder.is_verbose = namespace.verbose
    photo_folder.skip_folder_template = re.compile('[a-zA-Zа-яА-Я]')  # for skip commented folders
    photo_folder.move_photos()
    photo_folder.remove_empty_folders()
    finish_time = datetime.now()

    print('start at', start_time)
    print('finish at', finish_time)
    print('overall time', finish_time - start_time)
    print(photo_folder.count_files, 'files')
    print(photo_folder.count_moved_files, 'files moved')
    print(photo_folder.count_folders, 'folders')
    print(photo_folder.count_removed_folders, 'folders removed')
