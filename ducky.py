# GUI and compiler of duckyscript on a raspberry pi pico (w)

import sys
import re
from PyQt5.QtCore import QSize, Qt, QRect, QRegExp, QTextStream, QFile
from PyQt5.QtWidgets import QMainWindow, QApplication, QToolBar, QAction, QStatusBar, QMenu, QTextEdit, \
                            QHBoxLayout, QSizePolicy, QWidget, QPlainTextEdit, QMessageBox, QColorDialog
from PyQt5.QtGui import QIcon, QColor, QTextFormat, QBrush, QTextCharFormat, QFont, QSyntaxHighlighter, \
                        QPalette, QTextCursor
from pyqt_line_number_widget import LineNumberWidget
import os
import shutil

import language

target_os = "" # windows or mac
keyboard_lang = "us" # target keyboard language, default is us

# Initialize Duckyscript keywords to color code the ones written to the textbox
DUCKYSCRIPT_COMMENT = ("REM")
DUCKYSCRIPT_STARTING_KEYWORDS = ("DELAY", "STRING", "PRINT", "IMPORT", "DEFAULT_DELAY", "DEFAULTDELAY", "LED")
DUCKYSCRIPT_F_KEYS = ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12")
DUCKYSCRIPT_SHORTCUT_KEYS = ("ALT", "CTRL", "CONTROL", "SHIFT", "SPACE", "ENTER", "BACKSPACE", "TAB",
                             "CAPSLOCK", "ESC", "ESCAPE")
DUCKYSCRIPT_ARROWS = ("UP", "UPARROW", "DOWN", "DOWNARROW", "LEFT", "LEFTARROW", "RIGHT", "RIGHTARROW")
DUCKYSCRIPT_WINDOWS = ("WINDOWS", "GUI")
DUCKYSCRIPT_CHARS = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q",
                     "R", "S", "T", "U", "V", "W", "X", "Y", "Z")
DUCKYSCRIPT_UNCOMMON = ("APP", "MENU", "BREAK", "PAUSE", "DELETE", "END", "HOME", "INSERT", "NUMLOCK",
                        "PAGEUP", "PAGEDOWN", "PRINTSCREEN", "SCROLLLOCK")
ITEXT_COLORS_LIGHT = ((94,148,81), (220,11,11), (255,128,0), (0,204,204), (204,204,0), (0,0,204), (255,127,80), (46,199,199), (84,107,107), (32,32,32)) # 12 colors
ITEXT_COLORS_DARK = ((50,205,50), (255,0,0), (105,105,105), (210,105,30), (224,255,255), (62,62,236), (255,102,102), (133,193,187), (212,21,212), (250,250,250)) # 12 colors

# COLORS for (COMMENT, starting_keywords, fkeys, shortcut_keys, arrows, windows, chars, uncommon, numbers, text)

######## TODO: make a setup function that downloads add_to_pico/* into the microcontroller
######## TODO: add settings submenu for changing the colors of input text
######## TODO: make a toolbar item for loading from history and payloads
######## TODO: Make a side-toolbar for all payload files (not history)
######## TODO: Make a settings.json file for saving all preferences with theme for next time it's opened

class Setup(QMainWindow):
    def __init__(self):
        super().__init__()

# RGB to hex, accepts either one RGB tuple or r,g,b as seperate parameters
def rgbtohex(r:tuple, g:int=None,b:int=None) -> str:
    value = 0
    if isinstance(r, tuple):
        for i in r:
            value<<=8
            value|=i
    else:
        value<<=8
        value|=r
        value<<=8
        value|=g
        value<<=8
        value|=b
    return hex(value)[2:]

# Syntax Highlighter for Duckyscript
class SyntaxHighlighter(QSyntaxHighlighter):

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
                    wordi = 0
                    for t in words:
                        if t == pattern and t == words[0]:
                            index = expression.indexIn(t)
                            while index >= 0:
                                length = expression.matchedLength()
                                self.setFormat(index, length, self.keyword_format)
                                index = expression.indexIn(text, index + length)
                        else:
                            lengths = 0 # previous lengths
                            for i in range(wordi):
                                lengths += len(words[i])
                            num = QRegExp("\\b\\d+\\b")
                            indexn = num.indexIn(t)+lengths+1
                            if wordi == 0:
                                indexn -= 1
                            while indexn >= 0:
                                length = num.matchedLength()
                                self.setFormat(indexn, length, self.num_format)
                                indexn = num.indexIn(text, indexn + length)
                        wordi += 1
            fi+=1

