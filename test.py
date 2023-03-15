# GUI and compiler of duckyscript on a raspberry pi pico (w)

import sys
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QToolBar, QAction, QStatusBar
from PyQt5.QtGui import QIcon


target_os = "" # windows or mac
keyboard_lang = "" # this value will be from ducky.py

# Subclass QMainWindow to customize your application's main window
class IDE(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DuckScript IDE & Compiler")
        label = QLabel("Hello!")
        label.setAlignment(Qt.AlignCenter)

        self.setCentralWidget(label)

        toolbar = QToolBar("Editor toolbar")
        toolbar.setIconSize(QSize(16,16))
        self.addToolBar(toolbar)

        button_action = QAction(QIcon("pictures/compile.png"), "compile", self)
        button_action.setStatusTip("generate binary of program")
        button_action.triggered.connect(self.FileToolbarButton)
        button_action.setCheckable(True)
        toolbar.addAction(button_action)

        self.setStatusBar(QStatusBar(self))

    def FileToolbarButton(self):
        pass




app = QApplication(sys.argv)

window = IDE()
window.show()

app.exec()
