# GUI and compiler of duckyscript on a raspberry pi pico (w)

import sys
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QToolBar, QAction, QStatusBar, QMenu, QLineEdit
from PyQt5.QtGui import QIcon

import language

target_os = "" # windows or mac
keyboard_lang = "uk" # target keyboard language, default is uk

# Initialize Duckyscript keywords to color code the ones written to the textbox
DUCKYSCRIPT_COMMENT = "REM"
DUCKYSCRIPT_STARTING_KEYWORDS = ("DELAY", "STRING", "PRINT", "IMPORT", "DEFAULT_DELAY", "DEFAULTDELAY", "LED")
DUCKYSCRIPT_F_KEYS = ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12")
DUCKYSCRIPT_SHORTCUT_KEYS = ("ALT", "CTRL", "CONTROL", "SHIFT", "SPACE", "ENTER", "BACKSPACE", "TAB",
                             "CAPSLOCK", "ESC", "ESCAPE")
DUCKYSCRIPT_ARROWS = ("UP" "UPARROW", "DOWN", "DOWNARROW", "LEFT", "LEFTARROW", "RIGHT", "RIGHTARROW")
DUCKYSCRIPT_WINDOWS = ("WINDOWS", "GUI")
DUCKYSCRIPT_CHARS = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q",
                     "R", "S", "T", "U", "V", "W", "X", "Y", "Z")
DUCKYSCRIPT_UNCOMMON = ("APP", "MENU", "BREAK", "PAUSE", "DELETE", "END", "HOME", "INSERT", "NUMLOCK",
                        "PAGEUP", "PAGEDOWN", "PRINTSCREEN", "SCROLLLOCK")
ITEXT_COLORS = () # 12 colors

# COLORS for (COMMENT, starting_keywords, fkeys, shortcut_keys, arrows, windows, chars, uncommon, numbers, text)

######## TODO: make a setup function that downloads add_to_pico/* into the microcontroller
######## TODO: add settings submenu for changing the colors of input text
######## TODO: make a line parser

# Subclass QMainWindow to customize your application's main window
class IDE(QMainWindow):
    def __init__(self):
        super().__init__()

        # icons
        self.black_bk_pngs = {
                "add_file": [
                    "pictures/black_bk/add_file.png",
                    "add another duckyscript file",
                    self.add_file
                ],
                "compile": [
                    "pictures/black_bk/compile.png",
                    "generate binary of program",
                    self.compile_duckyscript
                ],
                "download": [
                    "pictures/black_bk/download.png",
                    "download the file on your computer",
                    self.download_file
                ],
                "save": [
                    "pictures/black_bk/save.png",
                    "save the file",
                    self.save
                ],
                "upload": [
                    "pictures/black_bk/upload.png",
                    "upload file onto the hacking USB",
                    self.upload
                ]
        }
        
        self.white_bk_pngs = {
                "add_file": [
                    "pictures/white_bk/add_file.png",
                    "add another duckyscript file",
                    self.add_file
                    ],
                "compile": [
                    "pictures/white_bk/compile.png",
                    "generate binary of program",
                    self.compile_duckyscript
                ],
                "download": [
                    "pictures/white_bk/download.png",
                    "download the file on your computer",
                    self.download_file
                ],
                "save": [
                    "pictures/white_bk/save.png",
                    "save the file",
                    self.save
                ],
                "upload": [
                    "pictures/white_bk/upload.png",
                    "upload file onto the hacking USB",
                    self.upload
                ]
        }

        view_black = [ # submenu
            "pictures/black_bk/view.png",
            "view",
        ]
        
        view_white = [ # submenu
            "pictures/white_bk/view.png",
            "view",
        ]

        self.pngs = self.black_bk_pngs # default icons
        self.view_theme = view_black
        self.theme = "white" # default theme
        self.setWindowTitle("DuckScript IDE & Compiler")
        main_menu = self.menuBar()

        toolbar = QToolBar("Editor toolbar")
        toolbar.setIconSize(QSize(22,22))
        self.addToolBar(toolbar)

        for action, lst in self.pngs.items():
            button_action = QAction(QIcon(lst[0]), action, self)
            button_action.setStatusTip(lst[1])
            button_action.triggered.connect(lst[2]) # lst[2] is the method added in the previous step
            button_action.setCheckable(True)

            # add buttons to toolbar
            toolbar.addAction(button_action)

        # add the view submenu
        view_menu = main_menu.addMenu(QIcon(self.view_theme[0]), 'View')
        copy_act = QAction('&Copy', self)
        paste_act = QAction('&Paste', self)
        cut_act = QAction('&Cut', self)
        copy_act.setShortcut("Ctrl+C")
        paste_act.setShortcut("Ctrl+V")
        cut_act.setShortcut("Ctrl+X")
        view_menu.addAction(copy_act)
        view_menu.addAction(paste_act)
        view_menu.addAction(cut_act)


        # add textspace to write code
        codespace = QLineEdit()
        codespace.setText("Write Duckyscript Here...")

        self.setStatusBar(QStatusBar(self))

    def compile_duckyscript(self):
        pass

    def change_theme(self):
        if self.theme == "black":
            self.pngs = self.black_bk_pngs
            self.view_theme = view_black
        else:
            self.pngs = self.white_bk_pngs
            self.view_theme = view_white

    # add another duckyscript file
    # https://github.com/dbisu/pico-ducky#multiple-payloads
    def add_file(self):
        pass

    # locally download payload(#).dd
    def download_file(self):
        pass

    # save the currently editing file
    def save(self):
        pass

    # upload payload(#).dd onto the microcontroller
    def upload(self):
        pass

    # view submenu. CTRL Z, CTRL C, CTRL V, etc.
    def view(self):
        pass

app = QApplication(sys.argv)

window = IDE()
window.show()

app.exec()
