import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QPushButton, QLineEdit
from PySide2.QtCore import QFile, QObject


class Form(QObject):

    def __init__(self, ui_file, parent=None):
        super(Form, self).__init__(parent)
        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()

        #self.line = self.window.findChild(QLineEdit, 'lineEdit')
        btn_clear = self.window.findChild(QPushButton, "ButClear")
        btn_clear.clicked.connect(self.test)

        self.window.show()

    def test(self):
        print ("faith tested")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Form('ui\MainGame.ui')
    sys.exit(app.exec_())

