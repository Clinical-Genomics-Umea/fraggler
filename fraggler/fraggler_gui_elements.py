# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindowkVvAYj.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
    QLabel, QLayout, QLineEdit, QListWidget,
    QListWidgetItem, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1187, 832)
        font = QFont()
        font.setPointSize(15)
        MainWindow.setFont(font)
        MainWindow.setAcceptDrops(True)
        MainWindow.setAutoFillBackground(False)
        self.action_loadFSAFile = QAction(MainWindow)
        self.action_loadFSAFile.setObjectName(u"action_loadFSAFile")
        self.action_loadFSAFile.setCheckable(False)
        self.action_about = QAction(MainWindow)
        self.action_about.setObjectName(u"action_about")
        self.actionToggle_Dark_Light = QAction(MainWindow)
        self.actionToggle_Dark_Light.setObjectName(u"actionToggle_Dark_Light")
        self.actionLoad_FSA_Directory = QAction(MainWindow)
        self.actionLoad_FSA_Directory.setObjectName(u"actionLoad_FSA_Directory")
        self.actionZoom_Out = QAction(MainWindow)
        self.actionZoom_Out.setObjectName(u"actionZoom_Out")
        self.actionZoom_In = QAction(MainWindow)
        self.actionZoom_In.setObjectName(u"actionZoom_In")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setAcceptDrops(False)
        self.centralwidget.setAutoFillBackground(False)
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.frame_1 = QFrame(self.centralwidget)
        self.frame_1.setObjectName(u"frame_1")
        font1 = QFont()
        font1.setPointSize(12)
        self.frame_1.setFont(font1)
        self.frame_1.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_1.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frame_1)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_description = QLabel(self.frame_1)
        self.label_description.setObjectName(u"label_description")
        font2 = QFont()
        font2.setPointSize(12)
        font2.setBold(True)
        font2.setUnderline(False)
        self.label_description.setFont(font2)

        self.horizontalLayout_4.addWidget(self.label_description)

        self.label_icon = QLabel(self.frame_1)
        self.label_icon.setObjectName(u"label_icon")
        self.label_icon.setMaximumSize(QSize(50, 50))
        self.label_icon.setFont(font1)
        self.label_icon.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_4.addWidget(self.label_icon)


        self.verticalLayout.addLayout(self.horizontalLayout_4)


        self.verticalLayout_2.addWidget(self.frame_1)

        self.frame_3 = QFrame(self.centralwidget)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFont(font1)
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.frame_3)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, -1, -1)
        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, -1, -1, -1)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(-1, 0, 0, -1)
        self.selectFileButton = QPushButton(self.frame_3)
        self.selectFileButton.setObjectName(u"selectFileButton")
        font3 = QFont()
        font3.setPointSize(10)
        self.selectFileButton.setFont(font3)
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.WindowNew))
        self.selectFileButton.setIcon(icon)

        self.horizontalLayout_3.addWidget(self.selectFileButton)

        self.selectDirectoryButton = QPushButton(self.frame_3)
        self.selectDirectoryButton.setObjectName(u"selectDirectoryButton")
        self.selectDirectoryButton.setFont(font3)
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentOpen))
        self.selectDirectoryButton.setIcon(icon1)

        self.horizontalLayout_3.addWidget(self.selectDirectoryButton)


        self.verticalLayout_7.addLayout(self.horizontalLayout_3)

        self.fileListWidget = QListWidget(self.frame_3)
        self.fileListWidget.setObjectName(u"fileListWidget")

        self.verticalLayout_7.addWidget(self.fileListWidget)


        self.horizontalLayout.addLayout(self.verticalLayout_7)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, -1, -1)
        self.webEngineView = QWebEngineView(self.frame_3)
        self.webEngineView.setObjectName(u"webEngineView")
        self.webEngineView.setMinimumSize(QSize(0, 400))
        self.webEngineView.setUrl(QUrl(u"about:blank"))

        self.verticalLayout_3.addWidget(self.webEngineView)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, -1)
        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.verticalLayout_8.setContentsMargins(0, -1, -1, -1)
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, -1, -1, -1)
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, -1, -1, -1)
        self.typeLabel = QLabel(self.frame_3)
        self.typeLabel.setObjectName(u"typeLabel")
        self.typeLabel.setFont(font3)

        self.verticalLayout_6.addWidget(self.typeLabel)

        self.typeComboBox = QComboBox(self.frame_3)
        self.typeComboBox.setObjectName(u"typeComboBox")
        self.typeComboBox.setFont(font3)

        self.verticalLayout_6.addWidget(self.typeComboBox)

        self.ladderLabel = QLabel(self.frame_3)
        self.ladderLabel.setObjectName(u"ladderLabel")
        self.ladderLabel.setFont(font3)

        self.verticalLayout_6.addWidget(self.ladderLabel)

        self.ladderComboBox = QComboBox(self.frame_3)
        self.ladderComboBox.setObjectName(u"ladderComboBox")
        self.ladderComboBox.setFont(font3)

        self.verticalLayout_6.addWidget(self.ladderComboBox)

        self.peakAreaModelLabel = QLabel(self.frame_3)
        self.peakAreaModelLabel.setObjectName(u"peakAreaModelLabel")
        self.peakAreaModelLabel.setFont(font3)

        self.verticalLayout_6.addWidget(self.peakAreaModelLabel)

        self.peakModelComboBox = QComboBox(self.frame_3)
        self.peakModelComboBox.setObjectName(u"peakModelComboBox")
        self.peakModelComboBox.setFont(font3)

        self.verticalLayout_6.addWidget(self.peakModelComboBox)

        self.outputLabel = QLabel(self.frame_3)
        self.outputLabel.setObjectName(u"outputLabel")
        self.outputLabel.setFont(font3)

        self.verticalLayout_6.addWidget(self.outputLabel)

        self.outputFolderInput = QLineEdit(self.frame_3)
        self.outputFolderInput.setObjectName(u"outputFolderInput")
        self.outputFolderInput.setFont(font3)

        self.verticalLayout_6.addWidget(self.outputFolderInput)


        self.horizontalLayout_6.addLayout(self.verticalLayout_6)

        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, -1, -1, -1)
        self.sampleChannelLabel = QLabel(self.frame_3)
        self.sampleChannelLabel.setObjectName(u"sampleChannelLabel")
        self.sampleChannelLabel.setFont(font3)

        self.verticalLayout_9.addWidget(self.sampleChannelLabel)

        self.sampleChannelInput = QLineEdit(self.frame_3)
        self.sampleChannelInput.setObjectName(u"sampleChannelInput")
        self.sampleChannelInput.setFont(font3)

        self.verticalLayout_9.addWidget(self.sampleChannelInput)

        self.peakStartLabel = QLabel(self.frame_3)
        self.peakStartLabel.setObjectName(u"peakStartLabel")
        self.peakStartLabel.setFont(font3)

        self.verticalLayout_9.addWidget(self.peakStartLabel)

        self.peakStartInput = QLineEdit(self.frame_3)
        self.peakStartInput.setObjectName(u"peakStartInput")
        self.peakStartInput.setFont(font3)

        self.verticalLayout_9.addWidget(self.peakStartInput)

        self.minRatioLabel = QLabel(self.frame_3)
        self.minRatioLabel.setObjectName(u"minRatioLabel")
        self.minRatioLabel.setFont(font3)

        self.verticalLayout_9.addWidget(self.minRatioLabel)

        self.minPeakRatioInput = QLineEdit(self.frame_3)
        self.minPeakRatioInput.setObjectName(u"minPeakRatioInput")
        self.minPeakRatioInput.setFont(font3)

        self.verticalLayout_9.addWidget(self.minPeakRatioInput)

        self.customPeaksLabel = QLabel(self.frame_3)
        self.customPeaksLabel.setObjectName(u"customPeaksLabel")
        self.customPeaksLabel.setFont(font3)

        self.verticalLayout_9.addWidget(self.customPeaksLabel)

        self.customPeaksInput = QLineEdit(self.frame_3)
        self.customPeaksInput.setObjectName(u"customPeaksInput")
        self.customPeaksInput.setFont(font3)

        self.verticalLayout_9.addWidget(self.customPeaksInput)


        self.horizontalLayout_6.addLayout(self.verticalLayout_9)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, -1, -1, -1)
        self.minDistanceBetweenPeaksLabel = QLabel(self.frame_3)
        self.minDistanceBetweenPeaksLabel.setObjectName(u"minDistanceBetweenPeaksLabel")
        self.minDistanceBetweenPeaksLabel.setFont(font3)

        self.verticalLayout_4.addWidget(self.minDistanceBetweenPeaksLabel)

        self.minDistBetweenPeaksInput = QLineEdit(self.frame_3)
        self.minDistBetweenPeaksInput.setObjectName(u"minDistBetweenPeaksInput")
        self.minDistBetweenPeaksInput.setFont(font3)

        self.verticalLayout_4.addWidget(self.minDistBetweenPeaksInput)

        self.minDistSizeStandardLabel = QLabel(self.frame_3)
        self.minDistSizeStandardLabel.setObjectName(u"minDistSizeStandardLabel")
        self.minDistSizeStandardLabel.setFont(font3)

        self.verticalLayout_4.addWidget(self.minDistSizeStandardLabel)

        self.minHeightPeakInput = QLineEdit(self.frame_3)
        self.minHeightPeakInput.setObjectName(u"minHeightPeakInput")
        self.minHeightPeakInput.setFont(font3)

        self.verticalLayout_4.addWidget(self.minHeightPeakInput)

        self.minPeakHeightLabel = QLabel(self.frame_3)
        self.minPeakHeightLabel.setObjectName(u"minPeakHeightLabel")
        self.minPeakHeightLabel.setFont(font3)

        self.verticalLayout_4.addWidget(self.minPeakHeightLabel)

        self.minPeakHeightInput = QLineEdit(self.frame_3)
        self.minPeakHeightInput.setObjectName(u"minPeakHeightInput")
        self.minPeakHeightInput.setFont(font3)

        self.verticalLayout_4.addWidget(self.minPeakHeightInput)

        self.distBetweenAssaysLabel = QLabel(self.frame_3)
        self.distBetweenAssaysLabel.setObjectName(u"distBetweenAssaysLabel")
        self.distBetweenAssaysLabel.setFont(font3)

        self.verticalLayout_4.addWidget(self.distBetweenAssaysLabel)

        self.minDistAssaysInput = QLineEdit(self.frame_3)
        self.minDistAssaysInput.setObjectName(u"minDistAssaysInput")
        self.minDistAssaysInput.setFont(font3)

        self.verticalLayout_4.addWidget(self.minDistAssaysInput)


        self.horizontalLayout_6.addLayout(self.verticalLayout_4)


        self.verticalLayout_8.addLayout(self.horizontalLayout_6)

        self.runFragglerButton = QPushButton(self.frame_3)
        self.runFragglerButton.setObjectName(u"runFragglerButton")
        self.runFragglerButton.setFont(font3)

        self.verticalLayout_8.addWidget(self.runFragglerButton)


        self.horizontalLayout_2.addLayout(self.verticalLayout_8)

        self.listWidget = QListWidget(self.frame_3)
        self.listWidget.setObjectName(u"listWidget")
        self.listWidget.setMaximumSize(QSize(16777215, 16777215))
        font4 = QFont()
        font4.setPointSize(8)
        self.listWidget.setFont(font4)

        self.horizontalLayout_2.addWidget(self.listWidget)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.verticalLayout_3.setStretch(0, 6)
        self.verticalLayout_3.setStretch(1, 3)

        self.horizontalLayout.addLayout(self.verticalLayout_3)

        self.horizontalLayout.setStretch(1, 8)

        self.verticalLayout_5.addLayout(self.horizontalLayout)


        self.verticalLayout_2.addWidget(self.frame_3)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1187, 24))
        font5 = QFont()
        font5.setPointSize(9)
        self.menubar.setFont(font5)
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        self.statusbar.setFont(font5)
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.action_loadFSAFile)
        self.menuFile.addAction(self.actionLoad_FSA_Directory)
        self.menuHelp.addAction(self.actionToggle_Dark_Light)
        self.menuHelp.addAction(self.action_about)
        self.menuHelp.addAction(self.actionZoom_Out)
        self.menuHelp.addAction(self.actionZoom_In)
        self.menuHelp.addSeparator()

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Fraggler GUI", None))
        self.action_loadFSAFile.setText(QCoreApplication.translate("MainWindow", u"Load FSA File", None))
