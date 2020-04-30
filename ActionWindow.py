import sys
import os
import csv

import PySide2
from PySide2 import QtGui, QtWidgets
from PySide2 import QtXml
from PySide2.QtGui import QKeySequence
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QPushButton, QLineEdit, QTableWidget, QLabel, QTableWidgetItem, \
    QMenu, QMessageBox, QFileDialog, QWidget, QRadioButton, QAction
from PySide2.QtCore import QFile, QEvent, Qt

from global_params import CsvParams, KeyShortcuts
import MainGame


def invert_table_key(tab_key):
    if len(tab_key) == 1:
        return QKeySequence(tab_key)
    if tab_key in (KeyShortcuts.MOUSE_RIGHT[2], KeyShortcuts.MOUSE_LEFT[2]):
        return tab_key
    for modifier in ('Ctrl', 'Shift', 'Alt'):
        if modifier in tab_key:
            return QKeySequence(tab_key)
    return [QKeySequence(minor_key) for minor_key in tab_key]


class ActionWindow(QWidget):

    def __init__(self, ui_file, parent=None):

        self.DEFAULT_PICTURE = "actions/pictures/default.png"
        self.UP = 1
        self.DOWN = -1

        self.csv_linked_path = ''
        self.is_saved = True
        self.is_recording = False
        # add -> false, rewrite -> true
        self.is_rewriting_mode = False

        super(ActionWindow, self).__init__(parent)
        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()

        # tab
        self.tab_action:QTableWidget = self.window.findChild(QTableWidget, "tab_action")

        self.btn_add = self.window.findChild(QPushButton, "btn_add")
        self.btn_down = self.window.findChild(QPushButton, "btn_down")
        self.btn_up = self.window.findChild(QPushButton, "btn_up")
        self.btn_remove = self.window.findChild(QPushButton, "btn_remove")
        self.btn_merge:QPushButton = self.window.findChild(QPushButton, "btn_merge")
        self.btn_split:QPushButton = self.window.findChild(QPushButton, "btn_split")

        self.btn_edit = self.window.findChild(QPushButton, "btn_edit")
        self.btn_apply = self.window.findChild(QPushButton, "btn_apply")
        self.btn_record:QPushButton = self.window.findChild(QPushButton, "btn_record")

        # img
        self.act_picture = self.window.findChild(QLabel, "img_action")
        self.le_name = self.window.findChild(QLineEdit, "le_name")

        self.rbtn_add: QRadioButton = self.window.findChild(QRadioButton, "rbtn_add")
        self.rbtn_rewrite: QRadioButton = self.window.findChild(QRadioButton, "rbtn_rewrite")

        self.menu_file = self.window.findChild(QMenu, 'menuFile').actions()
        self.menu_new = self.menu_file[0]
        self.menu_load = self.menu_file[1]
        self.menu_save = self.menu_file[2]
        self.menu_save_as = self.menu_file[3]
        self.menu_import_pic = self.menu_file[5]
        self.menu_settings = self.window.findChild(QMenu, 'menuSettings').actions()[0]
        self.sc_record: QtWidgets.QShortcut = QtWidgets.QShortcut(QKeySequence('Ctrl+R'), self.btn_record)

        self.btn_add.clicked.connect(self.add_row)
        self.btn_remove.clicked.connect(self.remove_row)
        self.btn_up.clicked.connect(self.up_row)
        self.btn_down.clicked.connect(self.down_row)
        self.btn_merge.clicked.connect(self.merge_row)
        self.btn_split.clicked.connect(self.split_row)
        self.btn_record.clicked.connect(self.toggle_recording)

        self.rbtn_add.clicked.connect(self.check_add_mode)
        self.rbtn_rewrite.clicked.connect(self.check_rewrite_mode)

        self.menu_new.triggered.connect(self.new_pic_action)
        self.menu_load.triggered.connect(self.load)
        self.menu_import_pic.triggered.connect(self.import_picture)
        self.menu_save.triggered.connect(self.save_short)
        self.menu_save_as.triggered.connect(self.save_full)
        #self.act_record.triggered.connect(lambda: print('11'))
        #print (self.act_record)
        # self.menu_settings.triggered.connect(self.test)

        self.rbtn_add.setChecked(True)
        self.window.installEventFilter(self)
        self.window.show()

        self.tab_action.setRowCount(0)
        self.act_picture.setPixmap(QtGui.QPixmap(self.DEFAULT_PICTURE))

    def eventFilter(self, obj, event: QEvent):
        if obj == self.window and self.is_recording:
            if event.type() == QEvent.MouseButtonPress:
                self.write_to_table(MainGame.invert_mouse_event(event))
            elif event.type() == QEvent.KeyPress and not event.isAutoRepeat():
                key_seq = MainGame.hook_key_event(event)
                if key_seq == True:
                    return True
                self.write_to_table(key_seq.toString())
            elif event.type() == QEvent.KeyRelease and event.key() == Qt.Key_Tab:
                self.write_to_table(QKeySequence(Qt.Key_Tab))
            else:
                return False
        try:
            return QWidget.eventFilter(self, obj, event)
        except RuntimeError:
            return True

    def write_to_table(self, data):
        if self.is_rewriting_mode:
            self.rbtn_add.setChecked(True)
            self.rbtn_add.setChecked(False)
            self.is_rewriting_mode = False

        self.add_row()
        self.tab_action.rowCount()
        self.tab_action.setItem(self.tab_action.rowCount()-1, 0, QTableWidgetItem(data))

    def toggle_recording(self):
        name_state = {
            True: 'Stop',
            False: 'Start'
        }
        self.is_recording = not self.is_recording
        self.btn_record.setText(name_state.get(self.is_recording))

    def add_row(self):
        selection = set([id.row() for id in self.tab_action.selectedIndexes()])
        row_id = self.tab_action.rowCount()
        if selection:
            row_id = max(selection)+1

        self.tab_action.insertRow(row_id)
        self.is_saved = False

    def remove_row(self):
        sel_row = self.tab_action.currentRow()
        self.tab_action.removeRow(sel_row)
        self.is_saved = False

    def up_row(self):
        self.move_row(self.UP)
        self.is_saved = False

    def down_row(self):
        self.move_row(self.DOWN)
        self.is_saved = False

    def merge_row(self):
        model = self.tab_action.model()
        selected_rows = list(set([id.row() for id in self.tab_action.selectedIndexes()]))

        if selected_rows:
            data = ''
            for row in selected_rows:
                id = model.index(row, 0)
                data += (str(model.data(id)))

            first_cell_row = selected_rows[0]
            self.tab_action.setItem(first_cell_row, 0, QTableWidgetItem(data))
            print(invert_table_key(data))

            for row in range(1, len(selected_rows)):
                self.tab_action.removeRow(first_cell_row+1)

    def split_row(self):
        print (MainGame.hex_to_modifiers('09'))

    def load(self):
        if not self.is_saved:
            ret_val = self.show_exit_save_dialog()
            if ret_val == QMessageBox.Save:
                self.save_short()
                if self.is_saved:
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

    def check_add_mode(self):
        self.change_mode('add')

    def check_rewrite_mode(self):
        self.change_mode('rewrite')

    def change_mode(self, button):
        if button == 'add':
            self.is_rewriting_mode = False
        elif button == 'rewrite' and not self.is_rewriting_mode:
            self.tab_action.setRowCount(0)
            self.is_rewriting_mode = True

    def move_row(self, direction):
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
            self.is_saved = False
        elif direction == self.DOWN and row_id != self.tab_action.rowCount() - 1:
            self.tab_action.insertRow(row_id + 2)
            self.tab_action.setItem(row_id + 2, 0, QTableWidgetItem(key_cell))
            self.tab_action.setItem(row_id + 2, 1, QTableWidgetItem(com_cell))
            self.tab_action.removeRow(row_id)
            self.tab_action.setCurrentCell(row_id + 1, col_id)
            self.is_saved = False
        else:
            return

    def show_loading_act_dialog(self):
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
        self.tab_action.setRowCount(len(data) - CsvParams.SHIFT_TO_CONTENT)
        #CsvParams.SHIFT_TO_CONTENT
        for row in range(self.tab_action.rowCount()):
            self.tab_action.setItem(row, 0, QTableWidgetItem(data[row + CsvParams.SHIFT_TO_CONTENT][0]))
            self.tab_action.setItem(row, 1, QTableWidgetItem(data[row + CsvParams.SHIFT_TO_CONTENT][1]))

        name = data[0][1]
        pic_url = str(data[CsvParams.PICTURE_ROW][1])
        self.act_picture.setPixmap(QtGui.QPixmap(pic_url))
        self.le_name.setText(name)

        self.is_saved = True
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
            self.is_saved = True

        if self.is_saved:
            refresh_space()
        else:
            res_val = self.show_exit_save_dialog()
            if res_val == QMessageBox.Save:
                self.save_short()
                if self.is_saved:
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
                self.is_saved = True
        else:
            self.write_files(self.csv_linked_path)
            self.is_saved = True

    def import_picture(self):
        file_name = QFileDialog.getOpenFileName(None, "Open Image", os.getcwd() + '\\actions\\pictures',
                                                "Image Files (*.png *.jpg *.bmp)")
        if file_name[0] is not '':
            self.act_picture.setPixmap(QtGui.QPixmap(file_name[0]))
            #self.picture_action_global.picture_url = file_name[0]
            self.is_saved = False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = ActionWindow('ui\ActionMain.ui')
    sys.exit(app.exec_())
