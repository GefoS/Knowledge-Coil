from xml.etree import ElementTree as et

from PySide2.QtCore import Qt
from PySide2.QtGui import QKeySequence


# def hex_to_sequence(keys):
#     result = dict()
#     for key, value in keys.items():
#         if len(value) == 1:
#             result[key] = QKeySequence(value)
#         elif value.startswith('hex'):
#             hex_keys = value[value.index(':')+1:]
#             hex_split = hex_keys.split(',')
#             full_key = hex_to_modifiers(hex_split[4])
#             if full_key != -1:
#                 full_key += int(hex_split[6], 16)
#                 hex_split = QKeySequence(full_key)
#             result[key] = hex_split
#         else:
#             result[key] = tuple(QKeySequence(ord(key)) for key in value)
#     return result


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


def hex_to_key(key:str):
    if not key.startswith('hex'):
        return key
    else:
        hex_sequence = key.replace('hex:', '').split(',')
        full_key = hex_to_modifiers(hex_sequence[4])
        if full_key != -1:
            full_key += int(hex_sequence[6], 16)

        return QKeySequence(full_key).toString()

def parse_settings_xml(xml_path):
    tree = et.parse(xml_path)
    root = tree.getroot()
    key_leaf = [elem for elem in root[1].iter('Value')]
    key_values = [key_value.text for key_value in key_leaf][1:]
    key_values = list(map(lambda kv: kv.replace('"', ''), key_values))

    #key_keyboarda -> command or list of commands
    key_map = dict()
    for key_value in key_values:
        command, key = key_value.split('=')
        if isinstance(key, str) and (isinstance(command, str) or isinstance(command, list)):
            existing_command = key_map.pop(key, False)
            if not existing_command:
                key_map[key] = command
            else:
                if isinstance(existing_command, list):
                    key_map[key] = existing_command + [command]
                else:
                    key_map[key] = [existing_command, command]

    key_map.pop('', False)
    filtered_key_map = {hex_to_key(key):command for key, command in key_map.items()}
    return filtered_key_map