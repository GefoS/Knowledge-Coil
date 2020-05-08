from PySide2.QtCore import Qt
from PySide2.QtGui import QKeySequence


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
