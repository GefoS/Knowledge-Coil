import sys
import os

from PySide2 import QtGui
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QPushButton, QLineEdit, QTableWidget, QLabel, QTableWidgetItem, QAction, \
    QMenu, QMessageBox, QFileDialog
from PySide2.QtCore import QFile, QObject
import csv


class ActionWindow(QObject):

    def __init__(self, ui_file, parent=None):

        self.DEFAULT_PICTURE = "actions/pictures/default.png"
        self.UP = 1
        self.DOWN = -1

        self.SHIFT_TO_CONTENT = 3
        self.PICTURE_ROW = 1

        self.csv_linked_path = ''
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
        self.menu_save = self.menu_file[2]
        self.menu_save_as = self.menu_file[3]
        self.menu_import_pic = self.menu_file[5]

        # btn_clear.clicked.connect(self.test)
        self.btn_add.clicked.connect(self.add_row)
        self.btn_remove.clicked.connect(self.remove_row)
        self.btn_up.clicked.connect(self.up_row)
        self.btn_down.clicked.connect(self.down_row)
        # self.btn_apply.clicked.connect(self.import_picture)

        self.menu_new.triggered.connect(self.new_pic_action)
        self.menu_load.triggered.connect(self.load)
        self.menu_import_pic.triggered.connect(self.import_picture)
        self.menu_save.triggered.connect(self.save_short)
        self.menu_save_as.triggered.connect(self.save_full)
        # self.act_picture.mousePressEvent = self.import_picture
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
        self.isSaved = False

    def down_row(self):
        self.move_row(self.DOWN)
        self.isSaved = False

    def load(self):
        if not self.isSaved:
            ret_val = self.show_exit_save_dialog()
            if ret_val == QMessageBox.Save:
                self.save_short()
                if self.isSaved:
                    self.show_loading_act_dialog()
            elif ret_val == QMessageBox.Ignore:
                self.show_loading_act_dialog()
        else:
            self.show_loading_act_dialog()

    def save_short(self):
        if self.csv_linked_path:
            self.save_pic_action(False)
        else:
            self.save_pic_action(True)

    def save_full(self):
        self.save_pic_action(True)

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

    def show_loading_act_dialog(self):
        """csv_path = self.show_loading_act_dialog()
        if csv_path:
            self.load_pic_action(csv_path)"""
        csv_path = QFileDialog.getOpenFileName(None, "Load Picture Action", os.getcwd() + '\\actions',
                                                    "CSV file (*.csv)")[0]
        if csv_path:
            self.load_pic_action(csv_path)

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

    def load_pic_action(self, csv_path):
        #def parse_and_rebuild():
        data = []
        with open(csv_path, newline='') as pic_file:
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
        self.csv_linked_path = csv_path

        """if not self.isSaved:
            ret_val = self.show_exit_save_dialog()
            if ret_val == QMessageBox.Save:
                self.save_short()
                if self.isSaved:
                    parse_and_rebuild()
            elif ret_val == QMessageBox.Ignore:
                parse_and_rebuild()
        else:
            parse_and_rebuild()"""

    def new_pic_action(self):
        def refresh_space():
            self.tab_action.setRowCount(0)
            self.le_name.setText("default")
            self.act_picture.setPixmap(QtGui.QPixmap(self.DEFAULT_PICTURE))
            self.csv_linked_path = ''
            self.isSaved = True

        if self.isSaved:
            refresh_space()
        else:
            res_val = self.show_exit_save_dialog()
            if res_val == QMessageBox.Save:
                self.save_short()
                if self.isSaved:
                    refresh_space()
            elif res_val == QMessageBox.Ignore:
                refresh_space()

    def write_files(self, path):
        if path:
            open(path, 'w').close()

        pic_name = self.le_name.text()
        pic_path = 'actions/pictures/' + pic_name + '.png'
        with open(path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='|')
            # csv_writer.writerow (['name', self.picture_action_global.name])
            # csv_writer.writerow (['pic_path', self.picture_action_global.picture_url])
            csv_writer.writerow(['name', pic_name])
            csv_writer.writerow(['pic_path', pic_path])
            csv_writer.writerow(['Key', 'Command'])
            for row in self.get_table_data():
                csv_writer.writerow(row)
            #csv_file.close()

        #pic_file = open(pic_path, 'w')
        self.act_picture.pixmap().save(pic_path, format='PNG')
        #pic_file.close()

    def save_pic_action(self, isFull):
        if isFull:
            file_name = QFileDialog.getSaveFileName(None, "Save Picture Action", os.getcwd() + '\\actions',
                                                    "CSV file (*.csv)")[0]
            if file_name is not '':
                self.csv_linked_path = file_name
                self.write_files(self.csv_linked_path)
                self.isSaved = True
        else:
            self.write_files(self.csv_linked_path)
            self.isSaved = True

    def import_picture(self):
        file_name = QFileDialog.getOpenFileName(None, "Open Image", os.getcwd() + '\\actions\\pictures',
                                                "Image Files (*.png *.jpg *.bmp)")
        if file_name[0] is not '':
            self.act_picture.setPixmap(QtGui.QPixmap(file_name[0]))
            #self.picture_action_global.picture_url = file_name[0]
            self.isSaved = False


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
