#!/usr/bin/env python3

# Скрипт для интеграции настроек панели в системы
# 1. Считывает схему schema.yml, где указаны настройки панели такие как: количество, взаимное расположение,
#    настройки скрытия, задержки и т.д., а также, возможно, расположение конфигов (для динамических апплетов).
#    Динамическими наз-ся те апплеты, которые в зависимости от расположения на панели (глобального порядкого id)
#    считывают тот или иной конфиг. Так, например, апплет календарь, который добавили 10-м по счету (среди всех
#    апплетов) будет иметь конфиг 10.json в соответствующей папке calendar@cinnamon.org.
# 2. На основе считанных данных формирует gsettings команды, а также производит копирование статических и дина-
#    мических конфигов, указанных в to_import_config['static_applets'] и to_import_config['dynamic_applets'].
#    Если для очередного апплета из to_import_config явно не задан конфиг, в соответствующей папке ищется
#    конфиг, имеющий название апплета. Например, spacer@cinnamon.org/spacer@cinnamon.org.json. Или
#    pomodoro@gregfreeman.org/pomodoro@gregfreeman.org.json
# 3. Копирует папки local и locale в соответствующие расположения
# 4. Применяет gsetting команды

import os
import sys
import yaml
import shutil
import subprocess


def load_yml(file: str):
    with open(file, "r") as yml_file:
        try:
            return yaml.safe_load(yml_file)
        except yaml.YAMLError as exc:
            raise Exception(f"\n\nОшибка! {exc}")


if __name__ == "__main__":

    script_dir = os.path.abspath(os.path.dirname(sys.argv[0]))  # '/tmp/cinnamon_applets/'
    using_dirs = {
        'config': {
            'source': os.path.join(script_dir, 'configs'),
            'dest': os.path.expanduser('~/.config/cinnamon/spices/')  # in 19.3 = ~/.cinnamon/configs/ (но это не точно)
        },
        'local': {
            'source': os.path.join(script_dir, 'local'),
            'dest': os.path.expanduser('~/.local/share/cinnamon/applets/')
        },
        'locale': {
            'source': os.path.join(script_dir, 'locale'),
            'dest': os.path.expanduser('~/.local/share/locale/ru/LC_MESSAGES/')
        }
    }

    yml_data = load_yml(os.path.join(script_dir, 'schema.yml'))

    panel_priority = dict()
    for panel in yml_data['panels_settings']:  # {'1': 'panel_1', '2', panel_2, ...}
        panel_priority[str(yml_data['panels_settings'][panel]['num'])] = panel

    gsettings = {  # например,
        'panels-enabled': [],  # "['1:0:bottom', '2:0:left', '3:1:bottom', '4:1:right']"
        'panels-autohide': [],  # "['1:false', '2:true', '3:false', '4:true']"
        'panels-hide-delay': [],  # "['1:0', '2:200', '3:0', '4:200']"
        'panels-show-delay': [],  # "['1:0', '2:750', '3:0', '4:750']"
        'panels-height': [],  # "['1:40', '2:48', '3:40', '4:48']"
        'enabled-applets': [],  # "['current_panel_g:LRC:applet_pos_relative:applet:applet_pos_absolute', ...]"
        'no-adjacent-panel-barriers': 'true',  # пропускать курсор через панели к мониторам
        'panel-zone-icon-sizes': []
    }

    # определение enabled-applets и копирование конфигов
    applet_pos_absolute = 0
    not_find_configs = []
    want_import = yml_data['to_import_config']['dynamic_applets'] + yml_data['to_import_config']['static_applets']
    for num in range(1, len(panel_priority) + 1):
        current_panel = panel_priority[str(num)]  # panel_1
        current_panel_g = 'panel' + str(num)  # panel1

        for LRC in yml_data['panels'][current_panel]:  # Left/Right/Center (LRC)
            applet_pos_relative = 0
            for applet in yml_data['panels'][current_panel][LRC]:
                if type(applet) != dict:
                    applet_config = applet + '.json'
                else:
                    applet_config = applet['config']
                    applet = applet['name']

                tmp_f_path_config = os.path.join(using_dirs['config']['source'], applet, applet_config)
                if os.path.isfile(tmp_f_path_config):
                    dest_dir = os.path.join(using_dirs['config']['dest'], applet)
                    os.makedirs(dest_dir, exist_ok=True)

                    if applet in yml_data['to_import_config']['dynamic_applets']:
                        dest_file = os.path.join(dest_dir, str(applet_pos_absolute) + '.json')
                        shutil.copy(tmp_f_path_config, dest_file)
                    elif applet in yml_data['to_import_config']['static_applets']:
                        dest_file =   os.path.join(dest_dir, str(applet) + '.json')  # os.path.join(dest_dir, applet_config)
                        shutil.copy(tmp_f_path_config, dest_file)
                elif applet in want_import:
                    not_find_configs.append({'applet': applet, 'path': tmp_f_path_config})

                gsettings['enabled-applets'].append(
                    f"{current_panel_g}:{LRC}:{applet_pos_relative}:{applet}:{applet_pos_absolute}"
                )
                applet_pos_absolute += 1
                applet_pos_relative += 1

    if len(not_find_configs) > 0:
        print('Предупреждение! Не удалось найти конфиги для:\n', not_find_configs)

    # нахождение остальные параметров
    for num in range(1, len(panel_priority) + 1):
        current_panel = panel_priority[str(num)]  # panel_1
        gsettings['panels-enabled'].append(
            f"{num}:{yml_data['panels_settings'][current_panel]['monitor']}:{yml_data['panels_settings'][current_panel]['position']}"
        )
        gsettings['panels-autohide'].append(f"{num}:{yml_data['panels_settings'][current_panel]['hidden']}")
        gsettings['panels-hide-delay'].append(f"{num}:{yml_data['panels_settings'][current_panel]['hide_delay']}")
        gsettings['panels-show-delay'].append(f"{num}:{yml_data['panels_settings'][current_panel]['show_delay']}")
        gsettings['panels-height'].append(f"{num}:{yml_data['panels_settings'][current_panel]['height']}")
        gsettings['panel-zone-icon-sizes'].append(
            {
                'panelId': num, 
                'left': yml_data['panels_settings'][current_panel]['icon_sizes']['left'],
                'center': yml_data['panels_settings'][current_panel]['icon_sizes']['center'],
                'right': yml_data['panels_settings'][current_panel]['icon_sizes']['right']
            }
        )
    gsettings['next-applet-id'] = applet_pos_absolute + 1

    for dirs in [using_dirs['local'], using_dirs['locale']]:
        os.makedirs(dirs['dest'], exist_ok=True)
        subprocess.call(['cp', '-r', dirs['source']+'/.', dirs['dest']])

    # установка схем
    for schema in gsettings:
        subprocess.call(                                                   # for panel-zone-icon-sizes
            ['gsettings', 'set', 'org.cinnamon', schema, str(gsettings[schema]).replace('\'', '"')]
        )
