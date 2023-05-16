"""
GUI and compiler of duckyscript on a raspberry pi pico (w)
@Author: Taha Canturk
@Github: Kibnakamoto
Date: Apr 16, 2023
"""

import sys
import os
import shutil
import json
from pathlib import Path
import send2trash
from copy import deepcopy
from PyQt5.QtCore import QSize, Qt, QRect, QRegExp, QDir
from PyQt5.QtWidgets import QMainWindow, QApplication, QToolBar, QAction, QStatusBar, QTextEdit,  \
                            QHBoxLayout, QSizePolicy, QWidget, QMessageBox, QInputDialog, \
                            QDockWidget, QFileDialog, QFileSystemModel, QTreeView, QComboBox
from PyQt5.QtGui import QIcon, QColor, QTextCharFormat, QFont, QSyntaxHighlighter, \
                        QPalette, QTextCursor
from PyQt5.QtGui import QKeySequence, QPixmap, QPainter
from PyQt5.QtCore import QBuffer, QByteArray
from pyqt_line_number_widget import LineNumberWidget

import language
from misc.colorwindow import ColorWindow
from misc.misc import hextorgb, rgbtohex
from settings import Settings
import setup

SUPPORTED_OSS = ("windows", "mac") # currently

# Initialize Duckyscript keywords to color code the ones written to the textbox
DUCKYSCRIPT_COMMENT = ("REM")
DUCKYSCRIPT_STARTING_KEYWORDS = ("DELAY", "STRING", "PRINT", "DEFAULT_DELAY", "DEFAULTDELAY", "LED", "REPEAT", "IMPORT")
DUCKYSCRIPT_F_KEYS = ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12")
DUCKYSCRIPT_SHORTCUT_KEYS = ("ALT", "CTRL", "CONTROL", "SHIFT", "SPACE", "ENTER", "BACKSPACE", "TAB",
                             "CAPSLOCK", "ESC", "ESCAPE")
DUCKYSCRIPT_ARROWS = ("UP", "UPARROW", "DOWN", "DOWNARROW", "LEFT", "LEFTARROW", "RIGHT", "RIGHTARROW")
DUCKYSCRIPT_WINDOWS = ("WINDOWS", "GUI")
DUCKYSCRIPT_CHARS = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q",
                     "R", "S", "T", "U", "V", "W", "X", "Y", "Z")
DUCKYSCRIPT_UNCOMMON = ("APP", "MENU", "BREAK", "PAUSE", "DELETE", "END", "HOME", "INSERT", "NUMLOCK",
                        "PAGEUP", "PAGEDOWN", "PRINTSCREEN", "SCROLLLOCK")

# catched errors. Not used for raising errors but fullfils the goto statement's purpose in python
class CatchedError(Exception):
    pass

class Setup(QMainWindow):
    """ Default Class Initializer """
    def __init__(self):
        super().__init__()

# COLORS for (COMMENT, starting_keywords, fkeys, shortcut_keys, arrows, windows, chars, uncommon, numbers, text, textbubble, background, sidebar background, sidebar text)
s = Settings()
s.set_theme("white")

ITEXT_COLORS_LIGHT = [s.comment, s.starting_keywords, s.fkeys, s.shortcuts, s.arrows, s.windows,
                      s.chars, s.uncommon, s.numbers, s.text, s.textbubble, s.bg, s.bg_sidebar, s.color_sidebar] # 12 colors
s.set_theme("black")
ITEXT_COLORS_DARK = [s.comment, s.starting_keywords, s.fkeys, s.shortcuts, s.arrows, s.windows,
                      s.chars, s.uncommon, s.numbers, s.text, s.textbubble, s.bg, s.bg_sidebar, s.color_sidebar] # 12 colors

for i in range(len(ITEXT_COLORS_DARK)):
    ITEXT_COLORS_LIGHT[i] = hextorgb(ITEXT_COLORS_LIGHT[i])
    ITEXT_COLORS_DARK[i] = hextorgb(ITEXT_COLORS_DARK[i])
ITEXT_COLORS_LIGHT = tuple(ITEXT_COLORS_LIGHT)
ITEXT_COLORS_DARK = tuple(ITEXT_COLORS_DARK)
del s


# Syntax Highlighter for Duckyscript
class SyntaxHighlighter(QSyntaxHighlighter):
    """ Default Class Initializer """
    def __init__(self, parent, all_keys, colors, color_str, color_num):
        super().__init__(parent)

        self.colors = colors

        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor(color_str))

        self.num_format = QTextCharFormat()
        self.num_format.setForeground(QColor(color_num))

        self.keyword_pattern = all_keys

    def highlightBlock(self, text):
        words = text.split(' ')
        fi = 0
        for keys in self.keyword_pattern:
            for pattern in keys:
                if words[0] == "REM": # if comment
                    for i in range(len(text)):
                        self.setFormat(i, len(text), QColor(self.colors[0][0], self.colors[0][1], self.colors[0][2]))
                else:
                    expression = QRegExp(f"\\b{pattern}\\b")
                    self.keyword_format = QTextCharFormat()
                    self.keyword_format.setForeground(QColor(self.colors[fi][0], self.colors[fi][1],
                                                             self.colors[fi][2]))
                    self.keyword_format.setFontWeight(QFont.Bold)
                    wordi = 0 # index of words
                    for t in words:
                        if t in DUCKYSCRIPT_STARTING_KEYWORDS and t == pattern and t == words[0] and wordi==0: # if it is a starting keyword, then only color code first word 
                            index = expression.indexIn(t)
                            length = expression.matchedLength()
                            self.setFormat(index, length, self.keyword_format)
                        elif t == pattern: # if words contains the pattern no matter where t is located in the line
                            # if first word of line is a starting keyword, don't color code it. E.g.: STRING (color code) HELLO (don't color code)
                            if not words[0] in DUCKYSCRIPT_STARTING_KEYWORDS and not t in DUCKYSCRIPT_STARTING_KEYWORDS:
                                index = expression.indexIn(t)+len(''.join(i for i in words[0:words.index(t)]))+len(words[0:words.index(t)])
                                while index >= 0:
                                    length = expression.matchedLength()
                                    self.setFormat(index, length, self.keyword_format)
                                    index = expression.indexIn(text, index + length)
                        else:
                            lengths = len(''.join(i for i in words[0:words.index(t)]))+len(words[0:words.index(t)])
                            num = QRegExp("\\b\\d+\\b")
                            indexn = num.indexIn(t)+lengths
                            while indexn >= 0:
                                length = num.matchedLength()
                                self.setFormat(indexn, length, self.num_format)
                                indexn = num.indexIn(text, indexn + length)
                        wordi += 1
            fi+=1

