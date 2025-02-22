from PySide2.QtCore import Qt
from PySide2.QtGui import QKeySequence, QIcon
import os

class GlobalParams:
    application_name = 'Knowledge Coil'
    #application_icon = QIcon('\\icons\\coil.png')

class CsvParams:
    SHIFT_TO_CONTENT = 3
    PICTURE_ROW = 1
    NAME_ROW = 0
    COMPLEX_KEY_DELIMITER = ':'


class KeyShortcuts:
    mouse_shorts = ('ML', 'MR')
    mouse_shorts_map = {
        'ML': 'MouseLeft',
        'MR': 'MouseRight'
    }
    MOUSE_LEFT = (Qt.MouseButton.LeftButton, 'MouseLeft', 'ML')
    MOUSE_RIGHT = (Qt.MouseButton.RightButton, 'MouseRight', 'MR')

    reserved_shortcuts = [QKeySequence.New, QKeySequence.Undo, QKeySequence.Redo]


def form_timer_label(minute, second):
    label = ''
    if minute < 10:
        label += '0' + str(minute)
    else:
        label += str(minute)
    label += ':'
    if second < 10:
        label += '0' + str(second)
    else:
        label += str(second)
    return label