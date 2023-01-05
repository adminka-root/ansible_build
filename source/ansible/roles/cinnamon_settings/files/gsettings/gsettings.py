#!/usr/bin/env python3

import os
import sys
import yaml
import subprocess
from datetime import datetime


def load_yml(file: str):
    with open(file, "r") as yml_file:
        try:
            return yaml.safe_load(yml_file)
        except yaml.YAMLError as exc:
            raise Exception(f"\n\nОшибка! {exc}")


# в качестве альтернативы можно адаптировать код отсюда
# https://stackoverflow.com/questions/39198489/get-path-of-all-the-elements-in-dictionary
def recursive_traversal(data, accumulation=''):
    previous = []
    for key in data.keys():
        if type(data[key]) != dict:
            previous.append(accumulation[1:] + '🎄' + key + '🎄' + str(data[key]))
            continue
        previous += recursive_traversal(data[key], accumulation + '.' + key)
    return previous


def save_file(save_to: str, data, time_postfix=False):
    save_to_dir = os.path.dirname(save_to)
    os.makedirs(save_to_dir, exist_ok=True)
    if time_postfix:
        backup_postfix = datetime.now().strftime("%d_%m_%y_(%H:%M:%S)")
        save_to_file = os.path.basename(save_to).split('.')
        ext = ''
        if len(save_to_file[1:]) > 0:
            ext = '.' + '.'.join(save_to_file[1:])
        save_to_file = save_to_file[0] + '_' + backup_postfix + ext
        save_to = os.path.join(save_to_dir, save_to_file)

    with open(save_to, 'w') as file:
        if type(data) == list:
            data = '\n'.join(data)
        file.write(data)


def show_list(data: list, message=''):  # , stdout=False
    if message:
        print('\n' + message)
    for line in data:
        print(line)


def get_system_values(gsettings: "list of list"):
    """return list of str (gsettings set schema, ..., ...)"""
    result_list = []

    for line in gsettings:
        try:
            result_line = subprocess.check_output(
                ['gsettings', 'get', line[0], line[1]], universal_newlines=True
            ).replace('\n', '')

            if result_line[0] + result_line[-1] == "''":
                result_line = '"' + result_line[1:-1] + '"'
            elif result_line[0] + result_line[-1] != '""':
                result_line = '"' + result_line + '"'

            result_list.append(
                f"gsettings set {line[0]} {line[1]} {result_line}"
            )
        except subprocess.CalledProcessError:
            pass
    return result_list


def get_py_values(gsettings: "list of list"):
    """return list of str (gsettings set schema, ..., ...)"""
    result_list = []
    for line in gsettings:
        result_list.append(f"gsettings set {line[0]} {line[1]} \"{line[2]}\"".replace('\t', '\\t'))
    return result_list


def save_sys_and_py_gsettings_to_file(gsettings: "list of list", show=False):
    system_values = get_system_values(gsettings)
    save_file(
        os.path.join(script_dir, 'logs', 'gsettings_sys.txt'),
        system_values,
        time_postfix=True
    )

    py_values = get_py_values(gsettings)
    save_file(
        os.path.join(script_dir, 'logs', 'gsettings_py.txt'),
        py_values,
        time_postfix=True
    )

    if show:
        show_list(system_values, "Соответствующие системные переменные:")
        show_list(py_values, "Соответствующие новые переменные:")


if __name__ == "__main__":
    script_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    yml_data = load_yml(os.path.join(script_dir, 'schema.yml'))

    gsettings = recursive_traversal(yml_data['gsettings'])
    gsettings = list(map(lambda x: x.split('🎄'), gsettings))
    save_sys_and_py_gsettings_to_file(gsettings, show=False)

    # get_error = False
    for line in gsettings:
        try:
            subprocess.check_output(
                ['gsettings', 'set', line[0], line[1], line[2]], universal_newlines=True
            ).replace('\n', '')
        except subprocess.CalledProcessError:
            get_error = True

    # if get_error:
    #     raise Exception('Отсутствуют пути для указанных схем!')