# Subclass QMainWindow to customize your application's main window
class IDE(QMainWindow, QWidget):
    def __init__(self, screensize:QRect, app: QApplication): # size of physical screen
        super().__init__()
        super(QWidget, self).__init__()

        # geometry of screensize
        self.left = screensize.left()
        self.top = screensize.top()
        self.width = screensize.width()
        self.height = screensize.height()
        self.left = self.left+self.width//3
        self.top = self.top+self.height//5
        self.width = self.width//2
        self.height = self.height//2

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

        self.pngs = self.black_bk_pngs # default icons
        self.exit_png = self.exit_black
        self.view_theme = self.view_black
        self.rgb = (5,5,5) # black
        pallete = QPalette()
        pallete.setColor(QPalette.Window, QColor(self.rgb[0], self.rgb[1], self.rgb[2]))
        self.setPalette(pallete)
        self.colors = ITEXT_COLORS_DARK
        self.setWindowTitle("DuckScript IDE & Compiler")
        main_menu = self.menuBar()
        self.app = app

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
        theme_menu = view_menu.addMenu(QIcon("pictures/theme.png"), 'Theme')
        copy_act = QAction('&Copy', self)
        paste_act = QAction('&Paste', self)
        cut_act = QAction('&Cut', self)
        quit_act = QAction('&Quit', self)
        save_act = QAction('&Save', self)
        
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

        view_menu.addAction(copy_act)
        view_menu.addAction(paste_act)
        view_menu.addAction(cut_act)
        view_menu.addAction(quit_act)
        view_menu.addAction(save_act)

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
        theme_menu.addAction(themeb_act)
        theme_menu.addAction(themew_act)
        theme_menu.addAction(theme_act)

        # add codespace to write code
        self.wg = QWidget(self)
        self.codespace = QTextEdit(self.wg)
        self.codespace.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.codespace.move(self.adjw(6), self.adjh(10)-self.adjh(200))
        self.wg.move(self.adjw(6), self.adjh(10)-self.adjh(200))
        self.codespace.textChanged.connect(self.__line_widget_line_count_changed)
        self.line = LineNumberWidget(self.codespace)
        code_palette = self.codespace.palette()
        code_palette.setColor(QPalette.Text, QColor(self.colors[-1][0], self.colors[-1][1], self.colors[-1][2]))
        self.codespace.setPalette(code_palette)
        self.codespace.setStyleSheet("background-color: #000000;");
        self.codespace.textChanged.connect(self.ifTyped)

        # initialize files
        self.current_payload = "payload.dd"
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.saved = True # wheter the file user is editing is saved
        self.historySaveLimit = 5 # Ask user how many files of history do they want saved

        # load the last payload from payloads
        try:
            f = open(self.path + "/payloads/" + self.current_payload)
            # stream = QTextStream(QString(f.name))
            # raise Exception(stream.readAll())
            # self.codespace.setPlainText(stream.readAll())
        except FileNotFoundError:
            pass

        # set layout
        layout = QHBoxLayout()
        layout.addWidget(self.line)
        layout.addWidget(self.codespace)
        self.wg.setLayout(layout)
        
        self.parse_line()

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
                                  QColor(self.colors[-1][0], self.colors[-1][1], self.colors[-1][2]),
                                  QColor(self.colors[-2][0], self.colors[-2][1], self.colors[-2][2]))
        block.highlightBlock(line)
        del tmp

    def ifTyped(self):
        self.saved = False

    # adjust an integer to the height of the application
    def adjh(self, num:int) -> int:
        return self.size().height()//num
    
    # adjust an integer to the width of the application
    def adjw(self, num:int) -> int:
        return self.size().width()//num

    def compile_duckyscript(self):
        pass

    def set_theme(self):
        average = 0;
        for i in self.rgb:
            average += i
        average//=3
        color_is_dark = True if average <= 128 else False
        if color_is_dark:
            self.pngs = self.black_bk_pngs
            self.view_theme = self.view_black
            self.colors = ITEXT_COLORS_DARK
            self.exit_png = self.exit_black
        else:
            self.pngs = self.white_bk_pngs
            self.view_theme = self.view_white
            self.colors = ITEXT_COLORS_LIGHT
            self.exit_png = self.exit_white

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
        clipboard = self.app.clipboard()
        selected_text = self.codespace.textCursor().selectedText()
        clipboard.setText(selected_text)

        # delete selected text
        text_cursor = self.codespace.textCursor()
        text_cursor.select(QTextCursor.Document)
        text_cursor.removeSelectedText()

    # CTRL+Q
    def quitter(self):
        if not self.saved:
            __exit = QMessageBox.question(None, 'Quit', "Are you sure you want to exit without saving?", QMessageBox.No|QMessageBox.Save|QMessageBox.Yes)
            if __exit == QMessageBox.Yes:
                sys.exit(0)
            elif __exit == QMessageBox.Save:
                self.save()
        else:
            sys.exit(0)

    # set black theme
    def black_theme(self):
        self.rgb = (5,5,5)
        pallete = QPalette()
        pallete.setColor(QPalette.Window, QColor(self.rgb[0], self.rgb[1], self.rgb[2]))
        self.setPalette(pallete)
        self.codespace.setStyleSheet("background-color: #000000;");
        self.set_theme()
        self.parse_line()
        code_palette = self.codespace.palette()
        code_palette.setColor(QPalette.Text, QColor(self.colors[-1][0], self.colors[-1][1], self.colors[-1][2]))
        self.codespace.setPalette(code_palette)


    # set white theme
    def white_theme(self):
        self.rgb = (250,250,250)
        pallete = QPalette()
        pallete.setColor(QPalette.Window, QColor(self.rgb[0], self.rgb[1], self.rgb[2]))
        self.setPalette(pallete)
        self.codespace.setStyleSheet("background-color: #ffffff;");
        self.set_theme() # sets the icons and text color
        self.parse_line()
        code_palette = self.codespace.palette()
        code_palette.setColor(QPalette.Text, QColor(self.colors[-1][0], self.colors[-1][1], self.colors[-1][2]))
        self.codespace.setPalette(code_palette)

    # set custom theme for background, and text
    def custom_theme(self):
        # colors to modify: self.rgb, self.colors, codespace background color, codespace pallet for text
        color = QColorDialog.getColor()
        if color.isValid():
            print(color.name())

        self.set_theme() # sets icons and text color based on how dark the background is


    def closeEvent(self, event): ###### TODO: add QIcon to QMessageBox, soooo annoying. Not working. Pyton on Crack
        if not self.saved:
            __exit = QMessageBox.question(None, 'Quit', "Are you sure you want to exit without saving?", QMessageBox.No|QMessageBox.Save|QMessageBox.Yes)
            #__exit = QMessageBox()
            # QMessageBox.setIcon(__exit, QIcon(self.exit_png[0]))
            # __exit.setText('Quit')
            # __exit.setInformativeText("Are you sure you want to exit without saving?")
            # __exit.setStandardButtons(QMessageBox.No|QMessageBox.Save|QMessageBox.Yes)
            if __exit == QMessageBox.Yes:
                event.accept()
            elif __exit == QMessageBox.Save:
                self.save()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()



    # add another duckyscript file
    # https://github.com/dbisu/pico-ducky#multiple-payloads
    def add_file(self):
        pass

    # locally download payload(#).dd
    def download_file(self):
        pass

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
                f = open(f"{payloads}/{self.current_payload}","w")
                text = self.codespace.toPlainText()
                f.write(text)
                self.saved = True
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
                    f = open(f"{payloads}/{self.current_payload}","w")
                    text = self.codespace.toPlainText()
                    f.write(text)
                    self.saved = True
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
                        f = open(f"{payloads}/{self.current_payload}","w")
                        text = self.codespace.toPlainText()
                        f.write(text)
                        message_box = QMessageBox(QMessageBox.Information,
                                                  "Save",
                                                  "Sucessfully saved",
                                                  QMessageBox.Ok)
                        message_box.exec_()
                        self.saved = True
                    except FileNotFoundError:
                        message_box = QMessageBox(QMessageBox.Information,
                                                  "FileNotFoundError",
                                                  "File Not Found, please input the correct path to the usb-app",
                                                  QMessageBox.Cancel)
                        message_box.exec_()

    # upload payload(#).dd onto the microcontroller
    def upload(self):
        pass

app = QApplication(sys.argv)
window = IDE(screensize=app.primaryScreen().availableGeometry(), app=app)

window.show()
sys.exit(app.exec())
