import sys
import re
from PyQt5.QtCore import QSize, Qt, QRect, QRegExp, QTextStream, QFile, QDir
from PyQt5.QtWidgets import QMainWindow, QApplication, QToolBar, QAction, QStatusBar, QMenu, QTextEdit,  \
                            QHBoxLayout, QSizePolicy, QWidget, QPlainTextEdit, QMessageBox, QColorDialog, \
                            QPushButton, QDockWidget, QFileDialog, QVBoxLayout, QFileSystemModel, QTreeView, \
                            QCheckBox, QGridLayout
from PyQt5.QtGui import QIcon, QColor, QTextFormat, QBrush, QTextCharFormat, QFont, QSyntaxHighlighter, \
                        QPalette, QTextCursor
from pyqt_line_number_widget import LineNumberWidget
import os
import shutil
import json
from ducky import rgbtohex, hextorgb, Settings

import language

# Select Custom Color Window
class ColorWindow(QMainWindow):
    def __init__(self, colors:list, bg_color:str, names:tuple, bg_rgb:tuple=(0x00,0x00,0x00), settings=None, theme_name="black", bg_color_sidebar="070707", color_sidebar="f0f0f0"):
        super().__init__()
        pallete = QPalette()
        pallete.setColor(QPalette.Window, QColor(bg_rgb[0], bg_rgb[1], bg_rgb[2]))
        self.setPalette(pallete)
        self.setWindowTitle("Choose Custom Colors") 
        self.colors = colors
        self.names = names
        self.rows = 2
        self.columns = 6
        self.settings = settings
        self.closed_event = False
        self.theme_name = theme_name
        self.bg_color = bg_color
        self.bg_color_sidebar = bg_color_sidebar
        self.color_sidebar = color_sidebar

    def color_set(self) -> None:
        grid_layout = QGridLayout()
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_widget.setLayout(grid_layout)
        self.boxes = []
        for i in range(self.rows):
            for j in range(self.columns):
                checkbox = QCheckBox(f"Color {self.names[i*self.columns+j]}", self)
                checkbox.stateChanged.connect(self.selector)
                self.boxes.append(checkbox)
                grid_layout.addWidget(checkbox, i, j)

    def selector(self, state) -> None:
        if state == Qt.Checked: # selected colors
            for i in names:
                


    def closeEvent(self, event):
        __exit = QMessageBox.question(None, 'Save Theme', "Do you want to save the theme?\nyou can change the theme anytime", QMessageBox.No|QMessageBox.Yes)
        if __exit == QMessageBox.Yes:
            colors = [rgbtohex(i) for i in self.colors]
            self.settings.theme = self.theme_name
            self.settings.create_theme(colors[-1], colors[0], colors[1], colors[2], colors[3], colors[4], colors[5],
                                       colors[6], colors[7], colors[8], colors[9], self.bg_color, self.bg_color_sidebar, self.color_sidebar)
            self.settings.set_colors()
            self.settings.save()
            self.closed_event = True
            event.accept()
        else:
            msg = QMessageBox.question(None, 'Exit', "Are you sure you want to exit without saving?", QMessageBox.No|QMessageBox.Save|QMessageBox.Yes)
            if msg == QMessageBox.Yes:
                self.closed_event = True
                event.accept()
            elif msg == QMessageBox.Save:
                colors = [rgbtohex(i) for i in self.colors]
                self.settings.theme = self.theme_name
                self.settings.create_theme(colors[-1], colors[0], colors[1], colors[2], colors[3], colors[4], colors[5],
                                           colors[6], colors[7], colors[8], colors[9], self.bg_color, self.bg_color_sidebar, self.color_sidebar)
                self.settings.set_colors()
                self.settings.save()
                self.closed_event = True
                event.accept()
            else:
                event.ignore()

a = QApplication([])
l = [(50, 205, 50), (255, 0, 0), (105, 105, 105), (210, 105, 30), (224, 255, 255), (62, 62, 236), (255, 102, 102), (133, 193, 187), (212, 21, 212), (250, 250, 250), (5, 5, 5)]
names =  ('comment', 'starting keywords', 'F-keys', "shortcut keys", "arrows", "windows", "chars",
                 "uncommon", "numbers", "text", "textbubble", "background")
s = Settings()
w = ColorWindow(l, "000000", names, (255,255,255), s)
w.color_set()
w.show()
a.exec_()
