import sys, csv, datetime, warnings
import xml.etree.ElementTree as et

from PySide2 import QtXml, QtGui, QtCore
from PySide2.QtGui import QKeySequence
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QPushButton, QLabel, QPlainTextEdit, QMainWindow
from PySide2.QtCore import QFile, QObject, QTimer, SIGNAL, QLine, QEvent, Qt

from global_params import CsvParams, KeyShortcuts


def hook_mouse_event(event):
    if event.button() == Qt.MouseButton.LeftButton:
        return (KeyShortcuts.MOUSE_LEFT[1] + '\n')
    elif event.button() == Qt.MouseButton.RightButton:
        return (KeyShortcuts.MOUSE_RIGHT[1] + '\n')

def invert_mouse_event(event):
    if event.button() == Qt.MouseButton.LeftButton:
        return KeyShortcuts.MOUSE_LEFT[2]
    elif event.button() == Qt.MouseButton.RightButton:
        return KeyShortcuts.MOUSE_RIGHT[2]

def hook_key_event(event):
    key = event.key()

    if key == Qt.Key_unknown:
        warnings.warn("Unknown key from a macro probably")
        return True

    if key in (Qt.Key_Shift, Qt.Key_Control, Qt.Key_Alt, Qt.Key_Meta):
        return True

    modifiers = event.modifiers()
    if modifiers & QtCore.Qt.ShiftModifier:
        key += QtCore.Qt.SHIFT
    if modifiers & QtCore.Qt.ControlModifier:
        key += QtCore.Qt.CTRL
    if modifiers & QtCore.Qt.AltModifier:
        key += QtCore.Qt.ALT
    if modifiers & QtCore.Qt.MetaModifier:
        key += QtCore.Qt.META

    k_seq = QKeySequence(key)

    if k_seq in KeyShortcuts.reserved_shortcuts:
        return True

    return k_seq


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

class KeyHistory:
    def __init__(self):
        self.is_present = True
        self.present_history = []
        self.past_history = []

    def draw(self, key):
        if self.is_present:
            self.present_history.append(key)
        else:
            self.present_history = self.past_history.copy()
            self.present_history.append(key)
            self.past_history.clear()
            self.is_present = True

    def undo(self):
        if self.is_present and self.present_history:
            self.past_history = self.present_history[:-1].copy()
            self.is_present = False
        elif self.past_history:
            self.past_history = self.past_history[:-1]

    def redo(self):
        if not self.is_present:
            if len(self.past_history) + 1 == len(self.present_history):
                self.is_present = True
                self.past_history.clear()
            else:
                self.past_history = self.present_history[:len(self.past_history) + 1].copy()

    def stop_flow(self):
        if not self.is_present:
            a = 3
            self.present_history = self.past_history.copy()
            self.past_history.clear()
            self.is_present = True

    def clear(self):
        self.present_history.clear()
        self.past_history.clear()
        self.is_present = True

    def take_current_obj(self):
        if self.is_present:
            return self.present_history[-1]
        else:
            return self.past_history[-1]

    def deep(self):
        if self.is_present:
            return len(self.present_history)
        else:
            return len(self.past_history)

    def printer(self):
        if self.is_present:
            print('we are in present: ', self.present_history)
        else:
            print('we are in past: ', self.past_history)
            print('our future: ', self.present_history)


