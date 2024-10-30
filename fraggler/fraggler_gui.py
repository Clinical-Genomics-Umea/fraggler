import os
import platform
import sys
import glob

from . import fraggler_gui_elements as Ui_MainWindow, log_config, ladders, fraggler
from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox, QLabel, QVBoxLayout, QDialog, QListWidgetItem
from PySide6.QtCore import *
from PySide6.QtGui import *
import logging
from PySide6.QtWebEngineCore import QWebEngineSettings 
from PySide6.QtCore import QTimer

class MainWindow(QMainWindow):
    """Main application window for the Fraggler GUI, handling the setup and interaction of UI components."""
    def __init__(self):
        """Initialize MainWindow, setting up the UI, system theme, logging, and connections for actions."""
        super().__init__()
        self.ui = Ui_MainWindow.Ui_MainWindow()
        self.ui.setupUi(self)

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

        # Set up GUI elements
        self.setupLogging()
        self.initMenuActions()
        self.initButtonActions()
        self.initComboBoxActions()
        self.initIcons()
        self.setupStatusBar()
        self.update_status_indicator()

        # Setup QTimer 
        self.statusUpdateTimer = QTimer(self)
        self.statusUpdateTimer.timeout.connect(self.update_status_indicator)
        self.statusUpdateTimer.start(
            10000
        )  # Timer interval set to 10000 milliseconds (10 second)

        # Set up QWebEngineView
        self.ui.webEngineView.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        self.ui.webEngineView.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.ui.webEngineView.setZoomFactor(0.75)
        self.display_default_html_report()
        self.showMaximized()
    
    ################## REPORT VIEWING ##################
    def display_report(self, file_name):
        """Display a specific report based on the provided file name.

        Args:
            file_name (str): The name of the file to locate and display in the web engine view.
        """
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
    
    def display_default_html_report(self):
        """Display the default HTML report in QWebEngineView."""
        default_html = self.get_default_html_report()
        self.ui.webEngineView.setHtml(default_html)
        self.ui.webEngineView.show()
    
    def get_default_html_report(self):
        """Return HTML content for the default welcome report.

        Returns:
            str: HTML content for the default report displayed when no specific file is loaded.
        """
        default_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to Fraggler GUI</title>
            <style>
                body {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    background-color: #f3f3f3;
                    font-family: Arial, sans-serif;
                    text-align: center;
                    color: #333;
                }
                .container {
                    max-width: 600px;
                    padding: 20px;
                    background-color: #fff;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    border-radius: 8px;
                }
                h1 {
                    font-size: 24px;
                    margin-bottom: 20px;
                }
                p {
                    font-size: 16px;
                    margin-bottom: 10px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Welcome to Fraggler GUI</h1>
                <p>Load an FSA File, set your parameters, and press Run Fraggler</p>
                <p>Please wait a moment for processing large FSA directories.</p>
            </div>
        </body>
        </html>
        """
        return default_html

    def handle_error(self, error_message):
        """Display an error message in a modal dialog.

        Args:
            error_message (str): The message to display.
        """
        QMessageBox.critical(self, "Error", error_message)

    def zoom_in(self):
        """Increase the zoom factor in the web view by a fixed increment."""
        current_zoom = self.ui.webEngineView.zoomFactor()
        self.ui.webEngineView.setZoomFactor(current_zoom + 0.1)

    def zoom_out(self):
        """Decrease the zoom factor in the web view by a fixed increment."""
        current_zoom = self.ui.webEngineView.zoomFactor()
        self.ui.webEngineView.setZoomFactor(current_zoom - 0.1)

    def onFragglerSuccess(self):
        """Handle successful Fraggler run by displaying the first loaded file's report and enabling controls."""
        self.ui.fileListWidget.setCurrentRow(0)
        self.display_report(self.loaded_files[0])
        self.enableButtons()


    ################## INITIALIZATION ##################
    def initMenuActions(self):
        """Connect menu actions to their respective handler functions."""
        self.ui.action_loadFSAFile.triggered.connect(self.loadFSAFile)
        self.ui.actionLoad_FSA_Directory.triggered.connect(self.loadFSADirectory)
        self.ui.actionZoom_In.triggered.connect(self.zoom_in)
        self.ui.actionZoom_Out.triggered.connect(self.zoom_out)
        self.ui.actionToggle_Dark_Light.triggered.connect(self.toggle_theme)
        self.ui.action_about.triggered.connect(self.about)

    def initButtonActions(self):
        """Connect button actions to their respective handler functions."""
        self.ui.selectFileButton.clicked.connect(self.loadFSAFile)
        self.ui.selectDirectoryButton.clicked.connect(self.loadFSADirectory)    
        self.ui.fileListWidget.itemClicked.connect(self.onFileListItemClicked)
        self.ui.runFragglerButton.clicked.connect(self.runFraggler)

    def initComboBoxActions(self):
        """Initialize combobox options with available selections."""
        self.ui.typeComboBox.addItems(fraggler.TYPES)
        self.ui.peakModelComboBox.addItems(fraggler.PEAK_AREA_MODELS)
        self.ui.ladderComboBox.addItems(ladders.LADDERS.keys())

    def initIcons(self):
        """Set the application window icon and add a logo to the UI."""
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
    
    def get_system_theme(self):
        """Retrieve the system theme based on OS settings.

        Returns:
            str: 'dark' or 'light' depending on the OS theme.
        """
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
        """Apply a dark color theme to the application interface."""
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
        """Apply a light color theme to the application interface."""
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
        """Toggle between dark and light themes based on the current system theme."""
        if self.system_theme == "dark":
            self.apply_light_theme()
        else:
            self.apply_dark_theme()

    ############### LOGGING ###############

    def log(self, msg, level="none", asctime="none", class_name="none"):
        """Add a log message to the status bar and the UI list widget.

        Args:
            msg (str): Message content.
            level (str): Log level.
            asctime (str): Timestamp.
            class_name (str): Class or context of the log message.
        """
        self.statusBar().showMessage(msg)
        msg = f"{asctime} \t {class_name} \t {msg}"
        item = QListWidgetItem(msg)
        self.ui.listWidget.insertItem(0, item)
        
    def setupLogging(self):
        """Configure logging for the application and initialize the main logging handler."""
        self.logger = logging.getLogger("FragglerGUI")
        self.logger.setLevel(logging.INFO)
        self.log_handler = MainWindowLoggingHandler(self.log)
        logging.getLogger().addHandler(self.log_handler)




    def setupStatusBar(self):
        """Set up the status bar with a permanent widget for the service status label."""
        # Add a permanent widget (label) to the right
        self.serviceStatusLabel = QLabel(self.ui.statusbar)
        self.ui.statusbar.addPermanentWidget(self.serviceStatusLabel)

    def update_status_indicator(self):
        """Update the service status label in the status bar."""
        self.serviceStatusLabel.setText("Service: Running")

    def about(self):
        """Display an about dialog with information about the application."""
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
        """Enable the run Fraggler and select file buttons."""
        self.ui.runFragglerButton.setEnabled(True)
        self.ui.selectFileButton.setEnabled(True)

    def disableButtons(self):
        """Disable the run Fraggler and select file buttons."""
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
        """Handle the click event for items in fileListWidget.

        Args:
            item (QListWidgetItem): The clicked item in the file list.
        """
        self.logger.info(f"Selected FSA file: {item.text()}")
        self.display_report(item.text())

    def dragEnterEvent(self, event):
        """Handle the drag enter event for the main window.

        Args:
            event (QDragEnterEvent): The drag enter event.
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle the drop event for the main window.

        Args:
            event (QDropEvent): The drop event containing the dragged files.
        """
        for url in event.mimeData().urls():
            self.loadFSAFile(url.toLocalFile())

    ############### VALIDATION #############

    def validateEntries(self):
        """Validate the user input entries for running Fraggler.

        Returns:
            bool: True if entries are valid, False otherwise.
        """
        if self.fp is None or self.fp == "":
            self.logger.error("No file imported, please import FSA file")
            return False
        if self.ui.sampleChannelInput.text() == "":
            self.logger.error("Sample channel is empty, please input a valid sample channel. E.g. 'DATA1', 'DATA2'...")
            return False
        if self.ui.outputFolderInput.text() == "":
            self.logger.error("Output folder input is empty, please input a valid output folder name")
            return False
        return True

    ############### RUN FRAGGLER ###############

    def reportProgress(self, message):
        """Report progress messages from the Fraggler worker to the logger and UI.

        Args:
            message (str): The progress message to log and display.
        """
        self.logger.info("Progress: %s", message)


    def runFraggler(self):
        """Run Fraggler with the provided parameters and input files."""
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
        self.worker.finished.connect(self.onFragglerSuccess)

        # Start the thread
        self.thread.start()
        


class Worker(QObject):
    """Worker class to run Fraggler in a separate thread."""
    finished = Signal()
    error = Signal(str)
    log_message = Signal(str) 

    def __init__(self, parent=None):
        """Initialize the Worker with the parent MainWindow.

        Args:
            parent (MainWindow): The main application window.
        """
        super().__init__(parent)
        self.parent = parent
        self.logger = logging.getLogger("FragglerGUI")

    def run(self):
        """Run Fraggler with the provided parameters and input files."""
        try:
            fraggler.runFraggler(
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
    """Custom logging handler to send log messages to the main window."""
    def __init__(self, log_method):
        """Initialize the logging handler with a method for logging messages.

        Args:
            log_method (callable): The method to send log messages to.
        """
        super().__init__()
        self.log_method = log_method

    def emit(self, record):
        """Send log messages to the provided log method.

        Args:
            record (LogRecord): The log record containing message details.
        """
        message = self.format(record)
        levelname = record.levelname
        asctime = record.asctime
        class_name = record.name
        self.log_method(message, levelname, asctime, class_name)


def run():
    """Start the Fraggler GUI application."""
    app = QApplication(sys.argv)
    app.setStyle("fusion")  # Set application style to 'fusion' for consistent look.
    window = MainWindow()  # Create the main application window.
    window.show()
    logger = log_config.get_logger("FragglerGUI")  # Initialize the logger for FragglerGUI.
    try:
        logger.info("Welcome to Fraggler GUI, load a FSA file to get started.")  # Initial log message.
        sys.exit(app.exec_())  # Run the application event loop.
    except Exception as e:
        logger.error(f"Error: {e}")  # Log any errors encountered in the main loop.
        sys.exit(app.exec_())

if __name__ == "__main__":
    run()  # Entry point for the application.
