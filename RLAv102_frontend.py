import sys, os, PySide2, re
import RLAv102_backend

from PySide2 import QtWidgets, QtCore
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QPixmap

dirname = os.path.dirname(PySide2.__file__)  # Bug fix
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

if not os.path.exists("images"):
    os.mkdir("images")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RLA v1.0.2")  # Window
        self.setFixedSize(QSize(400, 300))
        self.selections = 0
        self.directory = ''

        layout = QVBoxLayout()  # Layouts
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()

        title = QLabel("RENDER LOG ANALYSIS")  # Title
        title.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        title.setFixedHeight(50)

        directory_message = QLabel("Select directory:")  # Browse for folder
        self.button_browse = QPushButton("Browse for Folder")
        self.button_browse.setCheckable(True)
        self.button_browse.clicked.connect(self.browse_button_was_clicked)

        file_message = QLabel("Select file:")  # Logs dropdown list
        self.file_select = QComboBox()
        self.file_select.activated.connect(self.activated)

        self.button_confirm = QPushButton("OK")  # Opens log details window
        self.button_confirm.setCheckable(True)
        self.button_confirm.clicked.connect(self.open_logs)

        layout.addWidget(title)  # Add widgets to main window
        layout2.addWidget(directory_message, Qt.AlignRight)
        layout2.addWidget(self.button_browse, Qt.AlignLeft)
        layout.addLayout(layout2)
        layout3.addWidget(file_message, Qt.AlignLeft)
        layout3.addWidget(self.file_select)
        layout.addLayout(layout3)
        layout.addWidget(self.button_confirm)

        widget_final = QWidget()
        widget_final.setLayout(layout)
        self.setCentralWidget(widget_final)

    def browse_button_was_clicked(self):  # Browse button function
        self.directory = QFileDialog.getExistingDirectory()
        self.selections = 0
        if self.directory == '':  # No directory error
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('Directory not selected')
            msg.setWindowTitle("Error")
            msg.exec_()
        else:
            self.button_browse.setText(self.directory)  # Add logs to dropdown
            self.logs = RLAv102_backend.Logs_in_dir(self.directory).get_logs()
            self.file_select.clear()
            for files in self.logs:
                self.file_select.addItem(files)

    def open_logs(self, s):  # Autoselect file
        if self.directory == '':
            msg_no_dir = QMessageBox()
            msg_no_dir.setIcon(QMessageBox.Critical)
            msg_no_dir.setText("Error")
            msg_no_dir.setInformativeText('Please select a directory')
            msg_no_dir.setWindowTitle("Error")
            msg_no_dir.exec_()

        elif self.logs == []:
            msg_no_logs = QMessageBox()
            msg_no_logs.setIcon(QMessageBox.Critical)
            msg_no_logs.setText("Error")
            msg_no_logs.setInformativeText('There are no logs in your directory')
            msg_no_logs.setWindowTitle("Error")
            msg_no_logs.exec_()

        elif self.selections > 0:
            self.dialog = Log(self, self.logs[self.index], self.directory)
            self.dialog.show()
        else:
            self.dialog = Log(self, self.logs[0], self.directory)
            self.dialog.show()

    def activated(self, index):
        self.index = index
        self.selections += 1


class Log(QMainWindow):
    def __init__(self, parent=None, log_name=None, log_path=None):
        super(Log, self).__init__(parent)

        self.setWindowTitle(log_name)  # Set file name as window name
        self.setFixedSize(QSize(1200, 1000))

        layout4 = QVBoxLayout()  # Layouts
        layout5 = QHBoxLayout()
        layout6 = QVBoxLayout()

        title = QLabel(RLAv102_backend.Render_log(log_name, log_path).get_title())  # title
        title.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        user = QLabel(RLAv102_backend.Render_log(log_name, log_path).get_user())  # Username
        user.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        user.setFixedHeight(50)

        times, utilization = RLAv102_backend.Render_log(log_name, log_path).get_time_utilization(
            ['Elapsed', 'scene creation time', 'frame time'])

        e_time = QLabel("ELAPSED TIME: " + str(times['Elapsed'][0]))  # Elapsed time
        e_time.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        sc_time = QLabel("SCENE CREATION TIME: " + str(times['scene creation time'][0]))  # Scene Creation Time
        sc_time.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        f_time = QLabel("FRAME TIME: " + str(times['frame time'][0]))  # Frame time
        f_time.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        sc_utilization_int = int(
            re.search(r'\d+', str(utilization['scene creation time'])).group())  # Get utilization as an integer
        scene_image_name = 'Scene Creation Utilization'
        RLAv102_backend.get_utilization_gauge(sc_utilization_int, scene_image_name, log_name)

        sc_gauge = QLabel(self)
        pixmap = QPixmap("images/" + log_name + " Scene Creation Utilization %.png")
        pixmap = pixmap.scaled(500, 500, QtCore.Qt.KeepAspectRatio)
        sc_gauge.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())
        sc_gauge.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        f_utilization_int = int(
            re.search(r'\d+', str(utilization['frame time'])).group())  # Get utilization as an integer
        frame_image_name = 'Frame Utilization'
        RLAv102_backend.get_utilization_gauge(f_utilization_int, frame_image_name, log_name)

        f_gauge = QLabel(self)
        pixmap = QPixmap("images/" + log_name + " Frame Utilization %.png")
        pixmap = pixmap.scaled(500, 500, QtCore.Qt.KeepAspectRatio)
        f_gauge.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())
        f_gauge.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        memory = QLabel("PEAK MEMORY: " + str(RLAv102_backend.Render_log(log_name, log_path).get_memory()))  # Peak memory
        memory.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        memory.setFixedHeight(50)

        tagged_lines = RLAv102_backend.Render_log(log_name, log_path).get_errors_warnings(['WARNING'])  # Warnings
        warnings = QtWidgets.QListWidget()
        for i in tagged_lines:
            warnings.addItem(i)
        tagged_lines = RLAv102_backend.Render_log(log_name, log_path).get_errors_warnings(['ERROR'])  # Errors
        errors = QtWidgets.QListWidget()
        for i in tagged_lines:
            errors.addItem(i)

        layout4.addWidget(title)  # Add widgets to main window
        layout4.addWidget(user)
        layout4.addWidget(e_time)
        layout4.addWidget(sc_time)
        layout4.addWidget(f_time)
        layout4.addWidget(memory)
        layout4.addLayout(layout5)
        layout5.addWidget(sc_gauge)
        layout5.addWidget(f_gauge)
        layout4.addLayout(layout6)
        layout6.addWidget(warnings)
        layout6.addWidget(errors)

        widget_final = QWidget()
        widget_final.setLayout(layout4)
        self.setCentralWidget(widget_final)


if not QApplication.instance():  # Bug fix
    app = QApplication(sys.argv)
else:
    app = QApplication.instance()

window = MainWindow()
window.show()

app.exec_()