# Subclass QMainWindow to customize your application's main window
class IDE(QMainWindow, QWidget):
    """ Default Class Initializer """
    def __init__(self, screensize:QRect, app: QApplication): # size of physical screen
        super().__init__()
        # super(QWidget, self).__init__()

        # geometry of screensize
        self.left = screensize.left()
        self.top = screensize.top()
        self.width = screensize.width()
        self.height = screensize.height()
        self.left = self.left+self.width//3
        self.top = self.top+self.height//5
        self.width = self.width//2
        self.height = self.height//2
        self.screensize = screensize

        self.setGeometry(self.left, self.top, self.width, self.height)
        self.window_size = self.size()

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
                "load": [
                    "pictures/black_bk/load.png",
                    "load payload from existing file",
                    self.load_payload
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
                "load": [
                    "pictures/white_bk/load.png",
                    "load payload from existing file",
                    self.load_payload
                ],
                "upload": [
                    "pictures/white_bk/upload.png",
                    "upload file onto the hacking USB",
                    self.upload
                ]
        }

        self.view_black = [ # submenu
            "pictures/black_bk/view.png",
            "view",
        ]
        
        self.view_white = [ # submenu
            "pictures/white_bk/view.png",
            "view",
        ]

        self.exit_black = [
            "pictures/black_bk/exit.png",
            "exit"
        ]

        self.exit_white = [
            "pictures/white_bk/exit.png",
            "exit"
        ]

        self.setup_pic = [
            "pictures/setup.png",
            "setup"
        ]

        self.settings = Settings()
        self.settings.set_colors()
        self.rgb = hextorgb(self.settings.bg)

        # target device os and language
        self.target_os = "windows"
        self.target_lang = "us"

        if sys.platform == "darwin":
            self.download_dir = f'/Users/{os.getlogin()}/Downloads/'
        elif sys.platform == "linux":
            self.download_dir = f"/home/{os.getlogin()}/Downloads/"
        else:
            self.download_dir = f'C:/Users/{os.getlogin()}/Downloads/'

        # Operating System Selector
        self.select_os = QComboBox()
        for OS in SUPPORTED_OSS: # Supported Operating Systems
            self.select_os.addItem(OS)
        self.select_os.currentIndexChanged.connect(self.selected_os)

        # Language Selector
        self.keyboard_languages = language.LANGUAGES_WIN[:]
        self.languages = QComboBox()
        for lang in self.keyboard_languages:
            self.languages.addItem(lang)
        self.select_os.setToolTip("select target device OS")
        self.languages.setToolTip("select target device Keyboard Language")
        self.languages.currentIndexChanged.connect(self.selected_lang)

        self.set_theme()

        self.app = app
        pallete = QPalette()
        pallete.setColor(QPalette.Window, QColor(self.rgb[0], self.rgb[1], self.rgb[2]))
        self.setPalette(pallete)
        self.setWindowTitle("DuckScript IDE - USB Pico Ducky")
        self.setWindowIcon(QIcon("pictures/logo.png"))
        self.app.setApplicationName("Duckyscript IDE")
        main_menu = self.menuBar()

        toolbar = QToolBar("Editor toolbar")
        toolbar.setIconSize(QSize(22,22))
        self.addToolBar(toolbar)

        for action, lst in self.pngs.items():
            button_action = QAction(QIcon(lst[0]), action, self)
            button_action.setStatusTip(lst[1])
            button_action.triggered.connect(lst[2]) # lst[2] is the method added in the previous step

            # add buttons to toolbar
            toolbar.addAction(button_action)

        # add the view submenu
        view_menu = main_menu.addMenu(QIcon(self.view_theme[0]), 'View')
        copy_act = QAction('&Copy', self)
        paste_act = QAction('&Paste', self)
        cut_act = QAction('&Cut', self)
        quit_act = QAction('&Quit', self)
        self.theme_menu = view_menu.addMenu(QIcon("pictures/theme.png"), 'Theme')

        edit_menu = main_menu.addMenu(QIcon(self.view_theme[0]), 'Edit')
        save_act = QAction('&Save', self)
        load_act = QAction('&Load', self)
        delete_act = QAction('&delete file', self)
        
        copy_act.setShortcut("Ctrl+C")
        paste_act.setShortcut("Ctrl+V")
        cut_act.setShortcut("Ctrl+X")
        quit_act.setShortcut("CTRL+Q")
        save_act.setShortcut("CTRL+S")
        
        copy_act.triggered.connect(self.copier)
        paste_act.triggered.connect(self.paster)
        cut_act.triggered.connect(self.cutter)
        quit_act.triggered.connect(self.quitter)
        save_act.triggered.connect(self.save)
        load_act.triggered.connect(self.load_payload)
        delete_act.triggered.connect(self.delete_payload)

        view_menu.addAction(copy_act)
        view_menu.addAction(paste_act)
        view_menu.addAction(cut_act)
        view_menu.addAction(quit_act)
        view_menu.addAction(save_act)

        edit_menu.addAction(save_act)
        edit_menu.addAction(load_act)
        edit_menu.addAction(delete_act)
        
        # theme shortcuts
        themeb_act = QAction("&Black", self)
        themew_act = QAction("&White", self)
        theme_act = QAction("&Custom", self)
        themeb_act.setShortcut("CTRL+SHIFT+B")
        themew_act.setShortcut("CTRL+SHIFT+W")
        theme_act.setShortcut("CTRL+SHIFT+T")
        themeb_act.triggered.connect(self.black_theme)
        themew_act.triggered.connect(self.white_theme)
        theme_act.triggered.connect(self.custom_theme)
        self.theme_menu.addAction(themeb_act)
        self.theme_menu.addAction(themew_act)
        self.theme_menu.addAction(theme_act)

        # add codespace to write code
        self.wg = QWidget(self)
        self.codespace = QTextEdit(self.wg)
        self.codespace.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.codespace.move(self.adjw(6), self.adjh(10)-self.adjh(200))
        self.wg.move(self.adjw(6), self.adjh(10)-self.adjh(200))
        self.codespace.textChanged.connect(self.__line_widget_line_count_changed)
        self.line = LineNumberWidget(self.codespace)
        code_palette = self.codespace.palette()
        code_palette.setColor(QPalette.Text, QColor(self.colors[-4][0], self.colors[-4][1], self.colors[-4][2]))
        self.codespace.setPalette(code_palette)
        self.codespace.setStyleSheet(f"background-color: #{self.settings.textbubble};color: #{self.settings.text};")
        self.codespace.textChanged.connect(self.if_typed)
        self.change_count = 0 # amount of changes made

        # initialize files
        self.current_payload = self.settings.settings['current file']
        self.pico_path = self.settings.settings["last pico path"]
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.saved = True # wheter the file user is editing is saved
        self.historySaveLimit = 5 # Ask user how many files of history do they want saved

        # load the last payload from payloads, if it doesn't exist, try the previous one

        try:
            with open(self.path + "/payloads/" + self.current_payload) as f:
                self.codespace.setText(f.read())
                self.change_count = 0
        except FileNotFoundError as e: # if current payload doesn't exist
            all_payloads = os.listdir(self.path+"/payloads")
            all_payloads.remove('history')
            all_payloads = sorted(all_payloads, reverse=True)
            for payload in all_payloads:
                try:
                    with open(self.path + "/payloads/" + payload) as f:
                        self.codespace.setText(f.read())
                        self.change_count = 0
                except FileNotFoundError as e:
                    if payload != all_payloads[-1]: # if iteration is done
                        print(f"error: Payload not found, please create {self.current_payload} or load existing payload\nFileNotFoundError: {e}")
                else:
                    self.current_payload = payload

                    # save the current payload preference to settings
                    tmp_settings = Settings()
                    tmp_settings.settings["current file"] = self.current_payload
                    self.settings.settings["current file"] = self.current_payload # set it to current settings as well
                    with open("settings.json", "w") as f:
                        json.dump(tmp_settings.settings, f, indent=4)
                    del tmp_settings
                    break

        # set layout
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.line)
        self.layout.addWidget(self.codespace)
        self.wg.setLayout(self.layout)
        
        # color code
        self.parse_line()

        # Create a dock widget                                                                                
        self.layout = QHBoxLayout()
        dock = QDockWidget("Sidebar", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setFeatures(QDockWidget.DockWidgetClosable|QDockWidget.DockWidgetFloatable|QDockWidget.DockWidgetMovable)
        dock.setMaximumWidth(200)
        dock.setMinimumWidth(50)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        #creating the main widget
        widget = QWidget(self)
        self.setCentralWidget(widget)
        
        #creating the file selector
        self.file_selector = QFileSystemModel()
        self.tree = QTreeView(widget)
        self.tree.setModel(self.file_selector)
        self.tree.setRootIndex(self.file_selector.setRootPath(self.path+"/payloads/"))
        self.file_selector.setFilter(QDir.NoDotAndDotDot | QDir.Files) # hide folder
        self.tree.setHeaderHidden(True)
        self.tree.setSortingEnabled(True)
        self.tree.setColumnHidden(1,True) # hide other data
        self.tree.setColumnHidden(2,True)
        self.tree.setColumnHidden(3,True)
        self.tree.setFixedWidth(self.width//6)
        self.tree.setFixedHeight(self.height)
        self.tree.setStyleSheet(f"background-color: #{self.settings.bg_sidebar};color: #{self.settings.color_sidebar}")
        self.file_selector.setNameFilters(["*.dd"])
        self.selection = self.tree.selectionModel()
        self.tree.doubleClicked.connect(self.file_picked)

        # Set the widget as the content of the dock widget
        dock.setWidget(widget)

        # add all themes to toolbar
        to_load = self.settings.all_themes[:]
        to_load.remove("black") # these 2 themes are exclusively added
        to_load.remove("white") 
        for i in to_load:
            self.iter_theme = i
            act = QAction(i, self)
            act.triggered.connect(self.load_theme)
            self.theme_menu.addAction(act)

        # add setup button to toolbar
        self.setup = QAction(QIcon(self.setup_pic[0]), self.setup_pic[1], self)
        self.setup.triggered.connect(self.setup_w)
        self.setup.setToolTip("Setup USB Pico Ducky")

        # add target info selector to toolbar
        toolbar.addWidget(self.select_os)
        toolbar.addWidget(self.languages)
        toolbar.addAction(self.setup)


        # Create a "Screenshot" action with a shortcut
        screenshot_action = QAction("Screenshot", self)
        screenshot_action.setShortcut("print")
        screenshot_action.triggered.connect(self.take_screenshot)

        # Add the action to the File menu
        view_menu.addAction(screenshot_action)

    def take_screenshot(self):
        # Get the main window's geometry and take a screenshot
        main_window_rect = self.geometry()
        screenshot = QApplication.primaryScreen().grabWindow(QApplication.desktop().winId(),
                                                             main_window_rect.left(),
                                                             main_window_rect.top(),
                                                             main_window_rect.width(),
                                                             main_window_rect.height())
        pixmap = QPixmap(screenshot)
        painter = QPainter(pixmap)
        painter.fillRect(pixmap.rect(), QColor(0, 0, 0, 100))
        painter.end()
        buffer = QBuffer()
        buffer.open(QBuffer.ReadWrite)
        pixmap.save(buffer, "PNG")
        screenshot_data = buffer.data()
        num = 0
        if os.path.exists(self.download_dir+"/ducky_screenshot.png"):
            while True:
                if not os.path.exists(self.download_dir+f"/ducky_screenshot{num}.png"):
                    break
                num+=1
            with open(f"{self.download_dir}/ducky_screenshot{num}.png", "wb") as f:
                 f.write(screenshot_data)
        else:
            with open(f"{self.download_dir}/ducky_screenshot.png", "wb") as f:
                f.write(screenshot_data)

        message_box = QMessageBox(QMessageBox.Information,
                                  "Screenshot",
                                  "Screenshot taken",
                                  QMessageBox.Ok)

        message_box.exec_()
        
    # setup window
    def setup_w(self) -> None:
        self.setup_window = setup.Setup(screensize=self.screensize, parent=self)
        self.setup_window.show()

    # if os selected
    def selected_os(self, index):
        self.target_os = self.select_os.itemText(index)
        self.settings.target_os = self.target_os
        self.settings.settings["last os"] = self.target_os
        if self.target_os == "mac":
            self.keyboard_languages = language.LANGUAGES_MAC[:]
        elif self.target_os == "windows":
            self.keyboard_languages = language.LANGUAGES_WIN[:]

        # reset languages and put the ones for the newly chosen OS
        self.languages.blockSignals(True)
        self.languages.clear()
        for lang in self.keyboard_languages:
            self.languages.addItem(lang)
        self.languages.blockSignals(False)
        self.selected_lang(self.languages.findText(self.target_lang))

    # if language is selected
    def selected_lang(self, index):
        tmp_item = self.languages.itemText(index)
        try:
            # check if pico ducky
            # save initial folder location based on OS
            if sys.platform == "darwin":
                initial_folder = "/volumes/"
            elif sys.platform == "linux":
                initial_folder = "/media/"
            else:
                initial_folder = "C:This PC/Computer/"

            if os.path.exists("{self.pico_path}/duckyinpython.py"): # if pico ducky selected
                open(f"{self.pico_path}/choices", "x")
            else:
                raise CatchedError

            with open(f"{self.pico_path}/choices", "w") as f:
                f.write(f"{self.target_os}|{self.target_lang}")

            self.settings.settings["last pico path"] = self.pico_path
        except CatchedError: # not ducky
            message_box = QMessageBox(QMessageBox.Information,
                                      "Target Info Selector",
                                      "The USB Pico Ducky is not found, make sure the device is plugged in and the path is correct",
                                      QMessageBox.Ok)

            message_box.exec_()
            self.languages.blockSignals(True)
            self.languages.setCurrentText(self.target_lang)
            self.select_os.setCurrentText(self.target_os)
            self.languages.blockSignals(False)
            self.pico_path = QFileDialog.getExistingDirectory(self, 'Select USB Pico Ducky Folder', initial_folder)
            if os.path.exists("{self.pico_path}/duckyinpython.py"): # if pico ducky selected
                with open(f"{self.pico_path}/choices", "w") as f:
                    f.write(f"{self.target_os}|{self.target_lang}")
        else:
            # save the new configuration

            # save the last pico path immediately
            tmp_settings = Settings()
            tmp_settings.settings["last pico path"] = self.pico_path
            self.settings.settings["last pico path"] = self.pico_path
            with open("settings.json", "w") as f:
                json.dump(tmp_settings.settings, f, indent=4)
            del tmp_settings

            self.target_lang = tmp_item
            self.settings.target_language = self.target_lang
            self.settings.settings["last language"] = self.target_lang

    def __line_widget_line_count_changed(self):
        if self.line:
            n = int(self.codespace.document().lineCount())
            self.line.changeLineCount(n)
   
    def resizeEvent(self, event):
        size = self.size()
        w = size.width()
        h = size.height()
        self.codespace.resize(w-self.window_size.width()//6, h-self.window_size.height()//10)
        self.wg.resize(w-self.window_size.width()//6, h-self.window_size.height()//10)

        self.setStatusBar(QStatusBar(self))

    def parse_line(self):
        cursor = self.codespace.textCursor()
        
        # colorcoding
        tmp = (DUCKYSCRIPT_COMMENT, DUCKYSCRIPT_STARTING_KEYWORDS, DUCKYSCRIPT_SHORTCUT_KEYS, DUCKYSCRIPT_F_KEYS, DUCKYSCRIPT_ARROWS,
               DUCKYSCRIPT_WINDOWS, DUCKYSCRIPT_CHARS, DUCKYSCRIPT_UNCOMMON)
        string = self.codespace.toPlainText()
        line = string.split("\n")[cursor.blockNumber()]
        cursor = self.codespace.textCursor()
        block = SyntaxHighlighter(self.codespace, tmp, self.colors,
                                  QColor(self.colors[-5][0], self.colors[-5][1], self.colors[-5][2]),
                                  QColor(self.colors[-6][0], self.colors[-6][1], self.colors[-6][2]))
        block.highlightBlock(line)
        del tmp

    # file picked in sidebar
    def file_picked(self, selected):
        indexes = self.selection.selectedIndexes()
        if indexes:
            index = indexes[0]
            file = self.file_selector.filePath(index)
            if self.current_payload != file.split('/')[-1]: # if not the currently editing file
                if not self.saved:
                    msg = QMessageBox.question(None, 'Exit',
                                               "Are you sure you want to load another payload without saving the current edited file?",
                                               QMessageBox.No|QMessageBox.Save|QMessageBox.Yes)
                    if msg == QMessageBox.Save:
                        self.save()
                    if msg != QMessageBox.No:
                        with open(file, "r") as f:
                            self.codespace.setText(f.read())
                            self.change_count = 0
                            self.saved = True # True because newly loaded saved file
                            self.current_payload = file.split('/')[-1]
                else:
                    with open(file, "r") as f:
                        self.codespace.setText(f.read())
                        self.change_count = 0
                        self.saved = True # True because newly loaded saved file
                        self.current_payload = file.split('/')[-1]

    # load payload from any directory, the default directory is payloads
    def load_payload(self):
        try:
            file = QFileDialog.getOpenFileNames(self, "Select Files", f"{self.path}/payloads/", "All Files (*.dd)", "", QFileDialog.DontUseNativeDialog)[0][0]
        except IndexError:
            pass
        else:
            if os.path.dirname(file) != self.path+"/payloads": # if path is different, copy it to the path
                payloads_count = len(os.listdir(self.path+"/payloads"))-1
                if payloads_count == 0:
                    self.current_payload = "payload.dd"
                else:
                    self.current_payload = f"payload{payloads_count}.dd"
                shutil.copy(f'{file}', f'payloads/{self.current_payload}') # copy file to Downloads folder
                QMessageBox(QMessageBox.Information,
                            "Sucessfully Copied file",
                            f"{file} is saved as {self.current_payload}",
                            QMessageBox.Ok).exec_()
            else:
                self.current_payload = file.split('/')[-1] # seperate path from filename

            # load the payload into codespace
            try:
                with open(self.path + "/payloads/" + self.current_payload, "r") as f:
                    self.codespace.setText(f.read())
                    self.change_count = 0
                    self.saved = True
            except FileNotFoundError:
                QMessageBox(QMessageBox.Information,
                            "Payload Loader",
                            f"payload not found",
                            QMessageBox.Ok).exec_()
                print("payload not found")

    # delete the selected payload
    def delete_payload(self):
        options = QFileDialog.Options() # file selector options
        options |= QFileDialog.DontUseNativeDialog
        try:
            selected_files = QFileDialog.getOpenFileNames(self, "Select Files", f"{self.path}/payloads/", "All Files (*.dd)", "", options)[0] # file selector
            file = selected_files[0]
        except IndexError: # if canceled
            pass
        else:
            if os.path.dirname(file) == self.path+"/payloads": # if path of the file is payloads
                verify = QMessageBox.question(None, 'Delete file(s)', f"Are you sure you want to delete the file(s) selected?, you might not be able to recover it.", QMessageBox.No|QMessageBox.Yes)
                if verify == QMessageBox.Yes:
                    for file in selected_files:
                        files = os.listdir(self.path+"/payloads")
                        files.remove("history")
                        payloads_count = len(files) # subtract one because of history folder
                        tmp = file.split('/')[-1][:-3].split("payload")[1]
                        if tmp.isdigit(): # if not payload.dd, there would be a number, if so, then try to move all payload#.dd files 1 number below
                            found = int(tmp)
                            if found == payloads_count-1: # if file # number is the largest, delete the file and select the previous one 
                                send2trash.send2trash(file) # remove file and don't change anything else
                            else:
                                send2trash.send2trash(file)
                                open(file, "x").close()
                                # move file names to one previous one if they are bigger than file number (e.g. if file 2 deleted, file 3 becomes 2 and so on)
                                for i in range(found+1, payloads_count):
                                    payload = f"{self.path}/payloads/payload{i}.dd"
                                    if i-1 == 0:
                                        newpayload = f"{self.path}/payloads/payload.dd"
                                    else:
                                        newpayload = f"{self.path}/payloads/payload{i-1}.dd"
                                    if payload == self.current_payload: # change current payload if payload is updated
                                        self.current_payload = newpayload
                                    os.rename(payload, newpayload)
                        else: # if payload.dd
                            if payloads_count == 1: # if no other files
                                message_box = QMessageBox(QMessageBox.Information,
                                                          "Delete file",
                                                          f"There are no other files other than {file.split('/')[-1]}, therefore you cannot delete it",
                                                          QMessageBox.Ok)
                                message_box.exec_()
                            else:
                                send2trash.send2trash(file)

                                # update codespace
                                if not self.saved or self.change_count == 0: # save if not saved
                                    self.save()
                                with open(self.path + "/payloads/" + self.current_payload, "r") as f:
                                    self.codespace.setText(f.read())
                                    self.change_count = 0

                                # move file names to one previous one (e.g. payload1.dd becomes payload.dd)
                                for i in range(1, len(files)):
                                    payload = f"{self.path}/payloads/payload{i}.dd"
                                    if i-1 == 0:
                                        newpayload = f"{self.path}/payloads/payload.dd"
                                    else:
                                        newpayload = f"{self.path}/payloads/payload{i-1}.dd"
                                    os.rename(payload, newpayload)
                            
                    if not os.path.exists(self.current_payload): # if file doesn't exist
                        if payloads_count == 0:
                            self.current_payload = "payload.dd"
                        else:
                            self.current_payload = f"payload{payloads_count}.dd"
                    
                    tmp_settings = Settings()
                    tmp_settings.settings["current file"] = self.current_payload
                    self.settings.settings["current file"] = self.current_payload # set it to current settings as well
                    with open("settings.json", "w") as f:
                        json.dump(tmp_settings.settings, f, indent=4)
                    del tmp_settings

            else:
                message_box = QMessageBox(QMessageBox.Information,
                                          "Delete file",
                                          f"The file you picked isn't in payloads, please pick a file in payloads to delete it",
                                          QMessageBox.Ok)
                message_box.exec_()

    def if_typed(self):
        if self.codespace.document().isModified(): # only if plaintext of codespace is modified
            if self.change_count != 0:
                self.saved = False
            self.change_count+=1

    # adjust an integer to the height of the application
    def adjh(self, num:int) -> int:
        return self.size().height()//num
    
    # adjust an integer to the width of the application
    def adjw(self, num:int) -> int:
        return self.size().width()//num

    def compile_duckyscript(self):
        pass

    def set_theme(self):
        average = 0
        for i in self.rgb:
            average += i
        average//=3
        color_is_dark = True if average <= 128 else False
        if color_is_dark:
            self.pngs = self.black_bk_pngs
            self.view_theme = self.view_black
            self.exit_png = self.exit_black

            self.select_os.setStyleSheet(f"""
                QComboBox {{
                    padding: 1px 15px 1px 3px;
                }}

                QComboBox:!editable, QComboBox::drop-down:editable {{
                     background: #{self.settings.bg_sidebar};
                     color: #{self.settings.color_sidebar};
                }}

                QComboBox:!editable:on, QComboBox::drop-down:editable:on {{
                     background: #555555;
                     color: #ffffff;
                }}

                QComboBox:focus, QComboBox:focus QListView  {{
                     background: #07035C;
                     color: #ffffff;
                }}
            """)

            self.languages.setStyleSheet(f"""
                QComboBox {{
                    padding: 1px 15px 1px 3px;
                }}

                QComboBox:!editable, QComboBox::drop-down:editable {{
                     background: #{self.settings.bg_sidebar};
                     color: #{self.settings.color_sidebar};
                }}

                QComboBox:!editable:on, QComboBox::drop-down:editable:on {{
                     background: #555555;
                     color: #ffffff;
                }}

                QComboBox:focus, QComboBox:focus QListView  {{
                     background: #07035C;
                     color: #ffffff;
                }}
            """)

        else:
            self.pngs = self.white_bk_pngs
            self.view_theme = self.view_white
            self.exit_png = self.exit_white
            self.select_os.setStyleSheet("")
            self.languages.setStyleSheet("")

        self.colors = [self.settings.comment, self.settings.starting_keywords, self.settings.fkeys,
                       self.settings.shortcuts, self.settings.arrows, self.settings.windows,
                       self.settings.chars, self.settings.uncommon, self.settings.numbers,
                       self.settings.text, self.settings.textbubble, self.settings.bg,
                       self.settings.bg_sidebar, self.settings.color_sidebar] # 12 colors

        # convert all hex colors to rgb
        for i in range(len(self.colors)):
            self.colors[i] = hextorgb(self.colors[i])

    # CTRL+C
    def copier(self):
        clipboard = self.app.clipboard()
        selected_text = self.codespace.textCursor().selectedText()
        clipboard.setText(selected_text)

    # CTRL+V
    def paster(self):
        self.codespace.insertPlainText(self.app.clipboard().text())

    # CTRL+X
    def cutter(self):
        # copy
        self.codespace.cut()

    # CTRL+Q
    def quitter(self):
        if not self.saved or self.change_count != 0:
            __exit = QMessageBox.question(None, 'Quit', "Are you sure you want to exit without saving?", QMessageBox.No|QMessageBox.Save|QMessageBox.Yes)
            if __exit == QMessageBox.Yes:
                sys.exit(0)
            elif __exit == QMessageBox.Save:
                self.save()
                sys.exit(0)
        else:
            sys.exit(0)

    # load themes
    def load_theme(self):
        self.settings.set_theme(self.iter_theme)
        self.rgb = hextorgb(self.settings.bg)
        pallete = QPalette()
        pallete.setColor(QPalette.Window, QColor(self.rgb[0], self.rgb[1], self.rgb[2]))
        self.setPalette(pallete)
        self.codespace.setStyleSheet(f"background-color: #{self.settings.textbubble};color: #{self.settings.text}")
        self.tree.setStyleSheet(f"background-color: #{self.settings.bg_sidebar};color: #{self.settings.color_sidebar}") # filebar color
        self.set_theme()
        self.parse_line()
        code_palette = self.codespace.palette()
        code_palette.setColor(QPalette.Text, QColor(self.colors[-4][0], self.colors[-4][1], self.colors[-4][2]))
        self.codespace.setPalette(code_palette)

    # set black theme
    def black_theme(self):
        self.settings.set_theme("black")
        self.rgb = hextorgb(self.settings.bg)
        pallete = QPalette()
        pallete.setColor(QPalette.Window, QColor(self.rgb[0], self.rgb[1], self.rgb[2]))
        self.setPalette(pallete)
        self.codespace.setStyleSheet(f"background-color: #{self.settings.textbubble};color: #{self.settings.text}")
        self.tree.setStyleSheet(f"background-color: #{self.settings.bg_sidebar};color: #{self.settings.color_sidebar}") # filebar color
        self.set_theme()
        self.parse_line()
        code_palette = self.codespace.palette()
        code_palette.setColor(QPalette.Text, QColor(self.colors[-4][0], self.colors[-4][1], self.colors[-4][2]))
        self.codespace.setPalette(code_palette)

    # set white theme
    def white_theme(self):
        self.settings.set_theme("white")
        self.rgb = hextorgb(self.settings.bg) # background color
        pallete = QPalette()
        pallete.setColor(QPalette.Window, QColor(self.rgb[0], self.rgb[1], self.rgb[2])) # background color
        self.setPalette(pallete)
        self.codespace.setStyleSheet(f"background-color: #{self.settings.textbubble};color: #{self.settings.text}")
        self.tree.setStyleSheet(f"background-color: #{self.settings.bg_sidebar};color: #{self.settings.color_sidebar}") # filebar color
        self.set_theme() # sets the icons and text color
        self.parse_line()
        code_palette = self.codespace.palette()
        code_palette.setColor(QPalette.Text, QColor(self.colors[-4][0], self.colors[-4][1], self.colors[-4][2])) # textbubble color
        self.codespace.setPalette(code_palette)

        self.select_os.setStyleSheet("")
        self.languages.setStyleSheet("")

    # set custom theme for background, and text
    def custom_theme(self) -> None:
        # colors to modify: self.rgb, self.colors, codespace background color, codespace pallet for text
        names =  ('comment', 'starting keywords', 'F-keys', "shortcut keys", "arrows", "windows", "chars",
                  "uncommon", "numbers", "text", "textbubble", "background", "background filebar", "filebar text")
        colors = list(self.colors)
        self.color = ColorWindow(colors, names, self.rgb, self.settings, self.screensize, self)
        self.color.color_set()
        self.color.show()

    def closeEvent(self, event) -> None:
        if not self.saved or self.change_count != 0: # warn user if not saved
            __exit = QMessageBox.question(None, 'Quit', "Are you sure you want to exit without saving?", QMessageBox.No|QMessageBox.Save|QMessageBox.Yes)
            if __exit == QMessageBox.Yes:
                with open("settings.json", "w") as f:
                    self.settings.settings['current file'] = self.current_payload
                    json.dump(self.settings.settings, f, indent=4)
                event.accept()
            elif __exit == QMessageBox.Save:
                self.save()
                with open("settings.json", "w") as f:
                    self.settings.settings['current file'] = self.current_payload
                    json.dump(self.settings.settings, f, indent=4)
                event.accept()
            else:
                event.ignore()
        else:
            with open("settings.json", "w") as f:
                self.settings.settings['current file'] = self.current_payload
                json.dump(self.settings.settings, f, indent=4)
            event.accept()

    # add another duckyscript file
    # https://github.com/dbisu/pico-ducky#multiple-payloads
    def add_file(self):
        payloads_count = len(os.listdir(self.path+"/payloads"))-1
        if payloads_count == 0:
            payload = "payload.dd"
        else:
            payload = f"payload{payloads_count}.dd"
        try:
            open(self.path+"/payloads/"+payload, "x").close() # if order of payload# is incremental
        except FileExistsError: # e.g. if payload3.dd exists but payload2.dd doesn't
            try:
                open(self.path+"/payloads/payload.dd", "x").close() # if order of payload# is incremental
            except FileExistsError:
                for i in range(1, payloads_count):
                    try:
                        open(self.path+f"/payloads/payload{i}.dd", "x").close() # if order of payload# is incremental
                    except FileExistsError:
                        pass
            

    # locally download payload(#).dd
    def download_file(self):
        download_path = os.path.expanduser("~") + "/Downloads"
        shutil.copy(f'payloads/{self.current_payload}', f'{download_path}/') # copy file to Downloads folder


    # save the currently editing file
    def save(self):
        if not self.saved:
            try:
                payloads = self.path+"/payloads"
                if len(os.listdir(payloads)) > 1: # if there are payloads, save history of the last 10 files
                    payload_history = [f for f in os.listdir(payloads+"/history") if os.path.isfile(f) and f.startswith(self.current_payload[:-3])]
                    count = len(payload_history)
                    if count <= self.historySaveLimit:
                        shutil.copy(f'{payloads}/{self.current_payload}', f'{payloads}/history/{self.current_payload[:-3]}_{count}.dd') # copy unedited file to history
                with open(f"{payloads}/{self.current_payload}","w") as f:
                    text = self.codespace.toPlainText()
                    f.write(text)
                self.saved = True
                self.change_count = 0
                message_box = QMessageBox(QMessageBox.Information,
                                          "Save",
                                          "Sucessfully saved",
                                          QMessageBox.Ok)
                message_box.exec_()
            except FileNotFoundError: # try to add a backslash and try again
                try:
                    self.path += "/"
                    payloads = self.path+"payloads"
                    if len(os.listdir(payloads) > 1): # if there are no payloads
                        payload_history = [f for f in os.listdir(payloads+"/history") if os.path.isfile(f) and f.startswith(self.current_payload[:-3])]
                        count = len(payload_history)
                        if count <= self.historySaveLimit:
                            shutil.copy(f'{payloads}/{self.current_payload}', f'{payloads}/history/{self.current_payload[:-3]}_{count}.dd') # copy unedited file to history
                    with open(f"{payloads}/{self.current_payload}","w") as f:
                        text = self.codespace.toPlainText()
                        f.write(text)
                    self.saved = True
                    self.change_count = 0
                    message_box = QMessageBox(QMessageBox.Information,
                                              "Save",
                                              "Sucessfully saved",
                                              QMessageBox.Ok)
                    message_box.exec_()
                except FileNotFoundError: # try to add a frontslash and try again
                    try:
                        self.path += "\\"
                        if len(os.listdir(self.path+"payloads")) > 1: # if there are no payloads
                            payload_history = [f for f in os.listdir(payloads+"/history") if os.path.isfile(f) and f.startswith(self.current_payload[:-3])]
                            count = len(payload_history)
                            if count <= self.historySaveLimit:
                                shutil.copy(f'{payloads}/{self.current_payload}', f'{payloads}/history/{self.current_payload[:-3]}_{count}.dd') # copy unedited file to history
                        with open(f"{payloads}/{self.current_payload}","w") as f:
                            text = self.codespace.toPlainText()
                            f.write(text)
                            message_box = QMessageBox(QMessageBox.Information,
                                                      "Save",
                                                      "Sucessfully saved",
                                                      QMessageBox.Ok)
                        self.saved = True
                        self.change_count = 0
                        message_box.exec_()
                    except FileNotFoundError:
                        message_box = QMessageBox(QMessageBox.Information,
                                                  "FileNotFoundError",
                                                  "File Not Found, please input the correct path to the usb-app",
                                                  QMessageBox.Cancel)
                        message_box.exec_()

    # upload payload(#).dd onto the microcontroller
    def upload(self):
        message_box = QMessageBox(QMessageBox.Information,
                                  "Payload Upload",
                                  "Choose the Payload to Upload",
                                  QMessageBox.Ok)
        message_box.exec_()
        files = QFileDialog.getOpenFileNames(self, "Select Payload to Upload", f"{self.path}/payloads/", "All Files (*.dd)", "", QFileDialog.DontUseNativeDialog)[0]
        message_box = QMessageBox(QMessageBox.Information,
                                  "Payload Upload",
                                  "Please choose a filename, what should the name of the file be in the USB Pico Ducky, remember that if you have one file, use payload.dd, if you have two: (payload.dd, payload1.dd), otherwise, they won't work, please refer to the documentation for more information",
                                  QMessageBox.Ok)
        message_box.exec_()
        dialog = QInputDialog(self)
        palette = dialog.palette()

        if self.settings.theme[0] == 'w': # white border of box means dark background
            dialog.setStyleSheet("background: black; color: white;")
            dialog.setStyleSheet("QLineEdit { color: white; background-color: black; } QPushButton { background-color: #202020; color: white; }")
            palette.setColor(QPalette.Background, QColor(5, 5, 5))
        else:
            dialog.setStyleSheet("background: 5f5f5f;color: f5f5f5;")
            dialog.setStyleSheet("QLineEdit { color: black; background-color: white; }")
            palette.setColor(QPalette.Background, QColor(250,250,250))
        dialog.setLabelText(f"Enter New File Name, Don't enter anything if you don't want to change the names.\nIf you have multiple files, seperate them using a single space bar inbetween\ne.g. payload.dd payload1.dd...")
        dialog.setWindowTitle("Theme name Picker")
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.setPalette(palette)
        ok = dialog.exec_()
        new_files = dialog.textValue()
        if new_files == "":
            new_files = []
            for file in files:
                new_files.append(file.split('/')[-1])
        else:
            new_files = new_files.split(" ")
            if len(new_files) != files:
                for i in range(len(new_files), len(files)):
                    new_files.append(files[i].split('/')[-1])

        for i in range(len(files)):
            file = files[i]
            new_file = new_files[i]
            if os.path.exists(self.settings.pico_path):
                shutil.copy(file, self.settings.pico_path + f"/{new_file}")
            else:
                if sys.platform == "darwin":
                    self.pico_path = QFileDialog.getExistingDirectory(self, 'Select USB Pico Ducky Folder', "/volumes/")
                elif sys.platform == "linux":
                    self.pico_path = QFileDialog.getExistingDirectory(self, 'Select USB Pico Ducky Folder', "/media/")
                else:
                    self.pico_path = QFileDialog.getExistingDirectory(self, 'Select USB Pico Ducky Folder', "C:This PC/Computer/")
                try:
                    shutil.copy(file, self.settings.pico_path + f"/{new_file}")
                except (PermissionError, OSError):
                    message_box = QMessageBox(QMessageBox.Information,
                                              "Payload Upload",
                                              "Upload failed, Are you sure you selected the USB Pico Ducky?",
                                              QMessageBox.Cancel)
                    message_box.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = IDE(screensize=app.primaryScreen().availableGeometry(), app=app)

    window.show()
    sys.exit(app.exec_())
