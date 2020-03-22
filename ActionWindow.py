import sys

from PySide2 import QtGui
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QPushButton, QLineEdit, QTableWidget, QLabel, QTableWidgetItem, QAction, \
    QMenu
from PySide2.QtCore import QFile, QObject, SIGNAL, QPoint


class ActionWindow(QObject):

    def __init__(self, ui_file, parent=None):

        self.DEFAULT_PICTURE = "actions/pictures/default.png"

        self.UP = 1
        self.DOWN = -1

        self.isSaved = True

        super(ActionWindow, self).__init__(parent)
        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()

        # tab
        self.tab_action = self.window.findChild(QTableWidget, "tab_action")
        self.btn_add = self.window.findChild(QPushButton, "btn_add")
        self.btn_down = self.window.findChild(QPushButton, "btn_down")
        self.btn_up = self.window.findChild(QPushButton, "btn_up")
        self.btn_remove = self.window.findChild(QPushButton, "btn_remove")

        # img
        self.act_picture = self.window.findChild(QLabel, "img_action")
        self.le_name = self.window.findChild(QLineEdit, "le_name")
        self.btn_edit = self.window.findChild(QPushButton, "btn_edit")
        self.btn_apply = self.window.findChild(QPushButton, "btn_apply")

        self.menu_file = self.window.findChild(QMenu, 'menuFile').actions()
        self.menu_new = self.menu.findChild(QAction, 'actionNew_Action')[0]
        self.menu_load = self.menu.findChild(QAction, 'actionLoad_Action')[1]
        self.menu_import_pic = self.menu.findChild(QAction, 'actionImport_Action')[2]

        print (self.menu.actions())
        #btn_clear.clicked.connect(self.test)
        self.btn_add.clicked.connect(self.add_row)
        self.btn_remove.clicked.connect(self.remove_row)
        self.btn_up.clicked.connect(self.up_row)
        self.btn_down.clicked.connect(self.down_row)

        self.btn_apply.clicked.connect(self.new_pic_action)
        self.window.show()

    def add_row(self):
        self.tab_action.insertRow(self.tab_action.rowCount())

    def remove_row(self):
        sel_row = self.tab_action.currentRow()
        self.tab_action.removeRow(sel_row)

    def up_row(self):
        self.move_row(self.UP)

    def down_row(self):
        self.move_row(self.DOWN)

    def move_row(self, direction):
        """model = self.tab_action.selectionModel()
        selected = model.selectedRows()
        if not selected:"""
        #cell_pos = (self.tab_action.currentRow(), self.tab_action.currentColumn())
        row_id = self.tab_action.currentRow()
        col_id = self.tab_action.currentColumn()
        if direction not in (self.UP, self.DOWN) or row_id == -1:
            return
        key_cell = self.tab_action.item(row_id, 0)
        com_cell = self.tab_action.item(row_id, 1)

        if direction == self.UP and row_id != 0:
            self.tab_action.insertRow(row_id-1)
            self.tab_action.setItem(row_id-1, 0, QTableWidgetItem(key_cell))
            self.tab_action.setItem(row_id-1, 1, QTableWidgetItem(com_cell))
            self.tab_action.removeRow(row_id+1)
            self.tab_action.setCurrentCell(row_id-1, col_id)
        elif direction == self.DOWN and row_id != self.tab_action.rowCount()-1:
            self.tab_action.insertRow(row_id+2)
            self.tab_action.setItem(row_id+2, 0, QTableWidgetItem(key_cell))
            self.tab_action.setItem(row_id+2, 1, QTableWidgetItem(com_cell))
            self.tab_action.removeRow(row_id)
            self.tab_action.setCurrentCell(row_id+1, col_id)
        else:
            return

    def new_pic_action(self):
        self.tab_action.setRowCount(0)

        self.act_picture.setPixmap(QtGui.QPixmap(self.DEFAULT_PICTURE))
        return ActionPicture()


class ActionPicture:
    def __init__(self, name="default action", picture_url="actions/pictures/default.png", combination=[]):
        self.a_name = name
        self.pic_url = picture_url
        self.comb = combination


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = ActionWindow('ui\ActionMain.ui')
    sys.exit(app.exec_())
