import queue
import random
import sys, csv, datetime, math, os
from shutil import copy2

from PySide2 import QtGui
from PySide2.QtGui import QKeySequence, QCloseEvent, Qt, QPixmap
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QPushButton, QLabel, QPlainTextEdit, QMainWindow, QWidget, QSlider, \
    QLineEdit, QMessageBox, QFileDialog, QShortcut
from PySide2.QtCore import QFile, QTimer, QEvent

#pyside2-rcc -o D:\PycharmProjects\KnowledgeCoil\icons\ui_icons.py D:\PycharmProjects\KnowledgeCoil\icons\ui_icons.qrc
from Action import KeyAction
import SettingsParser
from EventHandler import hook_mouse_event, hook_key_event
from SessionStat import SessionStat
from global_params import KeyShortcuts, GlobalParams, form_timer_label


class LoggingWindow(QWidget):
    def __init__(self, ui_file, parent=None):
        super(LoggingWindow, self).__init__(parent)
        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.logging_window = loader.load(ui_file)
        ui_file.close()

        self.setting_path = ''
        self.user_file_path = os.getcwd()+'/users/users_settings.csv'

        self.btn_login:QPushButton = self.logging_window.findChild(QPushButton, 'btn_login')
        self.btn_settings_name_edit:QPushButton = self.logging_window.findChild(QPushButton, 'btn_settings_name_edit')
        btn_statistics:QPushButton = self.logging_window.findChild(QPushButton, 'btn_statistics')
        btn_statistics.clicked.connect(lambda: print('a'))

        self.slider_time:QSlider = self.logging_window.findChild(QSlider, 'slider_time')
        self.le_username = self.logging_window.findChild(QLineEdit, 'le_username')
        self.le_game_time:QLineEdit = self.logging_window.findChild(QLineEdit, 'le_game_time')
        self.lb_settings_name:QLabel = self.logging_window.findChild(QLabel, 'lb_settings_name')
        self.lb_login_status:QLabel = self.logging_window.findChild(QLabel, 'lb_login_status')
        self.test: QLabel = self.logging_window.findChild(QLabel, 'test')

        self.slider_time.sliderMoved.connect(lambda pos: self.set_time(pos))
        self.le_game_time.editingFinished.connect(self.set_slider_position)
        self.le_username.editingFinished.connect(self.check_user)
        self.btn_settings_name_edit.clicked.connect(self.reload_settings)
        self.btn_login.clicked.connect(lambda: self.close())

        self.logging_window.setWindowTitle('{} Login'.format(GlobalParams.application_name))
        self.logging_window.show()

    def closeEvent(self, event:QCloseEvent):
        self.logging_window.close()

    def check_user(self):
        username = self.le_username.text()
        cwd = os.getcwd()
        user_dir = cwd +'/users/'+username
        if not username:
            return
        if os.path.exists(user_dir):
            self.settings_path = self.get_users_list().get(username)
            file_name = self.settings_path.split('/')[-1]
            self.set_settings_label(file_name)
            self.btn_settings_name_edit.setDisabled(False)
            self.lb_login_status.setPixmap(QPixmap.fromImage('icons/login_okay.png'))
        else:
            self.lb_login_status.setPixmap(QPixmap('icons/login_cancel.png'))
            self.le_username.blockSignals(True)
            result = self.show_settings_missing_dialog(username)
            self.le_username.blockSignals(False)
            if result == 2:
                return

            self.btn_settings_name_edit.setDisabled(False)
            if result == 0:
                path = self.load_settings()
            else:
                path = self.load_settings(True)
            self.add_user(user_dir, path)

    def set_time(self, position):
        time = math.trunc(0.3*(position+1))+1
        self.le_game_time.setText(str(time))

    def set_slider_position(self):
        field_text = self.le_game_time.text()
        if field_text:
            try:
                time = int(field_text)
                if time > 30:
                    time = 30
                    self.le_game_time.setText('30')
                position = math.trunc((10 * time) / 3 - 1)
                self.slider_time.setSliderPosition(position)
            except ValueError:
                pass

    def add_user(self, user_dir, settings_path):
        os.mkdir(user_dir)
        copy2(settings_path, user_dir)

        file_name = settings_path.replace('\\', '/').split('/')[-1]
        user_name = user_dir.split('/')[-1]
        path = user_dir.replace('\\', '/')+'/'+file_name
        self.write_user_path(user_name, path)
        self.lb_login_status.setPixmap(QPixmap.fromImage('icons/login_okay.png'))

    def load_settings(self, default=False):
        xml_path = (os.getcwd()+'/settings/default_settings.xml').replace('\\', '/')
        if not default:
            loaded_path = QFileDialog.getOpenFileName(None, "Load Picture Action", os.getcwd(),
                                                   "XML file (*.xml)")[0]
            if loaded_path:
                xml_path = loaded_path
            else:
                self.show_settings_not_loaded_dialog()

        file_name = xml_path.split('/')[-1]
        self.set_settings_label(file_name)
        return xml_path

    def reload_settings(self):
        user_name = self.le_username.text()
        xml_path = self.load_settings()
        cwd = os.getcwd().replace('\\', '/')
        user_dir = cwd + '/users/{}/'.format(user_name)
        user_settings_path = user_dir + xml_path.split('/')[-1]
        self.write_user_path(user_name, user_settings_path)
        if os.path.exists(user_settings_path):
            os.remove(user_settings_path)
        copy2(xml_path, user_settings_path)

    def write_user_path(self, user_name, path):
        users = self.get_users_list()
        if user_name in users:
            users[user_name] = path
            with open(self.user_file_path, 'w', newline='') as user_file:
                csv_writer = csv.writer(user_file, delimiter=',', quotechar='|')
                for k, v in users.items():
                    csv_writer.writerow([k, v])
        else:
            with open(self.user_file_path, 'a+', newline='') as users_file:
                writer = csv.writer(users_file, delimiter=',', quotechar='|')
                writer.writerow([user_name, path])
        self.settings_path = path

    def set_settings_label(self, file_name):
        self.lb_settings_name.setText(file_name)
        size = 7.5 * len(file_name)
        self.lb_settings_name.setMinimumSize(math.trunc(size), 26)
        self.lb_settings_name.setMaximumSize(math.trunc(size), 26)
        self.lb_settings_name.adjustSize()

    def get_users_list(self):
        with open(self.user_file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            users = {user:settings for user, settings in list(reader)}
            return users

    def show_settings_missing_dialog(self, username):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText('Добро пожаловать, {}!'.format(username))
        msg_box.setInformativeText('Желаете загрузить настройки Inventor или оставить по умолчанию?')
        msg_box.addButton('Загрузить', QMessageBox.YesRole)
        msg_box.addButton('По-умолчанию', QMessageBox.NoRole)
        msg_box.addButton('Отмена', QMessageBox.RejectRole)
        result = msg_box.exec_()
        return result

    def show_settings_not_loaded_dialog(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText('Пользовательские настройки не загружены')
        msg_box.setInformativeText('Будут использованы настройки по умолчанию')
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()


class MainGame(QMainWindow):

    def init_global_fields(self):
        self.user_name = ''
        self.user_settings = dict()
        self.game_time = 0
        self.game_step = 0
        self.solved = False

        self.actions_queue = queue.Queue()
        self.current_combination = list()
        self.action_name = ''

        self.stat_session = None

    def __init__(self, ui_file, parent=None):

        self.init_global_fields()

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
        self.log:QPlainTextEdit = self.window.findChild(QPlainTextEdit, "log")
        self.log.clear()
        self.log.setReadOnly(True)
        self.picture_holder:QLabel = self.window.findChild(QLabel, "picture_holder")
        self.picture_holder.setPixmap(QtGui.QPixmap("actions/pictures/default.png"))

        self.global_timer = QTimer(self)
        self.second_timer = QTimer(self)
        self.second_timer.timeout.connect(self.redraw_label_timer)
        self.global_timer.timeout.connect(self.stop_game)
        self.log.textChanged.connect(self.scroll_log_to_max)
        self.btn_undo.clicked.connect(self.undo_action)
        self.btn_skip.clicked.connect(self.skip)
        self.btn_clear.clicked.connect(self.reset)

        undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self.window)
        undo_shortcut.activated.connect(lambda: self.undo_action())

        self.window.installEventFilter(self)
        self.window.adjustSize()
        self.window.setWindowTitle('{} Game'.format(GlobalParams.application_name))

        self.logging_window = LoggingWindow('ui\LoggingDialog.ui')
        self.logging_window.btn_login.clicked.connect(self.login_in_game)

    def eventFilter(self, obj, event):
        if obj == self.window:
            if event.type() == QEvent.MouseButtonPress:#and self.is_cursor_in_game_zone()
                key = hook_mouse_event(event)
                self.draw_key(key)

            elif event.type() == QEvent.KeyPress and not event.isAutoRepeat():
                key = hook_key_event(event)
                if key == True:
                    return True

                self.draw_key(key)

            elif event.type() == QEvent.KeyRelease and event.key() == Qt.Key.Key_Tab:
                self.draw_key(event.key())
            else:
                return False
        return QMainWindow.eventFilter(self, obj, event)

    def login_in_game(self):
        self.user_name = self.logging_window.le_username.text()
        self.game_time = int(self.logging_window.le_game_time.text())*60000
        self.user_settings = SettingsParser.parse_to_key_combination(self.logging_window.settings_path)

        self.logging_window.hide()
        self.window.show()
        self.show_start_countdown_dialog()

    def start_game(self):
        cur_time = datetime.datetime.fromtimestamp(self.game_time/1000)
        self.label_timer.setText(form_timer_label(cur_time.minute, cur_time.second))
        self.global_timer.start(self.game_time)
        self.second_timer.start(1000)

        self.stat_session = SessionStat(self.user_name, self.game_time, self)

        queue_size = math.trunc((self.game_time/60000)*2)
        self.build_action_queue(queue_size)
        self.next_combination()

    def next_combination(self):
        if self.actions_queue.empty():
            self.stop_game()
        else:
            self.action_name = self.actions_queue.get()
            current_action = self.action_by_name(self.action_name)
            new_picture = QtGui.QPixmap(current_action.picture_path)
            self.picture_holder.setPixmap(self.scale_picture(new_picture))
            self.current_combination = current_action.combination
            self.log.clear()
            self.game_step = 0
            print(self.current_combination)

    def draw_key(self, key):
        def key_to_text(coded_key):
            if coded_key in KeyShortcuts.mouse_shorts_map:
                return KeyShortcuts.mouse_shorts_map.get(coded_key)
            else:
                return QKeySequence(coded_key).toString()
        last_key_pos = len(self.current_combination)
        if self.game_step < last_key_pos:
            role = self.current_combination[self.game_step] == key
            self.insert_key_to_log(key_to_text(key), role)
            self.solved = False
            if self.game_step+1 == last_key_pos and role:
                self.solved = True
                self.insert_key_to_log('Решено! Нажмите любую клавишу, чтобы продолжить.', True)
                self.stat_session.solve()
        elif self.solved:
            self.next_combination()
            return
        else:
            self.insert_key_to_log(key_to_text(key), False)
        self.game_step += 1

    def show_start_countdown_dialog(self):
        def get_cur_time():
            time = over_timer.remainingTime()
            return math.trunc(time/1000)+1
        def timeout():
            msg_box.close()
            over_timer.stop()
            countdown_timer.stop()
            self.start_game()
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText('Игра начнется через 5 секунд')
        msg_box.addButton('Начать сейчас', QMessageBox.YesRole)
        countdown_timer = QTimer(msg_box)
        over_timer =  QTimer(msg_box)
        countdown_timer.timeout.connect(lambda:
                                        msg_box.setText('Игра начнется через {} секунд'.format(get_cur_time())))
        over_timer.timeout.connect(timeout)
        msg_box.buttonClicked.connect(timeout)
        over_timer.start(5000)
        countdown_timer.start(1000)
        msg_box.exec_()

    def skip(self):
        self.stat_session.skip()
        self.actions_queue.put(self.action_name)
        self.next_combination()

    def reset(self):
        self.stat_session.reset()
        self.game_step = 0
        self.log.clear()

    def undo_action(self):
        if self.game_step > 0:
            self.stat_session.reset()
            self.game_step -= 1
            self.log.undo()
            self.scroll_log_to_max()

    def redo_action(self):
        self.game_step += 1
        self.log.redo()

    def refresh_game_zone(self):
        self.game_step = 0
        self.log.clear()

    def is_cursor_in_game_zone(self):
        pos = QtGui.QCursor.pos()
        name_obj = QApplication.widgetAt(pos).objectName()
        return name_obj == 'picture_holder'

    def redraw_label_timer(self):
        self.game_time -= 1000
        cur_time = datetime.datetime.fromtimestamp(self.game_time / 1000)
        self.label_timer.setText(form_timer_label(cur_time.minute, cur_time.second))

    def stop_game(self):
        self.stat_session.finish_game(self.global_timer.remainingTime())
        self.global_timer.stop()
        self.second_timer.stop()

    def insert_key_to_log(self, key, role:bool):
        if role:
            self.log.appendHtml('<font color="#1cb845">{}</font>'.format(key))
        else:
            self.stat_session.make_mistake()
            self.log.appendHtml('<font color="#cf0a0a">{}</font>'.format(key))

    def build_action_queue(self, quantity):
        action_files = [file for file in os.listdir('actions/') if
                        os.path.splitext(file)[1] == '.csv']
        if len(action_files) == 0:
            self.show_error_dialog()
            self.close()
        if quantity >= len(action_files):
            quantity = len(action_files)
            random.shuffle(action_files)

        for action in random.sample(action_files, quantity):
            self.actions_queue.put(action)

    def show_error_dialog(self):
        msg_box = QMessageBox()
        msg_box.setDefaultButton(QMessageBox.Ok)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText('Файлы комбинаций не найдены.')
        msg_box.setInformativeText('Будет произведен выход из приложения.')
        msg_box.exec_()

    def action_by_name(self, name):
        return KeyAction('actions/{}'.format(name), self.user_settings)

    def scale_picture(self, picture:QPixmap):
        max_W = self.picture_holder.maximumWidth()
        max_H = self.picture_holder.maximumHeight()
        if picture.height() > max_H or picture.width() > max_W:
            return picture.scaled(max_W, max_H, Qt.KeepAspectRatio)
        else:
            return picture

    def scroll_log_to_max(self):
        self.log.verticalScrollBar().setValue(
        self.log.verticalScrollBar().maximum())

def main():
    app = QApplication(sys.argv)
    main = MainGame('ui\MainGame.ui')
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

'''pyinstaller --noconfirm --onedir --noconsole --add-data "D:/PycharmProjects/KnowledgeCoil/users;users/" --add-data "D:/PycharmProjects/KnowledgeCoil/ui;ui/" --add-data "D:/PycharmProjects/KnowledgeCoil/settings;settings/" --add-data "D:/PycharmProjects/KnowledgeCoil/icons;icons/" --add-data "D:/PycharmProjects/KnowledgeCoil/actions;actions/"  ""'''
