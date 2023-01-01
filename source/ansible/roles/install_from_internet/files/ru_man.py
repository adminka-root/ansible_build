#!/usr/bin/env python3

import urllib.request, json
import tarfile
import os
import shutil
import subprocess
from datetime import datetime

def get_link_for_download(link):
    with urllib.request.urlopen(link) as url:
        best_release = json.load(url)
    return best_release['release']['url']

def extract_bz2(file, path="."):
    with tarfile.open(file, "r:bz2") as tar:
        tar.extractall(path)

def make_tarfile(output_file, source_dir):
    with tarfile.open(output_file, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

def recursive_chown(path, user, group, rwx):
    for dir_path, dir_names, file_names in os.walk(path):
        shutil.chown(dir_path, user, group)
        for file_name in file_names:
            file = os.path.join(dir_path, file_name)
            shutil.chown(file, user, group)
            os.chmod(file, int(rwx, base=8))


if __name__ == "__main__":
    link = get_link_for_download('https://sourceforge.net/projects/man-pages-ru/best_release.json')
    file = '/tmp/man_ru.tar.bz2'
    urllib.request.urlretrieve(link, file)
    unpack_dir = os.path.join(os.path.dirname(file), 'man')
    extract_bz2(file, unpack_dir)
    # например, man_dir = /tmp/man/man-pages-ru_5.03-2390-2390-20191017
    man_dir = [f.path for f in os.scandir(unpack_dir) if f.is_dir()][0]
    man_dir_system = "/usr/share/man/ru"  # без окончательного /
    backup_postfix = datetime.now().strftime("%d_%m_%y_(%H:%M:%S)")
    if os.path.isdir(man_dir_system):
        backup_file = os.path.join(os.path.dirname(man_dir_system), 'ru_' + backup_postfix + '.tar.gz')
        make_tarfile(backup_file, man_dir_system)
    recursive_chown(man_dir, 'root', 'root', '644')
    os.makedirs(man_dir_system, exist_ok=True)
    # shutil.copytree(man_dir, man_dir_system, dirs_exist_ok=True)  # 3.8+ only!
    # alt way with files
    for dir in os.listdir(man_dir):
        subprocess.call(['cp', '-r', os.path.join(man_dir, dir), man_dir_system])
