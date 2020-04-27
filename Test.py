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
    return filtered_map

class Combination:

    def __init__(self, csv_path=None):
        self.full_combination = list()
        self.commands = list()

        self.name = 'name'
        self.picture_path = 'path'

        if csv_path:
            self.parse_action(csv_path)

    def parse_action(self, path):
        with open(path, newline='') as action_file:
            reader = csv.reader(action_file, delimiter=',', quotechar='|')
            data = list(reader)

            self.name = data[CsvParams.NAME_ROW][1]
            self.picture_path = data[CsvParams.PICTURE_ROW][1]

            for keyboard_key, command in data[CsvParams.SHIFT_TO_CONTENT:]:
                full_key = None
                try:
                    full_key = QKeySequence(int(keyboard_key))
                except ValueError:
                    full_key = tuple(QKeySequence(int(part_key)) for part_key in keyboard_key.split(':'))

                if command and command != 'None':
                    self.commands.append(command)
                else:
                    self.commands.append(None)

                self.full_combination.append(full_key)

    def remap_keys(self, settings=dict()):
        id = 0
        for command in self.commands:
            if command:
                new_key_action = settings.get(command, False)
                if new_key_action:
                    self.full_combination[id] = new_key_action
            id += 1

def main():
    c = Combination('actions//real_test.csv')
    print (c.full_combination)
    print (c.commands)
    c.remap_keys(parse_settings_xml('levin.xml'))
    print(c.full_combination)

if __name__ == '__main__':
    main()