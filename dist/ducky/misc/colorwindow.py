"""
The file for Color Picker Window
Author: Taha Canturk
Github: Kibnakamoto
Date: Apr 16, 2023
"""

import sys
import os

from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QMessageBox, QColorDialog, \
                            QPushButton, QCheckBox, QGridLayout, QFrame, QInputDialog, QLabel
from PyQt5.QtGui import QColor, QPalette

sys.path.append(os.path.abspath(".."))
from misc.misc import rgbtohex, hextorgb

# Select Custom Color Window
class ColorWindow(QMainWindow):
    """ Default Class Initializer """
    def __init__(self, colors:list, names:tuple, bg_rgb:tuple=(0x00,0x00,0x00), settings=None,
                 screensize=None, parent=None):
        super().__init__()
        self.parent = parent
        pallete = QPalette()
        self.screensize = screensize
        if self.screensize != None:
            self.setGeometry(self.screensize.left()//2, self.screensize.top()//2, self.screensize.width()//2,
                             self.screensize.height()//2)
        pallete.setColor(QPalette.Window, QColor(bg_rgb[0], bg_rgb[1], bg_rgb[2]))
        self.setPalette(pallete)
        self.setWindowTitle("Choose Custom Colors") 

        # convert colors to hex if they aren't
        self.colors = colors
        if not isinstance(colors[0], str):
            self.colors = self.hex_str()
        self.colors = list(self.colors)
        self.names = names
        self.bg_rgb = bg_rgb
        self.rows = 2
        self.columns = 7
        self.settings = settings
        self.closed_event = False
        self.saved = True
        self.theme_text = QLabel(f"{self.settings.theme}", self)

    # custom color picker
    def color_set(self) -> None:
        if (self.bg_rgb[0]+self.bg_rgb[1]+self.bg_rgb[2])//3 <= 127:
            self.setStyleSheet("color: #ffffff")
            self.borderofbox = "white"
        else:
            self.setStyleSheet("color: #000000")
            self.borderofbox = "black"
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

        # save button
        self.save = QPushButton("Save Theme", self)
        self.save.resize(self.save.sizeHint())
        self.save.move(self.screensize.width()//3-self.save.width()-10, 10)
        self.save.setToolTip("Save the Custom Theme")
        self.save.clicked.connect(self.saver)

        # color picker button
        self.pick_color = QPushButton("RGB Color Picker", self)
        self.pick_color.resize(self.pick_color.sizeHint())
        self.pick_color.move(self.screensize.width()//3-10, 10)
        self.setMinimumSize(self.pick_color.width()*10, self.pick_color.height()*10)
        self.pick_color.setToolTip("set colors of selected checkboxes")
        self.pick_color.clicked.connect(self.selector)

        # Input theme name
        self.theme_button = QPushButton("Input Theme Name", self)
        self.theme_button.resize(self.theme_button.sizeHint())
        self.theme_button.move(self.screensize.width()//3+self.pick_color.width()-10, 10)
        self.theme_button.setToolTip("Input the Theme Name Before Saving")
        self.theme_button.clicked.connect(self.input_theme_name)

        if self.borderofbox[0] == 'w': # white border of box means dark background
            self.save.setStyleSheet("""
                QPushButton {
                    background-color: #9f9f9f;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #afafaf;
                    color: #f1f1f1;
                }
            """)
            self.pick_color.setStyleSheet("""
                QPushButton {
                    background-color: #9f9f9f;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #afafaf;
                    color: #f1f1f1;
                }
            """)
            self.theme_button.setStyleSheet("""
                QPushButton {
                    background-color: #9f9f9f;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #afafaf;
                    color: #f1f1f1;
                }
            """)
        else:
            self.save.setStyleSheet("""
                QPushButton {
                    background-color: #efefef;
                    color: #000000;
                }
                QPushButton:hover {
                    background-color: #afafaf;
                    color: #f1f1f1;
                }
            """)
            self.pick_color.setStyleSheet("""
                QPushButton {
                    background-color: #efefef;
                    color: #000000;
                }
                QPushButton:hover {
                    background-color: #afafaf;
                    color: #f1f1f1;
                }
            """)
            self.theme_button.setStyleSheet("""
                QPushButton {
                    background-color: #efefef;
                    color: #000000;
                }
                QPushButton:hover {
                    background-color: #afafaf;
                    color: #f1f1f1;
                }
            """)

        self.theme_text.setText(f"selected theme: {self.settings.theme}")
        self.theme_text.resize(self.theme_text.sizeHint())
        self.theme_text.setGeometry((self.width() - self.theme_text.width()) // 2, (self.height() -
                                                                                    self.theme_text.height()) // 2,
                                    self.theme_text.width(), self.theme_text.height())

    # resize window if moved
    def resizeEvent(self, event):
        # resize theme_text
        size = self.size()
        text_size = self.theme_text.sizeHint()
        self.theme_text.move((size.width() - text_size.width()) // 2, (size.height() - text_size.height()) // 2)
        self.save.move((size.width() - self.save.sizeHint().width()) // 2 - int(self.pick_color.sizeHint().width()/1.03), 10)
        self.pick_color.move((size.width() - self.pick_color.sizeHint().width()) // 2 - self.save.sizeHint().width()//7, 10)
        self.theme_button.move((size.width() - self.theme_button.sizeHint().width()) // 2 + int(self.pick_color.sizeHint().width()/1.03), 10)

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
                    self.box_colors[i].setStyleSheet(f"background-color: {color};border: 1px solid {self.borderofbox};")
                    self.colors[i] = color[1:] # remove #
                    
        else:
            QMessageBox.question(None, 'Color Window', "Color not Chosen Properly or Color chosen doesn't exist", QMessageBox.Ok)

    def saver(self) -> None:
        if not self.saved:
            colors = self.colors
            self.settings.create_theme(colors[-1], colors[0], colors[1], colors[2], colors[3], colors[4], colors[5],
                                       colors[6], colors[7], colors[8], colors[9], colors[10], colors[11], colors[12])
            self.settings.set_colors()
            self.settings.save()
            self.saved = True

            # save the changes to the parent function
            self.parent.settings.set_theme() # update theme
    
            # set background color
            pallete = QPalette()
            tmp = hextorgb(colors[-3])
            pallete.setColor(QPalette.Window, QColor(tmp[0], tmp[1], tmp[2]))
            self.parent.setPalette(pallete) # set background color
            self.parent.codespace.setStyleSheet(f"background-color: #{colors[-4]};") # codespace color
            self.parent.tree.setStyleSheet(f"background-color: #{colors[-2]};color: #{colors[-1]}") # filebar color
    
            # set text color
            code_palette = self.parent.codespace.palette()
            tmp = hextorgb(colors[-5])
            code_palette.setColor(QPalette.Text, QColor(tmp[0], tmp[1], tmp[2]))
            self.parent.codespace.setPalette(code_palette)
            self.parent.rgb = hextorgb(colors[-3])
            self.parent.colors = self.rgb()
            self.parent.set_theme() # sets icons and text color based on how dark the background is
            self.parent.parse_line()
            QMessageBox.question(None, 'Save Theme', "Saved Theme", QMessageBox.Ok)

    def input_theme_name(self) -> None:
        dialog = QInputDialog(self)
        palette = dialog.palette()

        if self.borderofbox[0] == 'w': # white border of box means dark background
            dialog.setStyleSheet("background: black; color: white;")
            dialog.setStyleSheet("QLineEdit { color: white; background-color: black; } QPushButton { background-color: #202020; color: white; }")
            palette.setColor(QPalette.Background, QColor(5, 5, 5))
        else:
            dialog.setStyleSheet("background: 5f5f5f;color: f5f5f5;")
            dialog.setStyleSheet("QLineEdit { color: black; background-color: white; }")
            palette.setColor(QPalette.Background, QColor(250,250,250))
        dialog.setLabelText(f"Enter Theme Name (existing themes: {tuple(self.settings.all_themes)}\n\ncan also be new themes)")
        dialog.setWindowTitle("Theme name Picker")
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.setPalette(palette)
        ok = dialog.exec_()
        self.theme = dialog.textValue()
        if ok and self.theme != "":
            if self.theme in self.settings.all_themes: # if selected theme exists
                __exit = QMessageBox.question(None, 'Theme Selector',
                                              "An existing theme is selected, if the current theme is modified, it won't be automatically saved, would you like to continue?",
                                              QMessageBox.No|QMessageBox.Yes)
                if __exit == QMessageBox.Yes:
                    # set properties of existing theme, if theme was modified, it won't be saved
                    self.settings.set_theme(self.theme)
                    self.colors = [self.settings.comment, self.settings.starting_keywords, self.settings.fkeys,
                                   self.settings.shortcuts, self.settings.arrows, self.settings.windows,
                                   self.settings.chars, self.settings.uncommon, self.settings.numbers, self.settings.text,
                                   self.settings.textbubble, self.settings.bg,  self.settings.bg_sidebar, self.settings.color_sidebar] # 12 colors
                    self.settings.theme = self.theme
                    self.theme_text.setText(f"selected theme: {self.settings.theme}")
                    self.theme_text.resize(self.theme_text.sizeHint())
                    self.saved = True
                    self.close()
                    self.__init__(self.colors, self.names, self.bg_rgb, self.settings, self.screensize, self.parent)
                    self.color_set()
                    self.show()
            else:
                self.settings.theme = self.theme
                self.theme_text.setText(f"selected theme: {self.settings.theme}")
                self.theme_text.resize(self.theme_text.sizeHint())


    def closeEvent(self, event) -> None:
        if not self.saved:
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
        else:
            self.closed_event = True
            event.accept()
