#!/usr/bin/env python3

import os
import sys
import yaml
import subprocess


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


if __name__ == "__main__":
    script_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    yml_data = load_yml(os.path.join(script_dir, 'schema.yml'))

    gsettings = recursive_traversal(yml_data['gsettings'])
    gsettings = list(map(lambda x: x.split('🎄'), gsettings))

    if True:  # meld-ом можно сравнить и выставить предпочитаемые значения
        for line in gsettings:
            print(f"gsettings set {line[0]} {line[1]} \"{line[2]}\"")
    if True:  # get sys values
        print('\n\n----- get sys values -------')
        value_t = []
        for line in gsettings:  # bad --> "' !!!
            result = subprocess.check_output(['gsettings', 'get', line[0], line[1]], universal_newlines=True).replace('\n', '')
            value_t.append(
                    f"gsettings set {line[0]} {line[1]} \"{result}\""
            )
            print(*value_t[len(value_t)-1:])

    #for line in gsettings:
    #    for value in line:
    #        print('\t', value)
    #    print('-----')

