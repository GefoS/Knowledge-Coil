import sys

from PySide2 import QtGui
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QPushButton, QLineEdit, QTableWidget, QLabel, QTableWidgetItem, QAction, \
    QMenu, QMessageBox
from PySide2.QtCore import QFile, QObject
import csv


class ActionWindow(QObject):

    def __init__(self, ui_file, parent=None):

        self.DEFAULT_PICTURE = "actions/pictures/default.png"
        self.UP = 1
        self.DOWN = -1

        self.SHIFT_TO_CONTENT = 3
        self.PICTURE_ROW = 1

        self.pic_action = ActionPicture()

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
        self.menu_new = self.menu_file[0]
        self.menu_load = self.menu_file[1]
        self.menu_import_pic = self.menu_file[2]
        self.a = self.menu_file[3]
        self.b = self.menu_file[5]

        # btn_clear.clicked.connect(self.test)
        self.btn_add.clicked.connect(self.add_row)
        self.btn_remove.clicked.connect(self.remove_row)
        self.btn_up.clicked.connect(self.up_row)
        self.btn_down.clicked.connect(self.down_row)
        self.btn_apply.clicked.connect(self.load_pic_action)

        self.menu_new.triggered.connect(self.new_pic_action)
        self.window.show()

        self.tab_action.setRowCount(0)
        self.act_picture.setPixmap(QtGui.QPixmap(self.DEFAULT_PICTURE))

    def add_row(self):
        self.tab_action.insertRow(self.tab_action.rowCount())
        self.isSaved = False

    def remove_row(self):
        sel_row = self.tab_action.currentRow()
        self.tab_action.removeRow(sel_row)
        self.isSaved = False

    def up_row(self):
        self.move_row(self.UP)

    def down_row(self):
        self.move_row(self.DOWN)

    def move_row(self, direction):
        """model = self.tab_action.selectionModel()
        selected = model.selectedRows()
        if not selected:"""
        # cell_pos = (self.tab_action.currentRow(), self.tab_action.currentColumn())
        row_id = self.tab_action.currentRow()
        col_id = self.tab_action.currentColumn()
        if direction not in (self.UP, self.DOWN) or row_id == -1:
            return
        key_cell = self.tab_action.item(row_id, 0)
        com_cell = self.tab_action.item(row_id, 1)

        if direction == self.UP and row_id != 0:
            self.tab_action.insertRow(row_id - 1)
            self.tab_action.setItem(row_id - 1, 0, QTableWidgetItem(key_cell))
            self.tab_action.setItem(row_id - 1, 1, QTableWidgetItem(com_cell))
            self.tab_action.removeRow(row_id + 1)
            self.tab_action.setCurrentCell(row_id - 1, col_id)
            self.isSaved = False
        elif direction == self.DOWN and row_id != self.tab_action.rowCount() - 1:
            self.tab_action.insertRow(row_id + 2)
            self.tab_action.setItem(row_id + 2, 0, QTableWidgetItem(key_cell))
            self.tab_action.setItem(row_id + 2, 1, QTableWidgetItem(com_cell))
            self.tab_action.removeRow(row_id)
            self.tab_action.setCurrentCell(row_id + 1, col_id)
            self.isSaved = False
        else:
            return

    def show_exit_save_dialog(self):
        exit_save_dialog = QMessageBox()
        exit_save_dialog.setIcon(QMessageBox.Information)

        exit_save_dialog.setText('The document has been modified, would you like to save the changes?')
        exit_save_dialog.setInformativeText("If you don't save, your changes will be lost")
        exit_save_dialog.setWindowTitle("Would you save action?")
        exit_save_dialog.setStandardButtons(QMessageBox.Save | QMessageBox.Cancel | QMessageBox.Ignore)

        return exit_save_dialog.exec_()

    def get_table_data(self):
        model = self.tab_action.model()
        data = []

        for row in range(model.rowCount()):
            data.append([])
            for col in range(model.columnCount()):
                index = model.index(row, col)
                data[row].append(str(model.data(index)))

        return data

    def load_pic_action(self):
        if not self.isSaved:
            self.act_picture.setPixmap(QtGui.QPixmap(self.DEFAULT_PICTURE))
        else:
            data = []
            with open('actions/test.csv', newline='') as pic_file:
                reader = csv.reader(pic_file, delimiter=',', quotechar='|')
                data = list(reader)
            self.tab_action.setRowCount(len(data) - self.SHIFT_TO_CONTENT)
            for row in range(self.tab_action.rowCount()):
                self.tab_action.setItem(row, 0, QTableWidgetItem(data[row + self.SHIFT_TO_CONTENT][0]))
                self.tab_action.setItem(row, 1, QTableWidgetItem(data[row + self.SHIFT_TO_CONTENT][1]))

            name = data[0][1]
            pic_url = str(data[self.PICTURE_ROW][1])
            self.act_picture.setPixmap(QtGui.QPixmap(pic_url))
            self.le_name.setText(name)
            self.isSaved = True

            return ActionPicture(name=name, picture_url=pic_url, csv_path='actions/test.csv',
                                 combination=data[self.SHIFT_TO_CONTENT:])


    def new_pic_action(self):
        if self.isSaved:
            self.tab_action.setRowCount(0)
            self.act_picture.setPixmap(QtGui.QPixmap(self.DEFAULT_PICTURE))
            return ActionPicture()
        else:
            res_val = self.show_exit_save_dialog()
            print(res_val)


class ActionPicture:
    def __init__(self, name="default action", picture_url="actions/pictures/default.png", csv_path=None,
                 combination=[]):
        self.name = name
        self.picture_url = picture_url
        self.combination = combination
        self.csv_url = csv_path


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = ActionWindow('ui\ActionMain.ui')
    sys.exit(app.exec_())
