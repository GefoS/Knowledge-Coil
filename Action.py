import csv, warnings

import SettingsParser
from global_params import CsvParams, KeyShortcuts
from PySide2.QtGui import QKeySequence

def flatten_map_to_combination(full_combination, key_map):
    def flatten(object):
        for item in object:
            if isinstance(item, (list, tuple, set)):
                yield from flatten(item)
            else:
                yield item
    rebuilt_map = list()
    for comb_key, comb_command in full_combination:
        for commands, set_key in key_map.items():
            if comb_command in commands:
                comb_key = set_key
        rebuilt_map.append(comb_key)
    return list(flatten(rebuilt_map))

def sequence_to_key(sequence:QKeySequence):
    str_sequence = sequence.__str__()
    key_list = str_sequence.replace(')', '').split('(')[-1].split(',')
    filtered_list = [int(key) for key in key_list if int(key) > 0]
    if len(filtered_list) > 1:
        warnings.warn('Complex key defined', source=key_list)
    else:
        return filtered_list[0]

def complex_key_to_tuple(key:str):
    if key in KeyShortcuts.mouse_shorts:
        return key
    if len(key) == 1:
        return (ord(key),)
    elif ':' in key:
        return tuple(ord(k) for k in key.split(':'))
    else:
        seq = sequence_to_key(QKeySequence(key))
        return (seq,)

class KeyAction:
    def __init__(self, action_path:str, settings:dict):
        key_map = settings
        with open(action_path, newline='') as action_file:
            reader = csv.reader(action_file, delimiter=',', quotechar='|')
            data = list(reader)

        self.name = action_path.split('/')[-1]
        self.picture_path = data[CsvParams.PICTURE_ROW][1]
        full_combination = [[complex_key_to_tuple(k), v] for k, v in data[CsvParams.SHIFT_TO_CONTENT:]]
        self.combination = flatten_map_to_combination(full_combination, key_map)

if __name__ == '__main__':
    lebanon_settings = SettingsParser.parse_to_key_combination('users/lebanon/default_settings.xml')
    for k, v in lebanon_settings.items():
        if len(v) > 4:
            print (k, v)
    levin_settings = SettingsParser.parse_to_key_combination('users/levin/levin.xml')
    for k, v in levin_settings.items():
        if len(v) > 4:
            print (k, v)

    #lebanon = KeyAction('actions/triangle_levin.csv', lebanon_settings)
    #levin = KeyAction('actions/triangle_default.csv', levin_settings)
    #print(levin.combination)