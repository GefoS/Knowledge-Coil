import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QPushButton, QLabel, QPlainTextEdit
from PySide2.QtCore import QFile, QObject, QTimer, SIGNAL, SLOT, QLine


class Form(QObject):

    def __init__(self, ui_file, parent=None):
        self.remaining_time = 10

        super(Form, self).__init__(parent)
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
        self.picture_holder = self.window.findChild(QLabel, "picture_holder")
        self.gen_line = QLine()

        self.timer = QTimer(self)
        #self.timer.timeout.connect(self.stop_game)
        self.timer.start(1000)
        #QTimer.singleShot(1000, self.redraw_label_timer)
        QObject.connect(self.timer, SIGNAL('timeout()'), self.redraw_label_timer)

        self.window.show()

    def redraw_label_timer(self):
        self.label_timer.setText(str(self.remaining_time))
        self.remaining_time -= 1

    def stop_game(self):
        #self.timer.stop()
        print ('loh')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Form('ui\MainGame.ui')
    sys.exit(app.exec_())

