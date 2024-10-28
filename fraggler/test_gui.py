import sys
import logging
import numpy as np
from PySide6 import QtWidgets, QtCore
from fraggler import fraggler_gui_elements as Ui_MainWindow, log_config, ladders, fraggler
from queue import Queue

# Queue to store log messages for periodic GUI updates
log_queue = Queue()

# Long function that simulates fraggler running process and logging
def longFunction(logger):
    fraggler.runFraggler("peak", "/Users/thaddaeussandidge/Documents/FA24/HON4098/data/I101B18G04PR2_B01.fsa", "test10", "LIZ_500", sample_channel="DATA1")

class Worker(QtCore.QThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        # create logger for this class
        self.logger = logging.getLogger("Worker")
        self.logHandler = ThreadLogger()
        self.logHandler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(self.logHandler)
        self.logger.setLevel(logging.DEBUG)

    def run(self):
        longFunction(self.logger)

class MyLog(QtCore.QObject):
    signal = QtCore.Signal(str)

    def __init__(self):
        super().__init__()

class ThreadLogger(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log = MyLog()

    def emit(self, record):
        msg = self.format(record)
        log_queue.put(msg)  # Add log message to queue

class MyWidget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Text box for log display
        self.logTextBox = QtWidgets.QPlainTextEdit(self)
        self.logTextBox.setReadOnly(True)

        self.resize(400, 500)

        # Start button
        self.startButton = QtWidgets.QPushButton(self)
        self.startButton.setText('Start')
        self.startButton.clicked.connect(self.start)

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.logTextBox)
        layout.addWidget(self.startButton)
        self.setLayout(layout)

        # Timer to periodically check for logs in queue
        self.logTimer = QtCore.QTimer(self)
        self.logTimer.timeout.connect(self.check_log_queue)
        self.logTimer.start(200)  # Check every 200 ms

    def start(self):
        self.thread = Worker()
        self.thread.finished.connect(self.threadFinished)
        self.thread.start()

        # Disable start button while thread runs
        self.startButton.setEnabled(False)

    def threadFinished(self):
        self.startButton.setEnabled(True)

    @QtCore.Slot(str)
    def write_log(self, log_text):
        self.logTextBox.appendPlainText(log_text)
        self.logTextBox.centerCursor()  # Scroll to bottom

    def check_log_queue(self):
        while not log_queue.empty():
            log_text = log_queue.get()
            self.write_log(log_text)

def run():
    app = QtWidgets.QApplication(sys.argv)
    w = MyWidget()
    w.show()
    logger = log_config.get_logger("FragglerGUI")
    try:
        logger.info("Welcome to Fraggler GUI, load a FSA file to get started.")
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(app.exec_())
