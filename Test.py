import csv

from PySide2.QtCore import Qt
from PySide2.QtGui import QKeySequence
import xml.etree.ElementTree as et
from global_params import CsvParams, KeyShortcuts

def hex_to_modifiers(hex_key):
    tab = {
        '09' : Qt.CTRL,
        '11' : Qt.ALT,
        '05' : Qt.SHIFT,
        '0d' : Qt.CTRL + Qt.SHIFT,
        '19' : Qt.CTRL + Qt.ALT,
        '15' : Qt.ALT + Qt.SHIFT,
        '01' : 0
    }
    return tab.get(hex_key, -1)

def hex_to_sequence(keys):
    result = dict()
    for key, value in keys.items():
        if len(value) == 1:
            result[key] = QKeySequence(value)
        elif value.startswith('hex'):
            hex_keys = value[value.index(':')+1:]
            hex_split = hex_keys.split(',')
            full_key = hex_to_modifiers(hex_split[4])
            if full_key != -1:
                full_key += int(hex_split[6], 16)
                hex_split = QKeySequence(full_key)
            result[key] = hex_split
        else:
            result[key] = tuple(QKeySequence(ord(key)) for key in value)
    return result


def parse_settings_xml(xml_path):
    tree = et.parse(xml_path)
    root = tree.getroot()
    key_leaf = [elem for elem in root[1].iter('Value')]
    key_values = [key_value.text for key_value in key_leaf][1:]
    key_values = list(map(lambda kv: kv.replace('"', ''), key_values))

    key_map = dict()
    for key_value in key_values:
        key_value = key_value.split('=')
        if len(key_value) == 2:
            key_map[key_value[0]] = key_value[1]

    filtered_map = {k : v for k, v in hex_to_sequence(key_map).items() if v}
    for key, value in filtered_map.items():
        print (key, value)

class Combination:

    def __init__(self, csv_path=None):
        self.full_combination = tuple()
        self.combination_sequence =dict()
        self.commands = dict()

        self.name = 'name'
        self.picture_path = 'path'

        if csv_path:
            self.parse_action(csv_path)

    def parse_action(self, path):
        with open(path, newline='') as action_file:
            reader = csv.reader(action_file, delimiter=',', quotechar='|')
            data = list(reader)

            iter_pos = 0
            combination = list()
            for keyboard_key, command in data[CsvParams.SHIFT_TO_CONTENT:]:
                if command and command != 'None':
                    self.commands[command] = iter_pos

                full_key = None
                try:
                    full_key = QKeySequence(int(keyboard_key))
                except ValueError:
                    full_key = tuple(QKeySequence(ord(part_key)) for part_key in keyboard_key)

                combination.append(full_key)
                iter_pos += 1

            self.full_combination = tuple(combination)
            self.name = data[CsvParams.NAME_ROW][1]
            self.picture_path = data[CsvParams.PICTURE_ROW][1]

    def get_key_by_pos(self):
        res = dict()
        for k, v in self.commands.items():
            res[k] = self.full_combination[v]
        return res

    def remap_keys(self, settings):


def main():
    c = Combination('actions//test.csv')
    print (c.full_combination)
    print (c.commands)
    print (c.get_key_by_pos())
    parse_settings_xml('levin.xml')

if __name__ == '__main__':
    main()

'''
AppPreviousViewCmd ['06', '00', '00', '00', '01', '00', '74', '00', 'b4', '60'] F5
AppNextViewCmd     ['06', '00', '00', '00', '05', '00', '74', '00', '98', '60'] Shift+F5
74 - 5
'''