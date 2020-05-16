

'''По истечении заданного времени работы выводится статистика по полностью «разгаданным» картинкам,
количеству верно и неверно введенных комбинаций, количеству откатов и количеству пропусков.
Статистика записывается в отдельную строку в отдельный файл для последующего просмотра через программу либо отдельно.'''
import datetime
import sys

from PySide2.QtCore import QFile, QEvent
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QWidget, QApplication, QLabel, QDialogButtonBox

from global_params import form_timer_label


class SessionStat:
    def __init__(self, username, game_time, parent):
        self.username = username
        self.game_time = game_time
        self.pure, self.unclear, self.skips, self.resets = [0]*4
        self.is_pure = True
        self.finish_dialog = GameFinishedDialog(parent)

        print(self.finish_dialog.parent())
        print([method_name for method_name in dir(self.finish_dialog.parent())
                  if callable(getattr(self.finish_dialog.parent(), method_name))])

    def solve(self):
        if self.is_pure:
            self.pure += 1
        else:
            self.unclear += 1
        self.is_pure = True

    def skip(self):
        self.skips += 1

    def reset(self):
        self.resets += 1
        self.is_pure = False

    def make_mistake(self):
        self.is_pure = False

    def finish_game(self, remaining_time):
        spent_time = self.game_time - remaining_time
        time = datetime.datetime.fromtimestamp(spent_time / 1000)
        self.finish_dialog.show_dialog((form_timer_label(time.minute, time.second), self.pure, self.unclear, self.resets, self.skips))


class GameFinishedDialog(QWidget):
    def __init__(self, parent):
        super(GameFinishedDialog, self).__init__(parent=parent)
        ui_file = QFile('ui\SessionStat.ui')
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.finish_dialog = loader.load(ui_file)
        ui_file.close()

        self.result = None

        self.stat_holders = []
        lb_time:QLabel = self.finish_dialog.findChild(QLabel, 'lb_time')
        self.stat_holders.append(lb_time)
        lb_pure:QLabel = self.finish_dialog.findChild(QLabel, 'lb_pure')
        self.stat_holders.append(lb_pure)
        lb_unclear:QLabel = self.finish_dialog.findChild(QLabel, 'lb_unclear')
        self.stat_holders.append(lb_unclear)
        lb_resets:QLabel = self.finish_dialog.findChild(QLabel, 'lb_resets')
        self.stat_holders.append(lb_resets)
        lb_skips:QLabel = self.finish_dialog.findChild(QLabel, 'lb_skips')
        self.stat_holders.append(lb_skips)

        self.button_box:QDialogButtonBox = self.finish_dialog.findChild(QDialogButtonBox, 'button_box')
        self.button_box.clicked.connect(lambda button: self.handle_button(button))

        self.finish_dialog.installEventFilter(self)

    def show_dialog(self, stat_values):
        self.finish_dialog.show()
        def set_stat(label: QLabel, stat_value):
            stat_name = label.text().split(':', 1)[0]
            label.setText(stat_name + ': ' + stat_value)

        for holder, value in zip(self.stat_holders, stat_values):
            set_stat(holder, str(value))

    def handle_button(self, button):
        role = self.button_box.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.AcceptRole:
            self.parent().logging_window.logging_window.show()
            self.parent().window.hide()
        else:
            self.parent().window.close()
        self.finish_dialog.close()