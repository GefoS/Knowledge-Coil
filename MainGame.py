import datetime, sys, csv

from PySide2 import QtXml, QtGui, QtCore
from PySide2.QtGui import QKeyEvent
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QPushButton, QLabel, QPlainTextEdit, QWidget, QMainWindow
from PySide2.QtCore import QFile, QObject, QTimer, SIGNAL, QLine, QEvent, Qt

from global_params import CsvParams, KeyShortcuts as key_shorts


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

def parse_to_qt_format(combination):
    for key in combination:
        if len(key) == 1:
            return Qt.Key(ord(key))
        elif '+' not in key:
            return


def get_full_key(pressed_keys):
    if len(pressed_keys) == 1:
        return pressed_keys[0]
    elif len(pressed_keys) > 1:
        return pressed_keys
    else:
        return -1


def get_qt_key_name(key):
    return str(key).split('_')[-1]


class MainGame(QMainWindow):

    def __init__(self, ui_file, parent=None):
        self.GAME_TIME = -1
        self.remaining_time = 10000
        # PRESS-KEY -> ACTION
        self.current_combination = {
            Qt.Key.Key_L: None,
            Qt.MouseButton.LeftButton: None,
            Qt.Key.Key_2: None,
            Qt.Key.Key_1: None,
            Qt.Key.Key_Return: None
        }
        self.current_keys = list(self.current_combination.keys())
        self.key_queue = []
        self.game_step = 0

        self.pressed = []

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
        self.btn_skip.clicked.connect(self.start_game)

        self.window.installEventFilter(self)

        # keyboard.add_hotkey('ctrl+z', self.isis)
        self.window.show()

    def eventFilter(self, obj, event):
        pos = QtGui.QCursor.pos()
        if obj == self.window:
            if event.type() == QEvent.MouseButtonPress and self.is_cursor_in_game_zone():
                if event.button() == QtCore.Qt.MouseButton.LeftButton:
                    self.log.insertPlainText(key_shorts.MOUSE_LEFT[1] + '\n')
                else:
                    self.log.insertPlainText(key_shorts.MOUSE_RIGHT[1] + '\n')
                self.key_queue.append(event.button())
                print ('queue grow ', self.key_queue)
                return True

            elif event.type() == QEvent.KeyPress and not event.isAutoRepeat():
                self.pressed.append(Qt.Key(event.key()))

            elif event.type() == QEvent.KeyRelease and not event.isAutoRepeat():
                key = event.key()
                full_key = -1

                if Qt.Key(key) == Qt.Key_Tab:
                    full_key = Qt.Key_Tab
                else:
                    if key not in (Qt.Key_Shift, Qt.Key_Control, Qt.Key_Alt):
                        full_key = get_full_key(self.pressed)

                if full_key != -1:
                    self.key_queue.append(full_key)
                    print('queue grow ', self.key_queue)
                    self.write_row(full_key)

                if key in self.pressed:
                    self.pressed.remove(key)

                return True
            else:
                return False
        return QMainWindow.eventFilter(self, obj, event)

    def write_row(self, key):
        if not isinstance(key, list):
            self.log.insertPlainText(get_qt_key_name(key) + '\n')
        else:
            key_names = list(map(get_qt_key_name, key))
            row_list = ['+'] * (len(key_names) * 2 - 1)
            row_list[0::2] = key_names
            row = ''.join(row_list)
            self.log.insertPlainText(row + '\n')

    def undo_action(self):
        pass

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


class KeyHistory:
    def __init__(self):
        self.is_present = True
        self.present_history = []
        self.past_history =[]

    def draw(self, key):
        if self.is_present:
            self.present_history.append(key)
        else:
            self.present_history = self.past_history.append(key)
            self.past_history.clear()
            self.is_present = True

    def undo(self):
        if self.is_present and self.present_history:
            self.past_history = self.present_history[:-1]
            self.is_present = False
        elif self.past_history:
            self.past_history = self.past_history[:-1]


class Combination:
    def __init__(self, keys=None, values=None):
        if keys is None:
            self.keys = []
        else:
            self.keys = keys
        if values is None:
            self.values = []
        else:
            self.values = values

    def load_csv_combination(self, path):
        with open(path, newline='') as pic_file:
            reader = csv.reader(pic_file, delimiter=',', quotechar='|')
            data = list(reader)

            for item in data[CsvParams.SHIFT_TO_CONTENT:]:
                if item[1] == 'None':
                    item[1] = None
                self.insert(item[0], item[1])

    def insert(self, key, value=None):
        self.keys.append(key)
        self.values.append(value)

    def is_right_key(self, key, position=0):
        return self.keys[position] == key

    def get_combination(self):
        return self.keys, self.values

    def get_keys(self):
        return self.keys


def main():
    c = Combination()
    c.load_csv_combination('actions//action_line2.csv')
    test = ['L', '122', '3', '1521', 'TAB', '228', '5', 'ML', 'EN']
    # keyboard.add_hotkey('ctrl+z', lambda: print('я лох'))
    app = QApplication(sys.argv)
    main = MainGame('ui\MainGame.ui')
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

# ['L', 'ML', '3', '0', 'TAB', '3', '5', 'ML', 'EN']