class MainGame(QMainWindow):

    def __init__(self, ui_file, parent=None):
        self.GAME_TIME = -1
        self.remaining_time = 10000

        # tuple of keys or set of tuples of keys!!!!
        self.game_combination = []

        # PRESS-KEY -> ACTION
        self.game_step = 0
        self.current_combination = {
            Qt.Key.Key_L: None,
            Qt.MouseButton.LeftButton: None,
            Qt.Key.Key_2: None,
            Qt.Key.Key_1: None,
            Qt.Key.Key_Return: None
        }

        self.game_combination = [
            (
                Qt.Key.Key_L, Qt.MouseButton.LeftButton, Qt.Key.Key_2, Qt.Key.Key_1, Qt.Key.Key_Return
            ),
            (
                Qt.Key.Key_L, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.Key.Key_Return
            ),
            (
                Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.Key.Key_2, Qt.Key.Key_1, Qt.Key.Key_Return
            )
        ]
        self.key_history = KeyHistory()

        super(MainGame, self).__init__(parent)
        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()

        self.btn_clear = self.window.findChild(QPushButton, "btn_clear")
        self.btn_skip = self.window.findChild(QPushButton, "btn_skip")
        self.btn_undo = self.window.findChild(QPushButton, "btn_undo")

        self.label_timer = self.window.findChild(QLabel, "label_timer")
        self.log = self.window.findChild(QPlainTextEdit, "log")
        self.a = QPlainTextEdit()
        self.log.clear()
        self.log.setReadOnly(True)
        self.picture_holder = self.window.findChild(QLabel, "picture_holder")
        self.picture_holder.setPixmap(QtGui.QPixmap("actions/pictures/default.png"))
        self.gen_line = QLine()

        self.global_timer = QTimer(self)
        self.second_timer = QTimer(self)
        QObject.connect(self.second_timer, SIGNAL('timeout()'), self.redraw_label_timer)
        QObject.connect(self.global_timer, SIGNAL('timeout()'), self.stop_game)
        QObject.connect(self.log, SIGNAL('textChanged()'), lambda:
        self.log.verticalScrollBar().setValue(
            self.log.verticalScrollBar().maximum()))
        self.btn_undo.clicked.connect(self.undo_action)

        self.window.installEventFilter(self)

        self.window.show()

    def check_modifier(self):
        modifiers = QApplication.keyboardModifiers()
        a = 1
        return self.modifiers_set.get(modifiers)

    def eventFilter(self, obj, event):
        if obj == self.window:
            if event.type() == QEvent.MouseButtonPress and self.is_cursor_in_game_zone():
                self.log.insertPlainText(hook_mouse_event(event))
                self.game_step += 1
                self.key_history.draw(event.button())

            elif event.type() == QEvent.KeyPress and not event.isAutoRepeat():
                k_seq = hook_key_event(event)
                if k_seq == True:
                    return True

                self.game_step += 1
                log_row = k_seq.toString() + '\n'
                self.log.insertPlainText(log_row)
            else:
                return False
        return QMainWindow.eventFilter(self, obj, event)

    def get_last_key(self):
        full_log = self.log.toPlainText().split('\n')
        try:
            return full_log[-2]
        except IndexError:
            return ''

    def undo_action(self):
        self.game_step -= 1
        self.log.undo()
        self.key_history.undo()

    def redo_action(self):
        self.game_step += 1
        self.log.redo()
        self.key_history.redo()

    def check_next_key(self, key):
        def check_in_tuple (tup, item, pos):
            try:
                return tup[pos] == item
            except IndexError:
                return False

        if isinstance(self.game_combination, tuple):
            return check_in_tuple(self.game_combination, key, self.game_step)
        else:
            for combination in self.game_combination:
                try:
                    if combination[self.game_step] == key:
                        return True
                except IndexError:
                    return False
            return False

    def refresh_game_zone(self):
        self.game_step = 0
        self.log.clear()

    def is_cursor_in_game_zone(self):
        pos = QtGui.QCursor.pos()
        name_obj = QApplication.widgetAt(pos).objectName()
        return name_obj == 'picture_holder'

    def start_game(self):
        cur_time = datetime.datetime.fromtimestamp(self.remaining_time / 1000)
        self.label_timer.setText(form_timer_label(cur_time.minute, cur_time.second))
        self.global_timer.start(self.remaining_time)
        self.second_timer.start(1000)

    def redraw_label_timer(self):
        self.remaining_time -= 1000
        cur_time = datetime.datetime.fromtimestamp(self.remaining_time / 1000)
        self.label_timer.setText(form_timer_label(cur_time.minute, cur_time.second))

    def stop_game(self):
        self.global_timer.stop()
        self.second_timer.stop()


def main():
    app = QApplication(sys.argv)
    main = MainGame('ui\MainGame.ui')
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

# ['L', 'ML', '3', '0', 'TAB', '3', '5', 'ML', 'EN']
