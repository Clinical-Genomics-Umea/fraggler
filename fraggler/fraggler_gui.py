import os
import platform
import sys
import glob
import traceback
import time
# from .fraggler import fraggler
from fraggler import fraggler_gui_elements as Ui_MainWindow, log_config, ladders, fraggler
# from . import fraggler_gui_elements as Ui_MainWindow, log_config, ladders

from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox, QLabel, QVBoxLayout, QDialog, QListWidgetItem
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtUiTools import QUiLoader
import logging
from PySide6.QtWebEngineCore import QWebEngineSettings  # Add this line
import PySide6.QtWidgets as QtWidgets  # Add this line
from PySide6.QtCore import QTimer


import logging
from PySide6.QtWidgets import QPlainTextEdit
import PySide6.QtCore as QtCore

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.subprocess = None  # Initialize subprocess attribute
        self.fp = None
        self.loaded_files = []
        self.output_folder = None

        # Check if the system theme is dark or light
        self.system_theme = self.get_system_theme()
        # Apply the system theme
        if self.system_theme == "dark":
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

 # Add it to the layout

        self.setupLogging()
        self.initMenuActions()
        self.initButtonActions()
        self.initComboBoxActions()
        # add widget to layout
        self.initIcons()
        self.setupStatusBar()
        self.update_status_indicator()
        # Setup QTimer (not deemed necessary for slowing down application)
        self.statusUpdateTimer = QTimer(self)
        self.statusUpdateTimer.timeout.connect(self.update_status_indicator)
        self.statusUpdateTimer.start(
            10000
        )  # Timer interval set to 10000 milliseconds (10 second)


        self.ui.webEngineView.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        self.ui.webEngineView.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.showMaximized()
    
    def display_report(self, file_name):
        """Display the generated report in QWebEngineView."""
        if not self.output_folder:
            self.logger.info(f"Run Fraggler to access file reports")
            return
        try:
            report_pattern = f"{self.output_folder}/{file_name}_*.html"
            report_files = glob.glob(report_pattern)
            if report_files:
                report_path = report_files[0]
                self.ui.webEngineView.load(QUrl.fromLocalFile(report_path))
                self.ui.webEngineView.show()
                self.logger.info(f"Showing report: {report_path}")
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            self.logger.error(f"Unable to find fraggler report for {file_name} in {self.output_folder}")
            self.logger.info("Reselect directory and run Fraggler again if issue persists.")

    def handle_error(self, error_message):
        """Handle error if any occurs."""
        QMessageBox.critical(self, "Error", error_message)

    ################## INITIALIZATION ##################
    def initMenuActions(self):
        self.ui.action_loadFSAFile.triggered.connect(self.loadFSAFile)
        self.ui.actionToggle_Dark_Light.triggered.connect(self.toggle_theme)
        self.ui.action_about.triggered.connect(self.about)

    def initButtonActions(self):
        self.ui.selectFileButton.clicked.connect(self.loadFSAFile)
        self.ui.selectDirectoryButton.clicked.connect(self.loadFSADirectory)    
        self.ui.fileListWidget.itemClicked.connect(self.onFileListItemClicked)
        self.ui.runFragglerButton.clicked.connect(self.start)

    def initComboBoxActions(self):
        self.ui.typeComboBox.addItems(fraggler.TYPES)
        self.ui.peakModelComboBox.addItems(fraggler.PEAK_AREA_MODELS)
        self.ui.ladderComboBox.addItems(ladders.LADDERS.keys())

    def initIcons(self):
        self.icon = QIcon()
        self.icon.addFile(
            os.path.join(os.path.dirname(__file__), "icons", "icon.ico"),
            QSize(),
            QIcon.Normal,
            QIcon.Off,
        )
        self.setWindowIcon(self.icon)
        pixmap = QPixmap(os.path.join(os.path.dirname(__file__), "icons", "logo.png"))
        scaled_pixmap = pixmap.scaledToHeight(50, Qt.SmoothTransformation)
        self.ui.label_icon.setPixmap(scaled_pixmap)

    ############### LOGGING ###############
    def log(self, msg, level="none", asctime="none", class_name="none"):
        # Add the message to the status bar and list widget
        self.statusBar().showMessage(msg)
        msg = f"{asctime} \t {class_name} \t {msg}"
        item = QListWidgetItem(msg)
        self.ui.listWidget.insertItem(0, item)
        
    def setupLogging(self):
        # Configure logging to use the QTextEditLogger
        self.logger = logging.getLogger("FragglerGUI")
        self.logger.setLevel(logging.INFO)
        self.log_handler = MainWindowLoggingHandler(self.log)
        logging.getLogger().addHandler(self.log_handler)

    def get_system_theme(self):
        self.system = platform.system()
        if self.system == "Windows":
            import winreg
            registry_key = winreg.HKEY_CURRENT_USER
            sub_key = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            value_name = "AppsUseLightTheme"
            try:
                key = winreg.OpenKey(registry_key, sub_key, 0, winreg.KEY_READ)
                value = winreg.QueryValueEx(key, value_name)
                winreg.CloseKey(key)
                if value[0] == 0:
                    self.system_theme = "dark"
                else:
                    self.system_theme = "light"
            except FileNotFoundError:
                self.system_theme = "dark"
            except Exception as e:
                print(f"Error: {e}")
                self.system_theme = "light"

    def apply_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(35, 35, 35))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(53, 53, 53))
        palette.setColor(QPalette.AlternateBase, QColor(25, 25, 25))
        palette.setColor(QPalette.ToolTipBase, Qt.black)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(25, 25, 25))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(0, 120, 215))
        palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        self.setPalette(palette)
        self.system_theme = "dark"
    def apply_light_theme(self):
        light_palette = QPalette()
        light_palette.setColor(QPalette.Window, QColor(240, 240, 240))
        light_palette.setColor(QPalette.WindowText, Qt.black)
        light_palette.setColor(QPalette.Base, QColor(255, 255, 255))
        light_palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
        light_palette.setColor(QPalette.ToolTipBase, Qt.white)
        light_palette.setColor(QPalette.ToolTipText, Qt.black)
        light_palette.setColor(QPalette.Text, Qt.black)
        light_palette.setColor(QPalette.Button, QColor(240, 240, 240))
        light_palette.setColor(QPalette.ButtonText, Qt.black)
        light_palette.setColor(QPalette.BrightText, Qt.red)
        light_palette.setColor(QPalette.Link, QColor(0, 120, 215))
        light_palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        light_palette.setColor(QPalette.HighlightedText, Qt.white)
        self.setPalette(light_palette)
        self.system_theme = "light"
    def toggle_theme(self):
        if self.system_theme == "dark":
            self.apply_light_theme()
        else:
            self.apply_dark_theme()

    def setupStatusBar(self):
        # Add a permanent widget (label) to the right
        self.serviceStatusLabel = QLabel(self.ui.statusbar)
        self.ui.statusbar.addPermanentWidget(self.serviceStatusLabel)

    def update_status_indicator(self):
        self.serviceStatusLabel.setText("Service: Running")

    def about(self):
        # Open up the about dialog
        class AboutDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("About")
                self.layout = QVBoxLayout(self)
                self.label = QLabel(
                    "This is a GUI application for the Fraggler fragment analysis package.\n\n"
                    "Fraggler is used for DNA fragment analysis.\n\n"
                    "Developed by: Thaddaeus Sandidge [PLNU Software Engineering]\n\n"
                    "Date: 09/27/2024\n\n"
                    "Version: 1.0.0"
                )
                self.layout.addWidget(self.label)
        dialog = AboutDialog()
        dialog.setWindowIcon(self.icon)
        if self.system_theme == "dark":
            dialog.setStyleSheet(
                "background-color: rgb(35, 35, 35); color: rgb(255, 255, 255);"
            )
        else:
            dialog.setStyleSheet(
                "background-color: rgb(240, 240, 240); color: rgb(0, 0, 0);"
            )
        dialog.exec_()

    ############### ENABLE/DISABLE ###############
    def enableButtons(self):
        self.ui.runFragglerButton.setEnabled(True)
        self.ui.selectFileButton.setEnabled(True)
        self.display_report(self.loaded_files[0])


    def disableButtons(self):
        self.ui.runFragglerButton.setEnabled(False)
        self.ui.selectFileButton.setEnabled(False)

    ############### LOAD FSA FILE ###############

    def loadFSAFile(self):
        """Load a single FSA file and display it in the file list widget."""
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        # Open file dialog to select a single FSA file
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select FSA File", "", "FSA Files (*.fsa);;All Files (*)", options=options
        )

        if not file_path:
            return

        # Clear previous items in fileListWidget and the loaded files list
        self.ui.fileListWidget.clear()
        self.loaded_files.clear()

        # Process the selected file
        file_name = os.path.basename(file_path)
        self.ui.fileListWidget.addItem(file_name)
        self.loaded_files.append(file_name)
        self.logger.info(f"Loaded FSA file: {file_path}")
        self.fp = file_path

    def loadFSADirectory(self):
        """Load all FSA files in a selected directory and display them in the file list widget."""
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        # Open directory dialog to select a directory
        directory_path = QFileDialog.getExistingDirectory(
            self, "Select Directory with FSA Files", "", options=options
        )

        if not directory_path:
            return

        # Clear previous items in fileListWidget and the loaded files list
        self.ui.fileListWidget.clear()
        self.loaded_files.clear()

        # List all .fsa files in the selected directory
        fsa_files = [
            f for f in os.listdir(directory_path) if f.lower().endswith('.fsa')
        ]
        for fsa_file in fsa_files:
            file_path = os.path.join(directory_path, fsa_file)
            self.ui.fileListWidget.addItem(fsa_file)
            self.loaded_files.append(fsa_file)
            self.logger.info(f"Loaded FSA file from directory: {file_path}")
        self.fp = directory_path

    def onFileListItemClicked(self, item):
        """Handle the click event for items in fileListWidget."""
        self.logger.info(f"Selected FSA file: {item.text()}")
        self.display_report(item.text())

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            self.loadFSAFile(url.toLocalFile())

    ############### VALIDATION #############
    def validateEntries(self):
        if self.fp == None or self.fp == "":
            self.logger.error("No file imported, please import FSA file")
            return False
        if self.ui.sampleChannelInput.text() == "":
            self.logger.error("Sample channel is empty, please input a valid sample channel. E.g. 'DATA1', 'DATA2'...")
            return False
        if self.ui.outputFolderInput.text() == "":
            self.logger.error("Output folder input is empty, please input a valid output folder name")
            return False
        return True


    ############### RUN FRAGGLER CLI ###############
       
    def reportProgress(self, message):
        self.logger.info("Progress: %s", message)
    
    def start(self):
        self.runFraggler()

    def runFraggler(self):
        if not self.validateEntries():
            self.logger.info("Invalid entries...")
            return
        self.logger.info("Running Fraggler with file %s", self.fp)
        self.output_folder = os.path.join(os.getcwd(), self.ui.outputFolderInput.text())



        # Set up worker and thread for running Fraggler
        self.worker = Worker(self)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)


        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.log_message.connect(self.reportProgress)
        self.worker.error.connect(self.handle_error)
        self.worker.finished.connect(self.enableButtons)

        # Start the thread
        self.thread.start()


    def setLoading(self):
        """Set the loading spinner HTML content in the QWebEngineView."""
        loading_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Loading...</title>
            <style>
                body {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    background-color: #f3f3f3;
                }
                .spinner {
                    border: 16px solid #f3f3f3;
                    border-top: 16px solid #3498db;
                    border-radius: 50%;
                    width: 120px;
                    height: 120px;
                    animation: spin 2s linear infinite;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        </head>
        <body>
            <div class="spinner"></div>
        </body>
        </html>
        """
        self.ui.webEngineView.setHtml(loading_html)
        self.ui.webEngineView.show()
        QApplication.processEvents()  # Ensure the UI updates are processed
        

class Worker(QObject):
    finished = Signal()
    error = Signal(str)
    log_message = Signal(str)  # New signal for logging messages


    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.logger = logging.getLogger("FragglerGUI")


    def run(self):
        try:
            report = fraggler.runFraggler(
                type=self.parent.ui.typeComboBox.currentText(),
                fsa=self.parent.fp,
                output=self.parent.ui.outputFolderInput.text() or None,
                ladder=self.parent.ui.ladderComboBox.currentText() or None,
                sample_channel=self.parent.ui.sampleChannelInput.text() or None,
                min_distance_between_peaks=int(self.parent.ui.minDistBetweenPeaksInput.text() or 0),
                min_size_standard_height=int(self.parent.ui.minHeightPeakInput.text() or 0),
                custom_peaks=self.parent.ui.customPeaksInput.text() or None,
                peak_height_sample_data=int(self.parent.ui.minPeakHeightInput.text() or 0),
                min_ratio_to_allow_peak=float(self.parent.ui.minPeakRatioInput.text() or 0),
                distance_between_assays=int(self.parent.ui.minDistAssaysInput.text() or 0),
                search_peaks_start=int(self.parent.ui.peakStartInput.text() or 0),
                peak_area_model=self.parent.ui.peakModelComboBox.currentText() or None,
            )
            self.parent.logger.info("Fraggler run successful")
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()

class MainWindowLoggingHandler(logging.Handler):
    def __init__(self, log_method):
        super().__init__()
        self.log_method = log_method

    def emit(self, record):
        message = self.format(record)
        levelname = record.levelname
        asctime = record.asctime
        class_name = record.name
        self.log_method(message, levelname, asctime, class_name)


def run():
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    window = MainWindow()
    window.show()
    logger = log_config.get_logger("FragglerGUI")
    try:
        logger.info("Welcome to Fraggler GUI, load a FSA file to get started.")
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(app.exec_())


if __name__ == "__main__":
    run()
