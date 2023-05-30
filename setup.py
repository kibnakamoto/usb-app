"""
@Author: Taha Canturk
@Github: Kibnakamoto
Date: Apr 16, 2023
"""

import os
import sys
import shutil
import json
from time import sleep
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QPushButton, QMessageBox
from PyQt5.QtGui import QColor, QPalette

import settings

#TODO: possibly change the name of CIRCUITPY to self.settings.pico_path.split("/")[-1]

# Modes: disable/enable
# disable: press the button on the usb while plugging the usb in. After the USB shows up as a storage device. Execute the disable_h()
# enable: nothing

# Setup the Microcontoller for hacking (hacking usb) or default mode (Normal MicroController)
class Setup(QMainWindow):
    """ Default Class Initializer """
    def __init__(self, bg_rgb:tuple=(0x00,0x00,0x00), screensize=None, parent=None):
        super().__init__()
        self.setWindowTitle("Setup USB Pico Ducky")
        self.hack_mode = True
        self.path = os.path.dirname(os.path.realpath(__file__)) # get path of the application folder
        self.add_path = self.path + "/add_to_pico/"
        self.parent=parent # IDE

        self.screensize = screensize
        self.bg_rgb = bg_rgb

        # set background color
        pallete = QPalette()
        pallete.setColor(QPalette.Window, QColor(bg_rgb[0], bg_rgb[1], bg_rgb[2]))
        self.setPalette(pallete)

        self.pico_path = None

        self.select_path = QPushButton("Select USB Pico Ducky path", self)
        self.select_path.resize(self.select_path.sizeHint())
        self.select_path.move(self.screensize.width()//2-self.select_path.width()//2, self.screensize.height()//2)
        self.select_path.clicked.connect(self.path_selector)
        self.select_path.setToolTip("Select the path of USB Pico Ducky")

    # resize window if moved
    def resizeEvent(self, event):
        # resize theme_text
        size = self.size()
        self.select_path.move(size.width()//2-self.select_path.width()//2, size.height()//2)

        if hasattr(self, "selector_h"):
            self.selector_h.move(size.width()//2-self.select_path.width()//2, size.height()//2-self.select_path.height())

    def path_selector(self) -> None:
        if sys.platform == "darwin":
            self.pico_path = QFileDialog.getExistingDirectory(self, 'Select USB Pico Ducky Folder', "/volumes/")
        elif sys.platform == "linux":
            self.pico_path = QFileDialog.getExistingDirectory(self, 'Select USB Pico Ducky Folder', "/media/")
        else:
            self.pico_path = QFileDialog.getExistingDirectory(self, 'Select USB Pico Ducky Folder', "C:This PC/Computer/")

        if os.path.exists(self.pico_path+"/duckyinpython.py"): # if root/duckyinpython.py exists, then it's probably in hacking mode
            button_n = "Disable"
            self.hack_mode = True
        else:
            button_n = "Enable"
            self.hack_mode = False

        self.parent.pico_path = self.pico_path
        new_settings = settings.Settings()
        new_settings.settings["last pico path"] = self.pico_path
        with open("settings.json", "w") as f:
            json.dump(new_settings.settings, f, indent=4)

        # hack mode selector
        self.selector_h = QPushButton(f"Disable Hack Mode", self)
        self.selector_h.resize(self.selector_h.sizeHint())
        self.selector_h.move(self.size().width()//2-self.selector_h.width()//2, self.size().height()//2-self.select_path.height())
        self.selector_h.setToolTip(f"Disable the Hacking Mode of USB Pico Ducky")
        self.selector_h.show()
        self.selector_h.clicked.connect(self.disable_h)

        # hack mode selector
        self.selector_e = QPushButton(f"Enable Hack Mode", self)
        self.selector_e.resize(self.selector_e.sizeHint())
        self.selector_e.move(self.size().width()//2-self.selector_h.width()//2, self.size().height()//2-self.select_path.height()-self.selector_h.height())
        self.selector_e.setToolTip(f"Enable the Hacking Mode of USB Pico Ducky")
        self.selector_e.show()
        self.selector_e.clicked.connect(self.enable_h)

    # enable hacking mode
    def enable_h(self, hack_mode:bool=True) -> None:
        message_box = QMessageBox(QMessageBox.Information,
                                  "Enable Hack Mode",
                                  "Enabling Hacking Mode, this might take a minute",
                                  QMessageBox.Ok)
        message_box.exec_()
        # upload the files onto the microcontoller
        self.hack_mode = hack_mode

        # replace folder name in path
        if not os.path.exists(self.pico_path):
            self.pico_path = self.pico_path.replace(self.pico_path[self.pico_path.index(self.pico_path.split('/')[-1]):], "RPI-RP2")

        # copy the uf2.uf2 file to the microcontroller and wait for it to reboot
        try:
            shutil.copy(f"{self.add_path}/uf2.uf2", self.pico_path) # copy file to pico
        except PermissionError:
            message_box = QMessageBox(QMessageBox.Information,
                                      "Enable hack mode",
                                      "Device doesn't exist. Please make sure you selected the right device, if it still didn't work, try setting the device name to RPI-RP2",
                                      QMessageBox.Ok)
            message_box.exec_()
            

        possible_pico_names = ["CIRCUITPY", self.settings.pico_path.split("/")[-1]] # try both these names. Try one every iteration.
        self.pico_path = self.pico_path.replace(self.pico_path[self.pico_path.index(self.pico_path.split('/')[-1]):], "CIRCUITPY")
        index = -1
        while True:
            try:
                index+=1

                # add all the lib files
                lib_files = os.listdir(f"{self.add_path}lib")
                for file in lib_files:
                    if os.path.exists(self.pico_path + f"/{file}"):
                        os.remove(self.pico_path + f"/{file}")
                    elif os.path.exists(self.pico_path + f"/lib/{file}"):
                        os.remove(self.pico_path + f"/{file}")
                    try:
                        shutil.copy(f"{self.add_path}lib/{file}", self.pico_path+"/lib/") # copy file to pico
                    except IsADirectoryError: # IsADirectoryError: [Errno 21] Is a directory
                        if os.path.exists(self.pico_path + f"/{file}"):
                            shutil.rmtree(self.pico_path + f"/{file}")
                        elif os.path.exists(self.pico_path + f"/lib/{file}"):
                            shutil.rmtree(self.pico_path + f"/{file}")
                        shutil.copytree(f"{self.add_path}lib/{file}", self.pico_path+f"/lib/{file}") # copy file to pico

                # add all the root files
                root_files = os.listdir(f"{self.add_path}root")
                for file in root_files:
                    if os.path.exists(self.pico_path + f"/{file}"):
                        os.remove(self.pico_path + f"/{file}")
                    shutil.copy(f"{self.add_path}root/{file}", self.pico_path+f"/{file}") # copy file to pico
                break
            except PermissionError: # No permission meaning shutil didn't load
                if not os.path.exists(self.pico_path):
                    self.pico_path = self.pico_path.replace(self.pico_path[self.pico_path.index(self.pico_path.split('/')[-1]):], possible_pico_names[index%2])
                print("trying device", self.pico_path)
                sleep(1)
                continue
        new_settings = settings.Settings()
        new_settings.settings["last pico path"] = self.pico_path
        with open("settings.json", "w") as f:
            json.dump(new_settings.settings, f, indent=4)
        del new_settings
        message_box = QMessageBox(QMessageBox.Information,
                                  "Enable hack mode",
                                  "successfully enabled hacking mode",
                                  QMessageBox.Ok)
        message_box.exec_()

    # disable hacking mode
    def disable_h(self, hack_mode:bool=False) -> None:
        # remove the uploaded files from the microcontroller
        self.hack_mode = hack_mode
        if not os.path.exists(self.pico_path):
            self.pico_path = self.pico_path.replace(self.pico_path[self.pico_path.index(self.pico_path.split('/')[-1]):], "RPI-RP2")

        # while holding the button, plug the usb in and run this code
        try:
            shutil.copy(f"{self.add_path}/flash_nuke.uf2", self.pico_path) # copy uf2 nuke to pico
        except PermissionError:
            message_box = QMessageBox(QMessageBox.Information,
                                      "Disable Hack Mode",
                                      "Path isn't correct, please make sure to Hold the White Button (Labeled as Bootsel) while plugging the device in, then make sure the name of the microcontroller is set to RPI-RP2",
                                      QMessageBox.Ok)
            message_box.exec_()
        sleep(5)

        message_box = QMessageBox(QMessageBox.Information,
                    "Disable Hack Mode",
                    "Sucessfully Disabled Hacking USB",
                    QMessageBox.Ok)
        message_box.exec_()

if __name__ == '__main__':
    app = QApplication([])
    w = Setup(screensize=app.primaryScreen().availableGeometry())
    w.show()
    app.exec_()
