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
    def __init__(self, colors:list, bg_color:str, names:tuple, bg_rgb:tuple=(0x00,0x00,0x00), settings=None,
                 theme_name="black", bg_color_sidebar="070707", color_sidebar="f0f0f0"):
        super().__init__()
        pallete = QPalette()
        pallete.setColor(QPalette.Window, QColor(bg_rgb[0], bg_rgb[1], bg_rgb[2]))
        self.setPalette(pallete)
        if (bg_rgb[0]+bg_rgb[1]+bg_rgb[2])//3 <= 127:
            self.setStyleSheet(f"color: #ffffff")
            self.borderofbox = "white"
        else:
            self.setStyleSheet(f"color: #000000")
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
        self.theme_name = theme_name
        self.bg_color = bg_color
        self.bg_color_sidebar = bg_color_sidebar
        self.color_sidebar = color_sidebar
        pick_color = QPushButton("RGB Color Picker", self)
        pick_color.move(self.width(), self.height())
        pick_color.setToolTip("set colors of selected checkboxes")
        pick_color.clicked.connect(self.selector)
        self.saved = True

        # save button
        save = QPushButton("Save Theme", self)
        save.resize(save.sizeHint())
        save.move(self.width(), self.height())
        save.clicked.connect(self.saver)

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
            self.settings.theme = self.theme_name
            self.settings.create_theme(colors[-1], colors[0], colors[1], colors[2], colors[3], colors[4], colors[5],
                                       colors[6], colors[7], colors[8], colors[9], self.bg_color, self.bg_color_sidebar, self.color_sidebar)
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
s = Settings()
w = ColorWindow(l, "000000", names, (0,0,0), s)
w.color_set()
w.show()
a.exec_()
