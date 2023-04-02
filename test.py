import sys
import re
from PyQt5.QtCore import QSize, Qt, QRect, QRegExp, QTextStream, QFile, QDir
from PyQt5.QtWidgets import QMainWindow, QApplication, QToolBar, QAction, QStatusBar, QMenu, QTextEdit,  \
                            QHBoxLayout, QSizePolicy, QWidget, QPlainTextEdit, QMessageBox, QColorDialog, \
                            QPushButton, QDockWidget, QFileDialog, QVBoxLayout, QFileSystemModel, QTreeView, \
                            QCheckBox, QGridLayout, QFrame
from PyQt5.QtGui import QIcon, QColor, QTextFormat, QBrush, QTextCharFormat, QFont, QSyntaxHighlighter, \
                        QPalette, QTextCursor
from pyqt_line_number_widget import LineNumberWidget
import os
import shutil
import json
from ducky import rgbtohex, hextorgb, Settings

import language

# Color of checkbox
class ColorCheckBox(QWidget):
    def __init__(self):
        super().__init__()

        # create a checkbox and a colorbox to show what color it is
        self.color_box = QFrame(self)
        self.color_box.setMinimumSize(10, 10)
        self.check_box = QCheckBox(self)
        layout = QHBoxLayout(self)
        layout.addWidget(self.check_box)
        layout.addWidget(self.color_box)

# Select Custom Color Window
class ColorWindow(QMainWindow):
    def __init__(self, colors:list, names:tuple, bg_rgb:tuple=(0x00,0x00,0x00), settings=None,
                 screensize=None):
        super().__init__()
        pallete = QPalette()
        self.screensize = screensize
        if self.screensize != None:
            self.setGeometry(self.screensize.left()//2, self.screensize.top()//2, self.screensize.width()//2,
                             self.screensize.height()//2)
        pallete.setColor(QPalette.Window, QColor(bg_rgb[0], bg_rgb[1], bg_rgb[2]))
        self.setPalette(pallete)

        # save button
        save = QPushButton("Save Theme", self)
        save.resize(save.sizeHint())
        save.move(self.screensize.width()//4, 10)
        save.clicked.connect(self.saver)

        # color picker button
        pick_color = QPushButton("RGB Color Picker", self)
        pick_color.resize(pick_color.sizeHint())
        pick_color.move(self.screensize.width()//4+save.width(), 10)
        self.setMinimumSize(pick_color.width()*10, pick_color.height()*10)
        pick_color.setToolTip("set colors of selected checkboxes")
        pick_color.clicked.connect(self.selector)

        if (bg_rgb[0]+bg_rgb[1]+bg_rgb[2])//3 <= 127:
            self.setStyleSheet("color: #ffffff")
            save.setStyleSheet("""
                QPushButton {
                    background-color: #9f9f9f;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #afafaf;
                    color: #f1f1f1;
                }
            """)
            pick_color.setStyleSheet("background-color: #9f9f9f; color: #ffffff")
            
            color: white;
            self.borderofbox = "white"
        else:
            self.setStyleSheet("color: #000000")
            save.setStyleSheet("background-color: #efefef; color: #000000")
            pick_color.setStyleSheet("background-color: #efefef; color: #000000")
            self.borderofbox = "black"

        self.setWindowTitle("Choose Custom Colors") 

        # convert colors to hex if they aren't
        self.colors = colors
        if not isinstance(colors[0], str):
            self.colors = self.hex_str()
        self.names = names
        self.rows = 2
        self.columns = 6
        self.settings = settings
        self.closed_event = False
        self.saved = True

    # custom color picker
    def color_set(self) -> None:
        grid_layout = QGridLayout()
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_widget.setLayout(grid_layout)
        self.boxes = []
        self.box_colors = []
        for i in range(self.rows):
            for j in range(self.columns):
                checkbox = QCheckBox(f"Color {self.names[i*self.columns+j]}", self)
                color_box = QFrame(self)
                color_box.setFixedSize(10,10)
                color_box.setStyleSheet(f"background-color: #{self.colors[i*self.columns+j]};border: 1px solid {self.borderofbox};")
                checkbox.setStyleSheet("QCheckBox:checked { color: red; }")
                widget = QWidget(self)
                color_layout = QHBoxLayout(widget)
                color_layout.addWidget(checkbox)
                color_layout.addWidget(color_box)
                grid_layout.addWidget(widget, i, j)
                self.boxes.append(checkbox)
                self.box_colors.append(color_box)
        self.setFixedWidth(self.width())

    # return colors as rgb
    def rgb(self) -> tuple:
        rgbs = tuple([hextorgb(i) for i in self.colors])
        return rgbs

    # return colors as hex string
    def hex_str(self) -> tuple:
        hexs = tuple([rgbtohex(i) for i in self.colors])
        return hexs

    # select and set the color picked
    def selector(self) -> None:
        self.color_picker = QColorDialog.getColor()
        if self.color_picker.isValid():
            for i in range(len(self.boxes)):
                if self.boxes[i].isChecked():
                    self.saved = False
                    color = self.color_picker.name()
                    self.box_colors[i].setStyleSheet(f"background-color: {color};")
                    self.colors[i] = color[1:] # remove #
                    
        else:
            err = QMessageBox.question(None, 'Color Window', "Color chosen doesn't exist", QMessageBox.Ok)

    def saver(self) -> None:
        if not self.saved:
            self.settings.create_theme(colors[-1], colors[0], colors[1], colors[2], colors[3], colors[4], colors[5],
                                       colors[6], colors[7], colors[8], colors[9], colors[10], colors[11], colors[12])
            self.settings.set_colors()
            self.settings.save()
            self.saved = True

    def closeEvent(self, event):
        __exit = QMessageBox.question(None, 'Save Theme', "Do you want to save the theme?\nyou can change the theme anytime", QMessageBox.No|QMessageBox.Yes)
        if __exit == QMessageBox.Yes:
            self.saver()
            self.closed_event = True
            event.accept()
        else:
            msg = QMessageBox.question(None, 'Exit', "Are you sure you want to exit without saving?", QMessageBox.No|QMessageBox.Save|QMessageBox.Yes)
            if msg == QMessageBox.Yes:
                self.closed_event = True
                event.accept()
            elif msg == QMessageBox.Save:
                self.saver()
                self.closed_event = True
                event.accept()
            else:
                event.ignore()

a = QApplication([])
l = ((50, 205, 50), (255, 0, 0), (105, 105, 105), (210, 105, 30), (224, 255, 255), (62, 62, 236),
     (255, 102, 102), (133, 193, 187), (212, 21, 212), (250, 250, 250), (0, 0, 0), (5, 5, 5), (7, 7, 7), (240, 240, 240))

names =  ('comment', 'starting keywords', 'F-keys', "shortcut keys", "arrows", "windows", "chars",
                 "uncommon", "numbers", "text", "textbubble", "background")
screensize = a.primaryScreen().availableGeometry()
s = Settings()
w = ColorWindow(l, names, (0,0,0), s, screensize)
w.color_set()
w.show()
a.exec_()
