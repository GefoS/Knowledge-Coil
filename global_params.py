from PySide2.QtCore import Qt


class CsvParams:
    SHIFT_TO_CONTENT = 3
    PICTURE_ROW = 1


class KeyShortcuts:
    MOUSE_LEFT = (Qt.MouseButton.LeftButton, 'MouseLeft', 'ML')
    MOUSE_RIGHT = (Qt.MouseButton.RightButton, 'MouseRight', 'MR')

    CTRL = (Qt.Key_Control, 'CT')
    SHIFT = (Qt.Key_Shift, 'SF')
    ALT = (Qt.Key_Alt, 'ALT')
    TAB = (Qt.Key_Tab, 'TB')
    ENTER = (Qt.Key_Return, 'EN')
    BACKSPACE = (Qt.Key_Backspace, 'BK')

    service_keys = {
        'CT': Qt.Key_Control,
        'SF': Qt.Key_Shift,
        'ALT': Qt.Key_Alt,
        'TB': Qt.Key_Tab,
        'EN': Qt.Key_Return,
        'BK': Qt.Key_Backspace
    }

    '''self.current_combination = {
                'L': None,
                'ML': None,
                '2': None,
                '1': None,
                'EN': None
            }'''