#if QT_CONFIG(shortcut)
        self.action_loadFSAFile.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.action_about.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.actionToggle_Dark_Light.setText(QCoreApplication.translate("MainWindow", u"Toggle Dark/Light Mode", None))
        self.actionLoad_FSA_Directory.setText(QCoreApplication.translate("MainWindow", u"Load FSA Directory", None))
#if QT_CONFIG(shortcut)
        self.actionLoad_FSA_Directory.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+D", None))
#endif // QT_CONFIG(shortcut)
        self.actionZoom_Out.setText(QCoreApplication.translate("MainWindow", u"Zoom Out", None))
#if QT_CONFIG(tooltip)
        self.actionZoom_Out.setToolTip(QCoreApplication.translate("MainWindow", u"Zoom Out on Fraggler Report", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.actionZoom_Out.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+-", None))
#endif // QT_CONFIG(shortcut)
        self.actionZoom_In.setText(QCoreApplication.translate("MainWindow", u"Zoom In", None))
#if QT_CONFIG(tooltip)
        self.actionZoom_In.setToolTip(QCoreApplication.translate("MainWindow", u"Zoom In on Fraggler Report", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.actionZoom_In.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+=", None))
#endif // QT_CONFIG(shortcut)
        self.label_description.setText(QCoreApplication.translate("MainWindow", u"Fraggler GUI", None))
        self.label_icon.setText(QCoreApplication.translate("MainWindow", u"[ICON]", None))
#if QT_CONFIG(tooltip)
        self.selectFileButton.setToolTip(QCoreApplication.translate("MainWindow", u"Select a single FSA file for processing", None))
#endif // QT_CONFIG(tooltip)
        self.selectFileButton.setText(QCoreApplication.translate("MainWindow", u"Select File", None))
#if QT_CONFIG(tooltip)
        self.selectDirectoryButton.setToolTip(QCoreApplication.translate("MainWindow", u"Select a directory that contains FSA files for bulk processing", None))
#endif // QT_CONFIG(tooltip)
        self.selectDirectoryButton.setText(QCoreApplication.translate("MainWindow", u"Select Directory", None))
        self.typeLabel.setText(QCoreApplication.translate("MainWindow", u"Type", None))
#if QT_CONFIG(tooltip)
        self.typeComboBox.setToolTip(QCoreApplication.translate("MainWindow", u"Fraggler area or fraggler peak.", None))
#endif // QT_CONFIG(tooltip)
        self.typeComboBox.setCurrentText("")
        self.ladderLabel.setText(QCoreApplication.translate("MainWindow", u"Ladder", None))
#if QT_CONFIG(tooltip)
        self.ladderComboBox.setToolTip(QCoreApplication.translate("MainWindow", u"Which ladder to use.", None))
#endif // QT_CONFIG(tooltip)
        self.peakAreaModelLabel.setText(QCoreApplication.translate("MainWindow", u"Peak Finding Model", None))
#if QT_CONFIG(tooltip)
        self.peakModelComboBox.setToolTip(QCoreApplication.translate("MainWindow", u"Which peak finding model to use", None))
#endif // QT_CONFIG(tooltip)
        self.outputLabel.setText(QCoreApplication.translate("MainWindow", u"Output Folder Name", None))
#if QT_CONFIG(tooltip)
        self.outputFolderInput.setToolTip(QCoreApplication.translate("MainWindow", u"Output folder name (must be unique)", None))
#endif // QT_CONFIG(tooltip)
        self.sampleChannelLabel.setText(QCoreApplication.translate("MainWindow", u"Sample Channel", None))
#if QT_CONFIG(tooltip)
        self.sampleChannelInput.setToolTip(QCoreApplication.translate("MainWindow", u"Which sample channel to use. E.g. 'DATA1', 'DATA2'...", None))
#endif // QT_CONFIG(tooltip)
        self.sampleChannelInput.setInputMask("")
        self.sampleChannelInput.setText(QCoreApplication.translate("MainWindow", u"DATA1", None))
        self.peakStartLabel.setText(QCoreApplication.translate("MainWindow", u"Peak Start", None))
#if QT_CONFIG(tooltip)
        self.peakStartInput.setToolTip(QCoreApplication.translate("MainWindow", u"Where to start searching for peaks in basepairs", None))
#endif // QT_CONFIG(tooltip)
        self.peakStartInput.setText(QCoreApplication.translate("MainWindow", u"115", None))
        self.minRatioLabel.setText(QCoreApplication.translate("MainWindow", u"Min. Ratio to Allow Peak", None))
#if QT_CONFIG(tooltip)
        self.minPeakRatioInput.setToolTip(QCoreApplication.translate("MainWindow", u"Minimum ratio of the lowest peak compared to the highest peak in the assay", None))
#endif // QT_CONFIG(tooltip)
        self.minPeakRatioInput.setText(QCoreApplication.translate("MainWindow", u"0.15", None))
        self.customPeaksLabel.setText(QCoreApplication.translate("MainWindow", u"Custom Peaks (Optional)", None))
#if QT_CONFIG(tooltip)
        self.customPeaksInput.setToolTip(QCoreApplication.translate("MainWindow", u"CSV Filename with custom peaks to find", None))
#endif // QT_CONFIG(tooltip)
        self.minDistanceBetweenPeaksLabel.setText(QCoreApplication.translate("MainWindow", u"Min. Distance Between Peaks", None))
#if QT_CONFIG(tooltip)
        self.minDistBetweenPeaksInput.setToolTip(QCoreApplication.translate("MainWindow", u"Minimum distance between size standard peaks", None))
#endif // QT_CONFIG(tooltip)
        self.minDistBetweenPeaksInput.setText(QCoreApplication.translate("MainWindow", u"30", None))
        self.minDistSizeStandardLabel.setText(QCoreApplication.translate("MainWindow", u"Min. Height Size Standard Peaks", None))
#if QT_CONFIG(tooltip)
        self.minHeightPeakInput.setToolTip(QCoreApplication.translate("MainWindow", u"Minimum height of peaks in sample data", None))
#endif // QT_CONFIG(tooltip)
        self.minHeightPeakInput.setText(QCoreApplication.translate("MainWindow", u"100", None))
        self.minPeakHeightLabel.setText(QCoreApplication.translate("MainWindow", u"Min. Height Sample Peaks", None))
#if QT_CONFIG(tooltip)
        self.minPeakHeightInput.setToolTip(QCoreApplication.translate("MainWindow", u"Minimum height of peaks in sample data", None))
#endif // QT_CONFIG(tooltip)
        self.minPeakHeightInput.setText(QCoreApplication.translate("MainWindow", u"300", None))
        self.distBetweenAssaysLabel.setText(QCoreApplication.translate("MainWindow", u"Min. Distance Between Assays", None))
#if QT_CONFIG(tooltip)
        self.minDistAssaysInput.setToolTip(QCoreApplication.translate("MainWindow", u"Minimum distance between assays in a multiple assay experiment", None))
#endif // QT_CONFIG(tooltip)
        self.minDistAssaysInput.setText(QCoreApplication.translate("MainWindow", u"15", None))
        self.runFragglerButton.setText(QCoreApplication.translate("MainWindow", u"Run Fraggler", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi

