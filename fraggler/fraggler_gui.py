import os
import platform
import subprocess
import sys
import tempfile

from PySide6.QtCore import QThread, Signal, QObject
from bokeh.embed import components

import PySide6
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtUiTools import QUiLoader
import logging
import fraggler_gui_elements as Ui_MainWindow
import fraggler
import log_config
import ladders
import panel as pn
from PySide6.QtWebEngineCore import QWebEngineSettings  # Add this line


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.subprocess = None  # Initialize subprocess attribute
        self.fp = None

        # Check if the system theme is dark or light
        self.system_theme = self.get_system_theme()
        # Apply the system theme
        if self.system_theme == "dark":
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

        self.setupLogging()
        self.initMenuActions()
        self.initButtonActions()
        self.initComboBoxActions()

        self.initIcons()
        self.setupStatusBar()
        self.update_status_indicator()
        # Setup QTimer (not deemed necessary for slowing down application)
        self.statusUpdateTimer = QTimer(self)
        self.statusUpdateTimer.timeout.connect(self.update_status_indicator)
        self.statusUpdateTimer.start(
            10000
        )  # Timer interval set to 10000 milliseconds (10 second)

        # Setup the worker and thread
        self.worker = Worker(parent=self)
        self.worker = Worker(parent=self)
        self.worker.report_generated.connect(self.display_report)
        self.worker.error.connect(self.handle_error)
        self.worker.finished.connect(self.enableButtons)
        self.ui.webEngineView.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        self.ui.webEngineView.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.showFullScreen()
    
    def display_report(self, report_path):
        """Display the generated report in QWebEngineView."""
        self.logger.info(f"Generated report path: {report_path}")
        self.ui.webEngineView.load(QUrl.fromLocalFile(report_path))
        self.ui.webEngineView.show()

    def handle_error(self, error_message):
        """Handle error if any occurs."""
        QMessageBox.critical(self, "Error", error_message)

    ################## INITIALIZATION ##################
    def load_ui(self):
        loader = QUiLoader()
        loader.registerCustomWidget(QMainWindow)
        path = os.path.join(os.path.dirname(__file__), "MainWindow.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        ui = loader.load(ui_file, self)
        self.setCentralWidget(ui)  # Set the loaded UI as the central widget
        ui_file.close()
        return ui

    def initMenuActions(self):
        self.ui.action_loadFSAFile.triggered.connect(self.loadFSAFile)
        self.ui.actionToggle_Dark_Light.triggered.connect(self.toggle_theme)
        self.ui.action_about.triggered.connect(self.about)

    def initButtonActions(self):
        self.ui.selectFileButton.clicked.connect(self.loadFSAFile)
        self.ui.runFragglerButton.clicked.connect(self.runFraggler)


    def initComboBoxActions(self):
        # type is area or peak
        # Populate the typeComboBox with TYPES
        self.ui.typeComboBox.addItems(fraggler.TYPES)
        # Populate the peakModelComboBox with PEAK_AREA_MODELS
        self.ui.peakModelComboBox.addItems(fraggler.PEAK_AREA_MODELS)
        # Assuming LADDERS is a dictionary and you want to populate ladderComboBox with its keys
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

        # Set the scaled pixmap to the label
        self.ui.label_icon.setPixmap(scaled_pixmap)

    def setupLogging(self):
        self.logger = log_config.get_logger("FragglerGUI")
        # Create a logging handler that will log to the list widget
        self.log_handler = MainWindowLoggingHandler(self.log)
        # Add the handler to the root logger
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

    def closeEvent(self, event):
        # This method is called when the window is closed
        if self.subprocess:
            self.subprocess.kill()
            self.subprocess.wait()
        event.accept()

    ############### Enable/Disable ###############
    def enableButtons(self):
        self.ui.runFragglerButton.setEnabled(True)
        self.ui.selectFileButton.setEnabled(True)

    def disableButtons(self):
        self.ui.runFragglerButton.setEnabled(False)
        self.ui.selectFileButton.setEnabled(False)

    ############### LOAD FSA FILE ###############
    def loadFSAFile(self, fp):
        if not fp:
            fp = self.getValidFilePath()

        # Update label_fp with the file path
        self.logger.info("Loading FSA file: %s", fp)

        self.fp = fp
        # just include the filename not the complete path in the display
        self.ui.selectFileButton.setText(f"File loaded: {os.path.basename(fp)}")

    def getValidFilePath(
        self,
        filter="All files (*);;FSA files (*.fsa)",
    ):

        fp, _ = QFileDialog.getOpenFileName(
            parent=self,
            filter=filter,
        )

        return fp

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
    # def runFraggler(self):

        if not self.validateEntries():
            self.logger.info("Invalid entries...")
            return

        class RunFragglerThread(QThread):
            def __init__(self, parent):
                super().__init__()
                self.parent = parent

            def run(self):
                self.parent.disableButtons()

                self.parent.logger.info(
                    "Running fraggler with type=%s, sampleChannel=%s, peakStart=%s, minRatio=%s, peakAreaModel=%s, customPeaks=%s, ladder=%s, minDistanceBetweenPeaks=%s, minDistSizeStandard=%s, minPeakHeight=%s, distBetweenAssays=%s, outputFolder=%s",
                    self.parent.ui.typeComboBox.currentText(),
                    self.parent.ui.sampleChannelInput.text(),
                    self.parent.ui.peakStartInput.text(),
                    self.parent.ui.minPeakRatioInput.text(),
                    self.parent.ui.peakModelComboBox.currentText(),
                    self.parent.ui.customPeaksInput.text(),
                    self.parent.ui.ladderComboBox.currentText(),
                    self.parent.ui.minDistBetweenPeaksInput.text(),
                    self.parent.ui.minHeightPeakInput.text(),
                    self.parent.ui.minPeakHeightInput.text(),
                    self.parent.ui.minDistAssaysInput.text(),
                    self.parent.ui.outputFolderInput.text()
                )

                # Run fraggler
                try:
                    report = fraggler.runFraggler(
                        type=self.parent.ui.typeComboBox.currentText(),
                        fsa=self.parent.fp,
                        output=self.parent.ui.outputFolderInput.text() if self.parent.ui.outputFolderInput.text() else None,
                        ladder=self.parent.ui.ladderComboBox.currentText() if self.parent.ui.ladderComboBox.currentText() else None,
                        sample_channel=self.parent.ui.sampleChannelInput.text() if self.parent.ui.sampleChannelInput.text() else None,
                        min_distance_between_peaks=int(self.parent.ui.minDistBetweenPeaksInput.text()) if self.parent.ui.minDistBetweenPeaksInput.text() else None,
                        min_size_standard_height=int(self.parent.ui.minHeightPeakInput.text()) if self.parent.ui.minHeightPeakInput.text() else None,
                        custom_peaks=self.parent.ui.customPeaksInput.text() if self.parent.ui.customPeaksInput.text() else None,
                        peak_height_sample_data=int(self.parent.ui.minPeakHeightInput.text()) if self.parent.ui.minPeakHeightInput.text() else None,
                        min_ratio_to_allow_peak=float(self.parent.ui.minPeakRatioInput.text()) if self.parent.ui.minPeakRatioInput.text() else None,
                        distance_between_assays=int(self.parent.ui.minDistAssaysInput.text()) if self.parent.ui.minDistAssaysInput.text() else None,
                        search_peaks_start=int(self.parent.ui.peakStartInput.text()) if self.parent.ui.peakStartInput.text() else None,
                        peak_area_model=self.parent.ui.peakModelComboBox.currentText() if self.parent.ui.peakModelComboBox.currentText() else None,
                    )

                except Exception as e:
                    self.parent.logger.error(
                        "Error occurred while running fraggler: %s", str(e)
                    )
                finally:
                    self.parent.enableButtons()
                    # Create and start the thread
        self.thread = RunFragglerThread(self)
        self.thread.start()
    
    
    def runFraggler(self):
        if not self.validateEntries():
            self.logger.info("Invalid entries...")
            return

        # Create a QThread object
        self.thread = QThread()
        # Create a worker object
        self.worker = Worker(self)
        # Move the worker to the thread
        self.worker.moveToThread(self.thread)
        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.error.connect(self.handle_error)
        self.worker.progress.connect(self.report_progress)
        self.worker.finished.connect(self.enableButtons)

        # Connect the report_generated signal to the display_report slot
        self.worker.report_generated.connect(self.display_report)

        # Start the thread
        self.thread.start()

    def handle_error(self, error_message):
        self.logger.error("Error occurred while running fraggler: %s", error_message)

    def report_progress(self, message):
        self.logger.info(message)


    ############### LOGGING ###############
    def log(self, msg, level="none", asctime="none", class_name="none"):
        # Add the message to the status bar and list widget
        self.statusBar().showMessage(msg)

        # Add color to the message
        msg = f"{asctime} \t {class_name} \t {msg}"
        item = QListWidgetItem(msg)
        level = level.lower()
        if level == "error":
            item.setForeground(QBrush(QColor("red")))
        elif level == "warning":
            item.setForeground(QBrush(QColor("orange")))
        elif level == "success":
            item.setForeground(QBrush(QColor("green")))
        elif level == "info":
            pass
        elif level == "debug":
            item.setForeground(QBrush(QColor("black")))
        else:
            # Default text color
            pass

        # if self.debug or level != "info":
        self.ui.listWidget.insertItem(0, item)


class Worker(QObject):
    finished = Signal()
    error = Signal(str)
    progress = Signal(str)
    report_generated = Signal(str)  # Emit the path of the temporary report file

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def run(self):
        self.parent.disableButtons()

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
            self.progress.emit("Fraggler run completed successfully.")
            
            if report:  # If a report is generated
                self.progress.emit("Report generated.")
                # Create a temporary file to save the report
                with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as temp_file:
                    report.save(temp_file.name, title="test")  # Save report to the temp file
                    report_path = temp_file.name  # Get the path of the temp file
                    self.report_generated.emit(report_path)  # Emit the path of the temp file
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
    print(fraggler.ASCII_ART)
    try:
        logger.info("Welcome to Fraggler GUI, load a FSA file to get started.")
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(app.exec_())


if __name__ == "__main__":
    run()
