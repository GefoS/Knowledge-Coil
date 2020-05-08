import sys, os, csv
from shutil import copyfile

from PySide2 import QtGui, QtWidgets
from PySide2 import QtXml
from PySide2.QtGui import QKeySequence
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QPushButton, QLineEdit, QTableWidget, QLabel, QTableWidgetItem, \
    QMenu, QMessageBox, QFileDialog, QWidget, QRadioButton, QAction, QComboBox
from PySide2.QtCore import QFile, QEvent, Qt

import EventHandler
import SettingsParser
import icons.ui_icons
from global_params import CsvParams, KeyShortcuts

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
        self.CUSTOM_COMMAND_ROW = 'Custom command...'
        self.UP = 1
        self.DOWN = -1

        self.is_saved = True
        self.is_recording = False
        self.is_rewriting_mode = False # add -> false, rewrite -> true

        self.csv_linked_path = ''
        self.opened_box_id = -1
        self.keys_map = dict()
        if 'key_settings.xml' in (os.listdir(os.getcwd()+'\\settings')):
            self.keys_map = SettingsParser.parse_to_sequence(os.getcwd() + '\\settings\\key_settings.xml')
        self.custom_commands = dict()
        self.command_box = QComboBox()
        self.complex_keys = list()

        super(ActionWindow, self).__init__(parent)
        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()

        #icons = QResource.registerResource()

        # tab
        self.tab_action:QTableWidget = self.window.findChild(QTableWidget, "tab_action")
        self.tab_action.horizontalHeader().setStretchLastSection(True)

        self.btn_add = self.window.findChild(QPushButton, "btn_add")
        self.btn_down = self.window.findChild(QPushButton, "btn_down")
        self.btn_up = self.window.findChild(QPushButton, "btn_up")
        self.btn_remove = self.window.findChild(QPushButton, "btn_remove")
        self.btn_merge:QPushButton = self.window.findChild(QPushButton, "btn_merge")

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
        self.menu_settings:QAction = self.window.findChild(QMenu, 'menuSettings').actions()[0]
        self.sc_record: QtWidgets.QShortcut = QtWidgets.QShortcut(QKeySequence('Ctrl+R'), self.btn_record)

        self.btn_add.clicked.connect(self.add_row)
        self.btn_remove.clicked.connect(self.remove_row)
        self.btn_up.clicked.connect(self.up_row)
        self.btn_down.clicked.connect(self.down_row)
        self.btn_merge.clicked.connect(self.merge_row)
        self.btn_record.clicked.connect(self.toggle_recording)

        self.command_box.textActivated.connect(lambda command: self.close_box_in_cell(command))

        self.rbtn_add.clicked.connect(self.check_add_mode)
        self.rbtn_rewrite.clicked.connect(self.check_rewrite_mode)

        #self.tab_action.itemChanged.connect(self.unsaved)
        self.tab_action.itemChanged.connect(self.unsaved)
        self.tab_action.cellClicked.connect(lambda row, column: self.init_box_signal(row, column))

        self.menu_new.triggered.connect(self.new_pic_action)
        self.menu_import_pic.triggered.connect(self.import_picture)
        self.menu_save.triggered.connect(self.save_short)
        self.menu_save_as.triggered.connect(self.save_full)
        self.menu_settings.triggered.connect(self.show_loading_settings_dialog)
        self.menu_load.triggered.connect(self.load_action)

        self.rbtn_add.setChecked(True)
        self.window.installEventFilter(self)
        self.act_picture.setPixmap(QtGui.QPixmap(self.DEFAULT_PICTURE))
        self.tab_action.setRowCount(0)

        self.window.show()

    def eventFilter(self, obj, event: QEvent):
        if obj == self.window and self.is_recording:
            if event.type() == QEvent.MouseButtonPress:
                self.write_to_table(EventHandler.invert_mouse_event(event))
            elif event.type() == QEvent.KeyPress and not event.isAutoRepeat():
                key = EventHandler.hook_key_event(event)
                if key == True:
                    return True
                self.write_to_table(QKeySequence(key).toString())
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

        row_id = self.add_row()
        self.tab_action.rowCount()
        self.tab_action.setItem(row_id, 0, QTableWidgetItem(data))

    def toggle_recording(self):
        name_state = {
            True: 'Stop',
            False: 'Start'
        }
        self.is_recording = not self.is_recording
        self.btn_record.setText(name_state.get(self.is_recording))

    def init_box_signal(self, row, column):
        if column == 0:
            return
        self.init_box_in_cell(row)

    def close_box_in_cell(self, row, selected_command):
        self.tab_action.removeCellWidget(row, 1)
        if selected_command == self.CUSTOM_COMMAND_ROW:
            self.tab_action.setItem(row, 1, QTableWidgetItem(''))
            self.tab_action.edit(self.tab_action.model().index(row, 1))
        else:
            item = QTableWidgetItem(selected_command)
            self.tab_action.setItem(row, 1, item)

    def init_box_in_cell(self, row):
        try:
            key = self.tab_action.item(row, 0).text()
        except AttributeError:
            return
        commands = self.keys_map.get(key, False)
        if not key or not commands:
            return

        self.command_box.clear()
        if isinstance(commands, list):
            if self.CUSTOM_COMMAND_ROW not in commands:
                commands.insert(0, self.CUSTOM_COMMAND_ROW)
            try:
                custom_command = self.tab_action.item(row, 1).text()
                if custom_command not in commands:
                    commands.insert(1, custom_command)
            except AttributeError:
                pass
            finally:
                box = QComboBox()
                box.insertItems(0, commands)
                box.setCurrentIndex(1)
                self.tab_action.setCellWidget(row, 1, box)

                box.textActivated.connect(lambda command:self.close_box_in_cell(row, command))
        else:
            self.tab_action.setItem(row, 1, QTableWidgetItem(commands))

    def add_row(self):
        selection = set([id.row() for id in self.tab_action.selectedIndexes()])
        row_id = self.tab_action.rowCount()
        if selection:
            row_id = max(selection)+1

        self.tab_action.insertRow(row_id)
        self.is_saved = False
        self.tab_action.setCurrentCell(row_id, 0)

        return row_id

    def remove_row(self):
        sel_row = self.tab_action.currentRow()
        self.tab_action.removeRow(sel_row)
        self.tab_action.setCurrentCell(sel_row-1, 0)
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

        if len(selected_rows) > 1:
            data = ''
            self.complex_keys.append([])
            for row in selected_rows:
                id = model.index(row, 0)
                key = str(model.data(id))
                self.complex_keys[-1].append(key)
                data += (key)

            first_cell_row = selected_rows[0]
            self.tab_action.setItem(first_cell_row, 0, QTableWidgetItem(data))

            for row in range(1, len(selected_rows)):
                self.tab_action.removeRow(first_cell_row+1)

    def split_row(self):
        for k, v in self.keys_map.items():
            print (k, v)

    def load_action(self):
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

        new_row_id = 0
        if direction == self.UP and row_id != 0:
            new_row_id = row_id - 1
            self.tab_action.insertRow(new_row_id)
            self.tab_action.setItem(new_row_id, 0, QTableWidgetItem(key_cell))
            self.tab_action.setItem(new_row_id, 1, QTableWidgetItem(com_cell))
            self.tab_action.removeRow(new_row_id+2)
            self.tab_action.setCurrentCell(new_row_id, col_id)
            self.is_saved = False
        elif direction == self.DOWN and row_id != self.tab_action.rowCount() - 1:
            new_row_id = row_id + 2
            self.tab_action.insertRow(new_row_id)
            self.tab_action.setItem(new_row_id, 0, QTableWidgetItem(key_cell))
            self.tab_action.setItem(new_row_id, 1, QTableWidgetItem(com_cell))
            self.tab_action.removeRow(row_id)
            new_row_id -= 1
            self.tab_action.setCurrentCell(new_row_id, col_id)
            self.is_saved = False
        else:
            return

    def show_loading_settings_dialog(self):
        xml_path = QFileDialog.getOpenFileName(None, "Load Picture Action", os.getcwd() + '\\actions',
                                                    "XML file (*.xml)")[0]
        if xml_path:
            self.keys_map = SettingsParser.parse_to_sequence(xml_path)
            cwd = os.getcwd().__str__()
            copyfile(xml_path, cwd+'\\settings\\key_settings.xml')

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
        complex_keys_map = self.complex_keys_map()

        for row in range(model.rowCount()):
            data.append([])
            for col in range(model.columnCount()):
                index = model.index(row, col)
                cell_data = str(model.data(index))
                complex_key = complex_keys_map.get(index, False)
                if complex_key:
                    cell_data = complex_key
                if cell_data == 'None':
                    cell_data = ''
                data[row].append(cell_data)
        return data

    def assign_complex_keys(self, data):
        key_column = [k[0] for k in data]
        for key in key_column:
            if CsvParams.COMPLEX_KEY_DELIMITER in key:
                self.complex_keys.append(key.split(':'))

    def complex_keys_map(self):
        key_map = dict()
        model = self.tab_action.model()

        for complex_key in self.complex_keys:
            full_key = ''.join(complex_key)
            for row in range(model.rowCount()):
                index = model.index(row, 0)
                if full_key == str(model.data(index)):
                    key_map[index] = ':'.join(complex_key)
        return key_map

    def load_pic_action(self, csv_path):
        data = []
        with open(csv_path, newline='') as pic_file:
            reader = csv.reader(pic_file, delimiter=',', quotechar='|')
            data = list(reader)
        self.tab_action.setRowCount(len(data) - CsvParams.SHIFT_TO_CONTENT)
        self.assign_complex_keys(data[CsvParams.SHIFT_TO_CONTENT:])

        for row in range(self.tab_action.rowCount()):
            key_cell = data[row + CsvParams.SHIFT_TO_CONTENT][0]
            if ':' in key_cell:
                key_cell = key_cell.replace(':', '')
            self.tab_action.setItem(row, 0, QTableWidgetItem(key_cell))
            self.tab_action.setItem(row, 1, QTableWidgetItem(data[row + CsvParams.SHIFT_TO_CONTENT][1]))

        name = data[CsvParams.NAME_ROW][1]
        pic_url = str(data[CsvParams.PICTURE_ROW][1])
        self.act_picture.setPixmap(QtGui.QPixmap(pic_url))
        self.le_name.setText(name)
        self.is_saved = True
        self.csv_linked_path = csv_path

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
            csv_writer.writerow(['name', pic_name])
            csv_writer.writerow(['pic_path', pic_path])
            csv_writer.writerow(['Key', 'Command'])
            for row in self.get_table_data():
                csv_writer.writerow(row)

        self.act_picture.pixmap().save(pic_path, format='PNG')

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

    def unsaved(self):
        self.is_saved = False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = ActionWindow('ui\ActionMain.ui')
    sys.exit(app.exec_())
